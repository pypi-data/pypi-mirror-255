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
from flask_babel import gettext as _
from flask_babel import lazy_gettext as _l
from flask_login import current_user
from marshmallow import ValidationError
from wtforms.validators import DataRequired
from wtforms.validators import InputRequired
from wtforms.validators import Length
from wtforms.validators import NumberRange
from wtforms.validators import StopValidation

import kadi.lib.constants as const
from .extras import ExtrasField
from .models import Chunk
from .models import File
from .models import FileState
from .models import Record
from .models import RecordLink
from .models import RecordVisibility
from .models import Upload
from .schemas import RecordLinkDataSchema
from kadi.ext.db import db
from kadi.lib.conversion import empty_str
from kadi.lib.conversion import lower
from kadi.lib.conversion import none
from kadi.lib.conversion import normalize
from kadi.lib.conversion import strip
from kadi.lib.format import filesize
from kadi.lib.forms import BooleanField
from kadi.lib.forms import convert_schema_validation_msg
from kadi.lib.forms import DynamicMultiSelectField
from kadi.lib.forms import DynamicSelectField
from kadi.lib.forms import FileField
from kadi.lib.forms import IntegerField
from kadi.lib.forms import JSONField
from kadi.lib.forms import KadiForm
from kadi.lib.forms import LFTextAreaField
from kadi.lib.forms import SelectField
from kadi.lib.forms import StringField
from kadi.lib.forms import SubmitField
from kadi.lib.forms import validate_identifier
from kadi.lib.forms import validate_iri
from kadi.lib.forms import validate_mimetype
from kadi.lib.licenses.models import License
from kadi.lib.permissions.core import get_permitted_objects
from kadi.lib.permissions.core import has_permission
from kadi.lib.resources.forms import check_duplicate_identifier
from kadi.lib.resources.forms import RolesField
from kadi.lib.resources.forms import TagsField
from kadi.lib.storage.core import get_storage
from kadi.lib.tags.models import Tag
from kadi.modules.collections.models import Collection
from kadi.modules.collections.models import CollectionState
from kadi.modules.records.links import get_permitted_record_links
from kadi.modules.templates.models import TemplateType


class BaseRecordForm(KadiForm):
    """Base form class for use in creating or updating records.

    :param record: (optional) A record used for prefilling the form.
    :param template: (optional) A record or extras template used for prefilling the
        form.
    """

    title = StringField(
        _l("Title"),
        filters=[normalize],
        validators=[
            DataRequired(),
            Length(max=Record.Meta.check_constraints["title"]["length"]["max"]),
        ],
    )

    identifier = StringField(
        _l("Identifier"),
        filters=[lower, strip],
        validators=[
            DataRequired(),
            Length(max=Record.Meta.check_constraints["identifier"]["length"]["max"]),
            validate_identifier,
        ],
        description=_l("Unique identifier of this record."),
    )

    type = DynamicSelectField(
        _l("Type"),
        filters=[lower, normalize],
        validators=[Length(max=Record.Meta.check_constraints["type"]["length"]["max"])],
        description=_l(
            "Optional type of this record, e.g. dataset, experimental device, etc."
        ),
    )

    description = LFTextAreaField(
        _l("Description"),
        filters=[empty_str],
        validators=[
            Length(max=Record.Meta.check_constraints["description"]["length"]["max"])
        ],
    )

    license = DynamicSelectField(
        _l("License"),
        description=_l(
            "Specifying an optional license can determine the conditions for the"
            " correct reuse of data and metadata when the record is published or simply"
            " shared with other users. A license can also be uploaded as a file, in"
            ' which case one of the "Other" licenses can be chosen.'
        ),
    )

    visibility = SelectField(
        _l("Visibility"),
        choices=[
            (RecordVisibility.PRIVATE, _l("Private")),
            (RecordVisibility.PUBLIC, _l("Public")),
        ],
        description=_l(
            "Public visibility automatically grants EVERY logged-in user read"
            " permissions for this record."
        ),
    )

    tags = TagsField(
        _l("Tags"),
        max_len=Tag.Meta.check_constraints["name"]["length"]["max"],
        description=_l("An optional list of keywords further describing the record."),
    )

    extras = ExtrasField(_l("Extra metadata"))

    def _prefill_license(self, license):
        if license is not None:
            self.license.initial = (license.name, license.title)

    def __init__(self, *args, record=None, template=None, **kwargs):
        data = None

        # Prefill all simple fields using the "data" attribute.
        if record is not None:
            data = {
                "title": record.title,
                "identifier": record.identifier,
                "description": record.description,
                "visibility": record.visibility,
                "extras": record.extras,
            }
        elif template is not None:
            if template.type == TemplateType.RECORD:
                data = {
                    "title": template.data.get("title", ""),
                    "identifier": template.data.get("identifier", ""),
                    "description": template.data.get("description", ""),
                    "extras": template.data.get("extras", []),
                }
            elif template.type == TemplateType.EXTRAS:
                data = {"extras": template.data}

        super().__init__(*args, data=data, **kwargs)

        # Prefill all other fields separately, depending on whether the form was
        # submitted or not.
        if self.is_submitted():
            if self.type.data is not None:
                self.type.initial = (self.type.data, self.type.data)

            if self.license.data is not None:
                license = License.query.filter_by(name=self.license.data).first()
                self._prefill_license(license)

            self.tags.initial = [(tag, tag) for tag in sorted(self.tags.data)]

        elif record is not None:
            if record.type is not None:
                self.type.initial = (record.type, record.type)

            self._prefill_license(record.license)

            self.tags.initial = [
                (tag.name, tag.name) for tag in record.tags.order_by("name")
            ]

        elif template is not None and template.type == TemplateType.RECORD:
            if template.data.get("type") is not None:
                self.type.initial = (template.data["type"], template.data["type"])

            if template.data.get("license") is not None:
                license = License.query.filter_by(name=template.data["license"]).first()
                self._prefill_license(license)

            self.tags.initial = [
                (tag, tag) for tag in sorted(template.data.get("tags", []))
            ]

    def validate_license(self, field):
        # pylint: disable=missing-function-docstring
        if (
            field.data is not None
            and License.query.filter_by(name=field.data).first() is None
        ):
            raise StopValidation(_("Not a valid license."))


