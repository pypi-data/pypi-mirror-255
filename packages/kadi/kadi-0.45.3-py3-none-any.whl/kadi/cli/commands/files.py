# Copyright 2020 Karlsruhe Institute of Technology
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import os
import shutil
import sys

import click
from flask import current_app

import kadi.lib.constants as const
from kadi.cli.main import kadi
from kadi.cli.utils import check_env
from kadi.cli.utils import echo
from kadi.cli.utils import echo_danger
from kadi.cli.utils import echo_success
from kadi.cli.utils import echo_warning
from kadi.lib.exceptions import KadiFilesizeMismatchError
from kadi.lib.storage.core import get_storage
from kadi.lib.tasks.models import Task
from kadi.lib.tasks.models import TaskState
from kadi.modules.records.files import remove_file
from kadi.modules.records.models import File
from kadi.modules.records.models import FileState
from kadi.modules.records.models import Upload
from kadi.modules.records.models import UploadState
from kadi.modules.records.uploads import remove_upload


@kadi.group()
def files():
    """Utility commands for file management."""


def _remove_path(path):
    if os.path.isdir(path):
        shutil.rmtree(path)
    else:
        os.remove(path)


@files.command()
@click.option("--i-am-sure", is_flag=True)
@check_env
def clean(i_am_sure):
    """Remove all files in the configured local storage and upload paths.

    This command will delete all data stored in the local paths specified via the
    STORAGE_PATH and MISC_UPLOADS_PATH configuration values.

    Should only be run while the application and Celery are not running.
    """
    storage_path = current_app.config["STORAGE_PATH"]
    misc_uploads_path = current_app.config["MISC_UPLOADS_PATH"]

    if not i_am_sure:
        echo_warning(
            f"This will remove all data in '{storage_path}' and '{misc_uploads_path}'."
            " If you are sure you want to do this, use the flag --i-am-sure."
        )
        sys.exit(1)

    for item in os.listdir(storage_path):
        _remove_path(os.path.join(storage_path, item))

    for item in os.listdir(misc_uploads_path):
        _remove_path(os.path.join(misc_uploads_path, item))

    echo_success("Storage cleaned successfully.")


@files.command()
def check():
    """Check all files stored in the database for inconsistencies.

    Should only be run while the application and Celery are not running.
    """
    num_inconsistencies = 0
    inconsistent_items = []

    # Check all files.
    files_query = File.query.with_entities(
        File.id, File.size, File.storage_type, File.state
    )
    echo(f"Checking {files_query.count()} files in database...")

    for file in files_query.order_by(File.last_modified.desc()):
        storage = get_storage(file.storage_type)

        # For active files, we check if they exist and if at least their size matches.
        if file.state == FileState.ACTIVE:
            if storage.exists(str(file.id)):
                try:
                    actual_size = storage.get_size(str(file.id))
                    storage.validate_size(actual_size, file.size)

                except KadiFilesizeMismatchError:
                    num_inconsistencies += 1
                    inconsistent_items.append(File.query.get(file.id))

                    echo_danger(
                        f"[{num_inconsistencies}] Mismatched size for active file"
                        f" with storage type '{file.storage_type}' and ID '{file.id}'."
                    )
            else:
                num_inconsistencies += 1
                inconsistent_items.append(File.query.get(file.id))

                echo_danger(
                    f"[{num_inconsistencies}] Found orphaned active file with storage"
                    f" type '{file.storage_type}' and ID '{file.id}'."
                )

        # Inactive files will be handled by the periodic cleanup task eventually.
        elif file.state == FileState.INACTIVE:
            pass

        # Deleted file objects should not have any data associated with them anymore.
        elif file.state == FileState.DELETED and storage.exists(str(file.id)):
            num_inconsistencies += 1
            inconsistent_items.append(File.query.get(file.id))

            echo_danger(
                f"[{num_inconsistencies}] Found deleted file with associated data with"
                f" storage type '{file.storage_type}' and ID '{file.id}'."
            )

    # Check all uploads.
    uploads_query = Upload.query.with_entities(
        Upload.id, Upload.storage_type, Upload.state
    )
    echo(f"Checking {uploads_query.count()} uploads in database...")

    for upload in uploads_query.order_by(Upload.last_modified.desc()):
        # Active uploads will either be handled once they are finished or by the
        # periodic cleanup task eventually.
        if upload.state == UploadState.ACTIVE:
            pass

        # Inactive uploads will be handled by the periodic cleanup task eventually.
        elif upload.state == UploadState.INACTIVE:
            pass

        # If a (chunked) upload is still processing, check if the corresponding task is
        # still pending. If so, it will be up to the task to decide if the processing
        # completes or not, otherwise the task may have been canceled forcefully.
        elif upload.state == UploadState.PROCESSING:
            task = Task.query.filter(
                Task.name == const.TASK_MERGE_CHUNKS,
                Task.arguments["args"][0].astext == str(upload.id),
            ).first()

            if task is None or task.state != TaskState.PENDING:
                num_inconsistencies += 1
                inconsistent_items.append(Upload.query.get(upload.id))

                echo_danger(
                    f"[{num_inconsistencies}] Found processing (chunked) upload with"
                    f" storage type '{upload.storage_type}' and ID '{upload.id}' but"
                    f" no pending upload processing task."
                )

    if num_inconsistencies == 0:
        echo_success("Files checked successfully.")
    else:
        echo_warning(
            f"Found {num_inconsistencies}"
            f" {'inconsistency' if num_inconsistencies == 1 else 'inconsistencies'}."
        )

        if click.confirm(
            "Do you want to resolve all inconsistencies automatically by deleting all"
            " inconsistent database objects and associated data?"
        ):
            for item in inconsistent_items:
                if isinstance(item, File):
                    remove_file(item)
                else:
                    remove_upload(item)

            echo_success("Inconsistencies resolved successfully.")
