# Copyright 2022 Karlsruhe Institute of Technology
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
from marshmallow import fields
from marshmallow import validates
from marshmallow import ValidationError
from marshmallow.validate import OneOf
from marshmallow.validate import Range

from kadi.lib.schemas import KadiSchema
from kadi.lib.web import url_for
from kadi.modules.groups.models import Group


class BasicResourceSchema(KadiSchema):
    """Schema to represent the basic attributes of resources.

    Currently, these resources may refer to instances of :class:`.Record`,
    :class:`.Collection`, :class:`.Template` or :class:`.Group`.
    """

    id = fields.Integer(dump_only=True)

    title = fields.String(dump_only=True)

    identifier = fields.String(dump_only=True)

    visibility = fields.String(dump_only=True)

    created_at = fields.DateTime(dump_only=True)

    last_modified = fields.DateTime(dump_only=True)

    # The type of the resource.
    type = fields.String(dump_only=True)

    # The human-readable type of the resource.
    pretty_type = fields.String(dump_only=True)

    _links = fields.Method("_generate_links")

    def _generate_links(self, obj):
        return {
            "view": url_for(f"{obj.type}s.view_{obj.type}", id=obj.id),
        }


class DeletedResourceSchema(BasicResourceSchema):
    """Schema to represent the basic attributes of deleted resources."""

    # We simply use the last modification date, as it should not change for deleted
    # resources even when updating them.
    last_modified = fields.DateTime(dump_only=True, data_key="deleted_at")

    _actions = fields.Method("_generate_actions")

    def _generate_actions(self, obj):
        return {
            "restore": url_for(f"api.restore_{obj.type}", id=obj.id),
            "purge": url_for(f"api.purge_{obj.type}", id=obj.id),
        }


class BaseResourceRoleSchema(KadiSchema):
    """Base schema class to represent different kinds of resource roles.

    :param obj: (optional) An object that the current resource role refers to, which may
        be used when generating corresponding actions.
    """

    role = fields.Nested("RoleSchema", exclude=["permissions"], required=True)

    _actions = fields.Method("_generate_actions")

    def __init__(self, obj=None, **kwargs):
        super().__init__(**kwargs)
        self.obj = obj

    def _generate_actions(self, obj):
        return {}


class UserResourceRoleSchema(BaseResourceRoleSchema):
    """Schema to represent user roles.

    :param obj: (optional) An object that the current user role refers to. An instance
        of :class:`.Record`, :class:`.Collection`, :class:`.Template` or
        :class:`.Group`. See also :class:`BaseResourceRoleSchema`.
    """

    user = fields.Nested("UserSchema", required=True)

    def _generate_actions(self, obj):
        actions = {}

        try:
            user = getattr(obj, "user")
        except:
            user = obj.get("user")

        if user is None or self.obj is None:
            return actions

        if isinstance(self.obj, Group):
            kwargs = {"group_id": self.obj.id, "user_id": user.id}

            actions["remove_member"] = url_for("api.remove_group_member", **kwargs)
            actions["change_member"] = url_for("api.change_group_member", **kwargs)
        else:
            object_name = self.obj.__tablename__
            kwargs = {f"{object_name}_id": self.obj.id, "user_id": user.id}

            actions["remove_role"] = url_for(
                f"api.remove_{object_name}_user_role", **kwargs
            )
            actions["change_role"] = url_for(
                f"api.change_{object_name}_user_role", **kwargs
            )

        return actions

    def dump_from_iterable(self, iterable):
        """Serialize an iterable containing user roles.

        :param iterable: An iterable yielding tuples each containing a user and a
            corresponding role object.
        :return: The serialized output.
        """
        user_roles = [{"user": user, "role": role} for user, role in iterable]
        return self.dump(user_roles, many=True)


class GroupResourceRoleSchema(BaseResourceRoleSchema):
    """Schema to represent group roles.

    :param obj: (optional) An object that the current group role refers to. An instance
        of :class:`.Record`, :class:`.Collection` or :class:`.Template`. See also
        :class:`BaseResourceRoleSchema`.
    """

    group = fields.Nested("GroupSchema", required=True)

    def _generate_actions(self, obj):
        actions = {}

        try:
            group = getattr(obj, "group")
        except:
            group = obj.get("group")

        if group is None or self.obj is None:
            return actions

        object_name = self.obj.__tablename__
        kwargs = {f"{object_name}_id": self.obj.id, "group_id": group.id}

        actions["remove_role"] = url_for(
            f"api.remove_{object_name}_group_role", **kwargs
        )
        actions["change_role"] = url_for(
            f"api.change_{object_name}_group_role", **kwargs
        )

        return actions

    def dump_from_iterable(self, iterable):
        """Serialize an iterable containing group roles.

        :param iterable: An iterable yielding tuples each containing a group and a
            corresponding role object.
        :return: The serialized output.
        """
        group_roles = [{"group": group, "role": role} for group, role in iterable]
        return self.dump(group_roles, many=True)


class ResourceRoleDataSchema(KadiSchema):
    """Schema to represent the data of user or group resource roles.

    Mainly useful in combination with :func:`kadi.lib.resources.views.update_roles` and
    within templates.

    :param roles: A list of valid role values.
    """

    subject_type = fields.String(required=True, validate=OneOf(["user", "group"]))

    subject_id = fields.Integer(required=True, validate=Range(min=1))

    role = fields.String(required=True, allow_none=True)

    @validates("role")
    def _validate_role(self, value):
        # Always accept None values.
        if value is None:
            return

        if value not in self.roles:
            raise ValidationError(f"Must be one of: {', '.join(self.roles)}.")

    def __init__(self, roles, **kwargs):
        super().__init__(**kwargs)
        self.roles = set(roles)


def check_duplicate_identifier(model, identifier, exclude=None):
    """Check for a duplicate identifier in a schema.

    :param model: The model class to check the identifier of. One of :class:`.Record`,
        :class:`.Collection`, :class:`.Template` or :class:`.Group`.
    :param identifier: The identifier to check.
    :param exclude: (optional) An instance of the model that should be excluded in the
        check.
    """
    obj_to_check = model.query.filter_by(identifier=identifier).first()

    if obj_to_check is not None and (exclude is None or exclude != obj_to_check):
        raise ValidationError("Identifier is already in use.")