class RecordLinksField(JSONField):
    """Custom field to process and validate record links.

    Uses :class:`.RecordLinkDataSchema` for its validation.
    """

    def __init__(self, *args, **kwargs):
        kwargs["default"] = []
        super().__init__(*args, **kwargs)

        self.initial = []
        self._validation_errors = {}

    def _value(self):
        return self.initial

    def process_formdata(self, valuelist):
        super().process_formdata(valuelist)

        if valuelist:
            try:
                schema = RecordLinkDataSchema(many=True)
                self.data = schema.load(self.data)

            except ValidationError as e:
                self._validation_errors = e.messages

                # Check if at least the basic structure of the data is valid and discard
                # it otherwise.
                if not isinstance(self.data, list):
                    self.data = self.default
                    self._validation_errors = {}
                else:
                    for item in self.data:
                        if not isinstance(item, dict):
                            self.data = self.default
                            self._validation_errors = {}
                            break

                raise ValueError("Invalid data structure.") from e

    def to_dict(self):
        data = super().to_dict()

        constraints = RecordLink.Meta.check_constraints
        max_term_len = constraints["term"]["length"]["max"]

        data["validation"]["max"] = {
            "name": constraints["name"]["length"]["max"],
            "term": max_term_len,
        }
        data["errors"] = self._validation_errors

        for error_data in data["errors"].values():
            for field_name, error_msgs in error_data.items():
                for index, error_msg in enumerate(error_msgs):
                    interpolations = {}

                    if field_name == "term":
                        interpolations["max"] = max_term_len

                    error_msgs[index] = convert_schema_validation_msg(
                        error_msg, **interpolations
                    )

        return data

    def set_initial_data(self, data=None, record=None, user=None):
        """Set the initial data of this field.

        :param data: (optional) The form data to use for prefilling. Defaults to the
            submitted data of the current field instance.
        :param record: (optional) An existing record, which can be used to set the
            initial data instead of the given form data.
        :param user: (optional) A user that will be used for checking various access
            permissions when setting the data. Defaults to the current user.
        """
        data = data if data is not None else getattr(self, "data", [])
        user = user if user is not None else current_user

        initial_data = []

        if record is not None:
            record_links_query = get_permitted_record_links(
                record, actions=["link"], user=user
            ).order_by(RecordLink.created_at)

            for record_link in record_links_query:
                if record_link.record_from_id == record.id:
                    direction = "out"
                    linked_record = record_link.record_to
                else:
                    direction = "in"
                    linked_record = record_link.record_from

                initial_data.append(
                    {
                        "direction": direction,
                        "record": [linked_record.id, f"@{linked_record.identifier}"],
                        "name": record_link.name,
                        "term": record_link.term,
                    }
                )

        else:
            # Make sure to not rely on the data contents, as invalid (submitted) form
            # data is only discarded if the overall structure is invalid.
            for link_meta in data:
                linked_record_data = None
                record_id = link_meta.get("record")

                # pylint: disable=unidiomatic-typecheck
                if type(record_id) is int:
                    linked_record = Record.query.get_active(record_id)

                    if linked_record is not None and has_permission(
                        user, "link", "record", linked_record.id
                    ):
                        linked_record_data = [
                            linked_record.id,
                            f"@{linked_record.identifier}",
                        ]

                initial_data.append(
                    {
                        "direction": link_meta.get("direction", "out"),
                        "record": linked_record_data,
                        "name": link_meta.get("name"),
                        "term": link_meta.get("term"),
                    }
                )

        self.initial = initial_data


