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
from flask_babel import lazy_gettext as _l
from flask_login import current_user
from wtforms.validators import DataRequired
from wtforms.validators import Length

from .models import Collection
from .models import CollectionVisibility
from kadi.ext.db import db
from kadi.lib.conversion import empty_str
from kadi.lib.conversion import lower
from kadi.lib.conversion import normalize
from kadi.lib.conversion import strip
from kadi.lib.forms import DynamicMultiSelectField
from kadi.lib.forms import DynamicSelectField
from kadi.lib.forms import KadiForm
from kadi.lib.forms import LFTextAreaField
from kadi.lib.forms import SelectField
from kadi.lib.forms import StringField
from kadi.lib.forms import SubmitField
from kadi.lib.forms import validate_identifier
from kadi.lib.permissions.core import get_permitted_objects
from kadi.lib.permissions.core import has_permission
from kadi.lib.resources.forms import check_duplicate_identifier
from kadi.lib.resources.forms import RolesField
from kadi.lib.resources.forms import TagsField
from kadi.lib.tags.models import Tag
from kadi.modules.records.models import Record
from kadi.modules.records.models import RecordState
from kadi.modules.templates.models import Template
from kadi.modules.templates.models import TemplateState
from kadi.modules.templates.models import TemplateType


class BaseCollectionForm(KadiForm):
    """Base form class for use in creating or updating collections.

    :param collection: (optional) A collection used for prefilling the form.
    :param user: (optional) A user that will be used for checking various access
        permissions when prefilling the form. Defaults to the current user.
    """

    title = StringField(
        _l("Title"),
        filters=[normalize],
        validators=[
            DataRequired(),
            Length(max=Collection.Meta.check_constraints["title"]["length"]["max"]),
        ],
    )

    identifier = StringField(
        _l("Identifier"),
        filters=[strip, lower],
        validators=[
            DataRequired(),
            Length(
                max=Collection.Meta.check_constraints["identifier"]["length"]["max"]
            ),
            validate_identifier,
        ],
        description=_l("Unique identifier of this collection."),
    )

    description = LFTextAreaField(
        _l("Description"),
        filters=[empty_str],
        validators=[
            Length(
                max=Collection.Meta.check_constraints["description"]["length"]["max"]
            )
        ],
    )

    visibility = SelectField(
        _l("Visibility"),
        choices=[
            (CollectionVisibility.PRIVATE, _l("Private")),
            (CollectionVisibility.PUBLIC, _l("Public")),
        ],
        description=_l(
            "Public visibility automatically grants EVERY logged-in user read"
            " permissions for this collection."
        ),
    )

    tags = TagsField(
        _l("Tags"),
        max_len=Tag.Meta.check_constraints["name"]["length"]["max"],
        description=_l(
            "An optional list of keywords further describing the collection."
        ),
    )

    record_template = DynamicSelectField(
        _l("Default record template"),
        coerce=int,
        description=_l(
            "A record template that will be used as a default when adding new records"
            " to this collection."
        ),
    )

    def _check_template_permission(self, template):
        return has_permission(self.user, "read", "template", template.id)

    def _prefill_record_template(self, template):
        if (
            template is not None
            and template.state == TemplateState.ACTIVE
            and template.type == TemplateType.RECORD
            and self._check_template_permission(template)
        ):
            self.record_template.initial = (template.id, f"@{template.identifier}")

    def __init__(self, *args, collection=None, user=None, **kwargs):
        self.user = user if user is not None else current_user

        data = None

        # Prefill all simple fields using the "data" attribute.
        if collection is not None:
            data = {
                "title": collection.title,
                "identifier": collection.identifier,
                "description": collection.description,
                "visibility": collection.visibility,
            }

        super().__init__(*args, data=data, **kwargs)

        # Prefill all other fields separately, depending on whether the form was
        # submitted or not.
        if self.is_submitted():
            self.tags.initial = [(tag, tag) for tag in sorted(self.tags.data)]

            if self.record_template.data:
                template = Template.query.get(self.record_template.data)
                self._prefill_record_template(template)

        elif collection is not None:
            self.tags.initial = [
                (tag.name, tag.name) for tag in collection.tags.order_by("name")
            ]

            self._prefill_record_template(collection.record_template)