class NewRecordForm(BaseRecordForm):
    """A form for use in creating new records.

    :param record: (optional) See :class:`BaseRecordForm`.
    :param template: (optional) See :class:`BaseRecordForm`.
    :param collection: (optional) A collection used for prefilling the linked
        collections.
    :param user: (optional) A user that will be used for checking various access
        permissions when prefilling the form. Defaults to the current user.
    """

    collections = DynamicMultiSelectField(
        _l("Collections"),
        coerce=int,
        description=_l("Directly link this record with one or more collections."),
    )

    record_links = RecordLinksField(
        _l("Record links"),
        description=_l("Directly link this record with one or more other records."),
    )

    roles = RolesField(
        _l("Permissions"),
        roles=[(r, r.capitalize()) for r, _ in Record.Meta.permissions["roles"]],
        description=_l("Directly add user or group roles to this record."),
    )

    submit = SubmitField(_l("Create record"))

    submit_files = SubmitField(_l("Create record and add files"))

    def _prefill_collections(self, collections):
        self.collections.initial = [
            (collection.id, f"@{collection.identifier}") for collection in collections
        ]

    def __init__(
        self, *args, record=None, template=None, collection=None, user=None, **kwargs
    ):
        user = user if user is not None else current_user

        super().__init__(*args, record=record, template=template, **kwargs)

        linkable_collection_ids_query = (
            get_permitted_objects(user, "link", "collection")
            .filter(Collection.state == CollectionState.ACTIVE)
            .with_entities(Collection.id)
        )

        if self.is_submitted():
            if self.collections.data:
                collections = Collection.query.filter(
                    db.and_(
                        Collection.id.in_(linkable_collection_ids_query),
                        Collection.id.in_(self.collections.data),
                    )
                )
                self._prefill_collections(collections)

            self.record_links.set_initial_data(user=user)
            self.roles.set_initial_data(user=user)

        else:
            if record is not None:
                collections = record.collections.filter(
                    Collection.id.in_(linkable_collection_ids_query)
                )
                self._prefill_collections(collections)

                self.record_links.set_initial_data(record=record, user=user)
                self.roles.set_initial_data(resource=record, user=user)

            elif template is not None and template.type == TemplateType.RECORD:
                if template.data.get("collections"):
                    collections = Collection.query.filter(
                        db.and_(
                            Collection.id.in_(linkable_collection_ids_query),
                            Collection.id.in_(template.data["collections"]),
                        )
                    )
                    self._prefill_collections(collections)

                self.record_links.set_initial_data(
                    data=template.data.get("record_links", []), user=user
                )
                self.roles.set_initial_data(
                    data=template.data.get("roles", []), user=user
                )

            # If a collection is given, overwrite all values set previously for the
            # linked collections.
            if collection is not None:
                self._prefill_collections([collection])

    def validate_identifier(self, field):
        # pylint: disable=missing-function-docstring
        check_duplicate_identifier(Record, field.data)


class EditRecordForm(BaseRecordForm):
    """A form for use in editing existing records.

    :param record: The record to edit, used for prefilling the form.
    """

    submit = SubmitField(_l("Save changes"))

    submit_quit = SubmitField(_l("Save changes and quit"))

    def __init__(self, record, *args, **kwargs):
        self.record = record
        super().__init__(*args, record=record, **kwargs)

    def validate_identifier(self, field):
        # pylint: disable=missing-function-docstring
        check_duplicate_identifier(Record, field.data, exclude=self.record)


class AddRecordLinksForm(KadiForm):
    """A form for use in creating new record links.

    :param user: (optional) A user that will be used for checking various access
        permissions when prefilling the form. Defaults to the current user.
    """

    record_links = RecordLinksField(_l("New record links"))

    submit = SubmitField(_l("Link records"))

    def __init__(self, *args, user=None, **kwargs):
        user = user if user is not None else current_user

        super().__init__(*args, **kwargs)

        if self.is_submitted():
            self.record_links.set_initial_data(user=user)


class EditRecordLinkForm(KadiForm):
    """A form for use in editing existing record links.

    :param record_link: The record link to edit, used for prefilling the form.
    """

    name = DynamicSelectField(
        _l("Name"),
        filters=[normalize],
        validators=[
            DataRequired(),
            Length(max=RecordLink.Meta.check_constraints["name"]["length"]["max"]),
        ],
        description=_l("The name of the link."),
    )

    term = StringField(
        _l("Term IRI"),
        filters=[strip, none],
        validators=[
            Length(max=RecordLink.Meta.check_constraints["term"]["length"]["max"]),
            validate_iri,
        ],
        description=_l(
            "An IRI specifying an existing term that the link should represent."
        ),
    )

    submit = SubmitField(_l("Save changes"))

    def __init__(self, record_link, *args, **kwargs):
        data = None

        # Prefill all simple fields using the "data" attribute.
        if record_link is not None:
            data = {"term": record_link.term}

        super().__init__(*args, data=data, **kwargs)

        # Prefill all other fields separately, depending on whether the form was
        # submitted or not.
        if self.is_submitted():
            if self.name.data is not None:
                self.name.initial = (self.name.data, self.name.data)

        elif record_link is not None:
            if record_link.name is not None:
                self.name.initial = (record_link.name, record_link.name)


class LinkCollectionsForm(KadiForm):
    """A form for use in linking records with collections."""

    collections = DynamicMultiSelectField(
        _l("Collections"), validators=[DataRequired()], coerce=int
    )

    submit = SubmitField(_l("Link collections"))


class AddRolesForm(KadiForm):
    """A form for use in adding user or group roles to a record."""

    roles = RolesField(
        _l("New permissions"),
        roles=[(r, r.capitalize()) for r, _ in Record.Meta.permissions["roles"]],
    )

    submit = SubmitField(_l("Add permissions"))


class UploadDataForm(KadiForm):
    """A form for use in uploading data for direct uploads.

    Currently only used within the API with data sent via custom headers.
    """

    class Meta:
        """Container to store meta class attributes."""

        csrf = False

    checksum = StringField(
        filters=[strip, none],
        validators=[
            Length(max=Upload.Meta.check_constraints["checksum"]["length"]["max"])
        ],
    )


# Custom validation messages for form fields used in an API context to better match the
# usual schema validation.
FORM_VALIDATION_MISSING_DATA = "Missing data for required field."
FORM_VALIDATION_RANGE_GTE = "Must be greater than or equal to %(min)s."