class NewCollectionForm(BaseCollectionForm):
    """A form for use in creating new collections.

    :param collection: (optional) See :class:`BaseCollectionForm`.
    :param user: (optional) See :class:`BaseCollectionForm`.
    """

    records = DynamicMultiSelectField(
        _l("Linked records"),
        coerce=int,
        description=_l("Directly link this collection with one or more records."),
    )

    roles = RolesField(
        _l("Permissions"),
        roles=[(r, r.capitalize()) for r, _ in Collection.Meta.permissions["roles"]],
        description=_l("Directly add user or group roles to this collection."),
    )

    submit = SubmitField(_l("Create collection"))

    def _prefill_records(self, records):
        self.records.initial = [
            (record.id, f"@{record.identifier}") for record in records
        ]

    def __init__(self, *args, collection=None, user=None, **kwargs):
        user = user if user is not None else current_user

        super().__init__(*args, collection=collection, user=user, **kwargs)

        linkable_record_ids_query = (
            get_permitted_objects(user, "link", "record")
            .filter(Record.state == RecordState.ACTIVE)
            .with_entities(Record.id)
        )

        if self.is_submitted():
            if self.records.data:
                records = Record.query.filter(
                    db.and_(
                        Record.id.in_(linkable_record_ids_query),
                        Record.id.in_(self.records.data),
                    )
                )
                self._prefill_records(records)

            self.roles.set_initial_data(user=user)

        elif collection is not None:
            records = collection.records.filter(
                Record.id.in_(linkable_record_ids_query)
            )
            self._prefill_records(records)

            self.roles.set_initial_data(resource=collection, user=user)

    def validate_identifier(self, field):
        # pylint: disable=missing-function-docstring
        check_duplicate_identifier(Collection, field.data)


class EditCollectionForm(BaseCollectionForm):
    """A form for use in editing existing collections.

    :param collection: The collection to edit, used for prefilling the form.
    :param user: (optional) See :class:`BaseCollectionForm`.
    """

    submit = SubmitField(_l("Save changes"))

    submit_quit = SubmitField(_l("Save changes and quit"))

    def _check_template_permission(self, template):
        # See "modules.collections.core.update_collection" on why this special check is
        # done here.
        return (
            has_permission(self.user, "read", "template", template.id)
            or self.collection.record_template == template
        )

    def __init__(self, collection, *args, user=None, **kwargs):
        user = user if user is not None else current_user

        self.collection = collection
        self.user = user

        super().__init__(*args, collection=collection, user=user, **kwargs)

    def validate_identifier(self, field):
        # pylint: disable=missing-function-docstring
        check_duplicate_identifier(Collection, field.data, exclude=self.collection)


class LinkRecordsForm(KadiForm):
    """A form for use in linking collections with records."""

    records = DynamicMultiSelectField(
        _l("Records"), validators=[DataRequired()], coerce=int
    )

    submit = SubmitField(_l("Link records"))


class LinkCollectionsForm(KadiForm):
    """A form for use in linking collections with other collections."""

    collections = DynamicMultiSelectField(
        _l("Collections"), validators=[DataRequired()], coerce=int
    )

    submit = SubmitField(_l("Link collections"))


class AddCollectionRolesForm(KadiForm):
    """A form for use in adding user or group roles to a collection."""

    roles = RolesField(
        _l("New permissions"),
        roles=[(r, r.capitalize()) for r, _ in Collection.Meta.permissions["roles"]],
    )

    submit = SubmitField(_l("Add permissions"))


class UpdateRecordsRolesForm(KadiForm):
    """A form for use in updating user or group roles of linked records."""

    roles = RolesField(
        _l("New permissions"),
        roles=[(r, r.capitalize()) for r, _ in Record.Meta.permissions["roles"]],
    )

    submit = SubmitField(_l("Apply permissions"))