class UploadChunkForm(KadiForm):
    """A form for use in uploading data for chunked uploads.

    Currently only used within the API with data sent via custom headers.

    :param chunk_count: The total amount of chunks that the upload this chunk is part of
        has. Will be used to validate the chunk's index and size.
    """

    class Meta:
        """Container to store meta class attributes."""

        csrf = False

    index = IntegerField(
        validators=[
            InputRequired(message=FORM_VALIDATION_MISSING_DATA),
            NumberRange(
                min=Chunk.Meta.check_constraints["index"]["range"]["min"],
                message=FORM_VALIDATION_RANGE_GTE,
            ),
        ]
    )

    size = IntegerField(
        validators=[
            InputRequired(message=FORM_VALIDATION_MISSING_DATA),
            NumberRange(
                min=Chunk.Meta.check_constraints["size"]["range"]["min"],
                message=FORM_VALIDATION_RANGE_GTE,
            ),
        ],
    )

    checksum = StringField(
        filters=[strip, none],
        validators=[
            Length(max=Chunk.Meta.check_constraints["checksum"]["length"]["max"])
        ],
    )

    def __init__(self, chunk_count, *args, **kwargs):
        self.chunk_count = chunk_count
        super().__init__(*args, **kwargs)

    def validate_index(self, field):
        # pylint: disable=missing-function-docstring
        if field.data is not None and field.data >= self.chunk_count:
            raise StopValidation(f"Must be less than {self.chunk_count}.")

    def validate_size(self, field):
        # pylint: disable=missing-function-docstring
        chunk_size = field.data

        if chunk_size is not None:
            if chunk_size > const.UPLOAD_CHUNK_SIZE:
                raise StopValidation(
                    f"Chunk size ({filesize(const.UPLOAD_CHUNK_SIZE)}) exceeded."
                )

            chunk_index = self.index.data

            if (
                chunk_index is not None
                and chunk_size < const.UPLOAD_CHUNK_SIZE
                and chunk_index < self.chunk_count - 1
            ):
                raise StopValidation(
                    "Only the last chunk may be smaller than the chunk size"
                    f" ({filesize(const.UPLOAD_CHUNK_SIZE)})."
                )


class EditFileForm(KadiForm):
    """A form for use in editing file metadata.

    :param file: A file used for prefilling the form and checking for duplicate file
        names.
    """

    name = StringField(
        _l("Filename"),
        filters=[normalize],
        validators=[
            DataRequired(),
            Length(max=File.Meta.check_constraints["name"]["length"]["max"]),
        ],
    )

    mimetype = StringField(
        _l("MIME type"),
        filters=[lower, normalize],
        validators=[
            DataRequired(),
            Length(max=File.Meta.check_constraints["mimetype"]["length"]["max"]),
            validate_mimetype,
        ],
    )

    description = LFTextAreaField(
        _l("Description"),
        filters=[empty_str],
        validators=[
            Length(max=File.Meta.check_constraints["description"]["length"]["max"])
        ],
    )

    submit = SubmitField(_l("Save changes"))

    def __init__(self, file, *args, **kwargs):
        self.file = file
        super().__init__(*args, obj=file, **kwargs)

    def validate_name(self, field):
        # pylint: disable=missing-function-docstring
        file = File.query.filter(
            File.record_id == self.file.record_id,
            File.state == FileState.ACTIVE,
            File.name == field.data,
        ).first()

        if file is not None and self.file != file:
            raise StopValidation(_("Name is already in use."))


class LegacyUploadChunkForm(UploadChunkForm):
    """A form for use in uploading chunks.

    Currently only kept for backwards compatibility.
    """

    blob = FileField(validators=[DataRequired(message=FORM_VALIDATION_MISSING_DATA)])


class LegacyUploadDataForm(KadiForm):
    """A form for use in directly uploading files.

    Currently only kept for backwards compatibility.
    """

    class Meta:
        """Container to store meta class attributes."""

        csrf = False

    name = StringField(
        filters=[normalize],
        validators=[
            DataRequired(message=FORM_VALIDATION_MISSING_DATA),
            Length(
                max=Upload.Meta.check_constraints["name"]["length"]["max"],
                message="Longer than maximum length %(max)s.",
            ),
        ],
    )

    size = IntegerField(
        validators=[
            InputRequired(message=FORM_VALIDATION_MISSING_DATA),
            NumberRange(
                min=Upload.Meta.check_constraints["size"]["range"]["min"],
                message=FORM_VALIDATION_RANGE_GTE,
            ),
        ],
    )

    blob = FileField(validators=[DataRequired(message=FORM_VALIDATION_MISSING_DATA)])

    description = StringField(
        validators=[
            Length(max=Upload.Meta.check_constraints["description"]["length"]["max"])
        ],
    )

    mimetype = StringField(
        filters=[lower, normalize],
        validators=[
            Length(max=Upload.Meta.check_constraints["mimetype"]["length"]["max"]),
            validate_mimetype,
        ],
    )

    checksum = StringField(
        filters=[strip],
        validators=[
            Length(max=Upload.Meta.check_constraints["checksum"]["length"]["max"])
        ],
    )

    storage_type = StringField(default=const.STORAGE_TYPE_LOCAL)

    replace_file = BooleanField()

    def validate_storage_type(self, field):
        # pylint: disable=missing-function-docstring
        if not get_storage(field.data):
            raise StopValidation("Not a valid storage type.")
