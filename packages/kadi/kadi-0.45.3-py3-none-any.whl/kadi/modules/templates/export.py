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
from copy import deepcopy
from io import BytesIO

from flask_login import current_user

import kadi.lib.constants as const
from .models import TemplateType
from .schemas import TemplateSchema
from kadi.lib.tags.models import Tag
from kadi.lib.utils import formatted_json
from kadi.modules.records.export import filter_extras
from kadi.modules.records.extras import is_nested_type
from kadi.modules.records.models import Record


def get_dict_data(template, export_filter, user):
    """Export a template as a dictionary.

    See :func:`get_export_data` for an explanation of the parameters.

    :return: The exported template as a dictionary.
    """

    # Common attributes to exclude in all templates, also depending on whether user
    # information should be excluded.
    exclude_attrs = ["visibility", "plain_description", "state", "_actions", "_links"]

    if export_filter.get("user", False):
        exclude_attrs.append("creator")
    else:
        exclude_attrs += const.EXPORT_EXCLUDE_USER_ATTRS

    # Collect the basic metadata of the template.
    schema = TemplateSchema(exclude=exclude_attrs)
    template_data = schema.dump(template)

    # Exclude any filtered extra metadata, if applicable.
    exclude_extras = export_filter.get("extras")

    if exclude_extras:
        if template.type == TemplateType.RECORD:
            template_data["data"]["extras"] = filter_extras(
                template_data["data"]["extras"], exclude_extras
            )
        elif template.type == TemplateType.EXTRAS:
            template_data["data"] = filter_extras(template_data["data"], exclude_extras)

    return template_data


def get_json_data(template, export_filter, user):
    """Export a template as a JSON file.

    See :func:`get_export_data` for an explanation of the parameters and return value.
    """
    template_data = get_dict_data(template, export_filter, user)
    json_data = formatted_json(template_data)

    return BytesIO(json_data.encode())


JSON_SCHEMA_TYPE_MAPPING = {
    "str": {"type": ["string", "null"], "minLength": 1},
    "int": {"type": ["integer", "null"]},
    "float": {"type": ["number", "null"]},
    "bool": {"type": ["boolean", "null"]},
    "date": {"type": ["string", "null"], "format": "date-time"},
}


def _extras_to_json_schema(extras):
    extras_schema = {}

    for index, extra in enumerate(extras):
        extra_key = extra.get("key", str(index))

        if is_nested_type(extra["type"]):
            result = _extras_to_json_schema(extra["value"])

            if extra["type"] == "dict":
                extras_schema[extra_key] = {
                    "type": "object",
                    "properties": result,
                }
            else:
                # We handle the list as a tuple, so we can support different schemas for
                # all entries that are present.
                extras_schema[extra_key] = {
                    "type": "array",
                    "prefixItems": list(result.values()),
                }
        else:
            extras_schema[extra_key] = deepcopy(JSON_SCHEMA_TYPE_MAPPING[extra["type"]])

            if extra["value"] is not None:
                extras_schema[extra_key]["default"] = extra["value"]

            # We simply add the unit as a custom property in the JSON schema for now to
            # keep the validation of the actual values consistent across types.
            if "unit" in extra:
                extras_schema[extra_key]["unit"] = {
                    "type": ["string", "null"],
                    "minLength": 1,
                }
                if extra["unit"]:
                    extras_schema[extra_key]["unit"]["default"] = extra["unit"]

            if "validation" in extra:
                required = extra["validation"].get("required", False)

                if required:
                    # Remove the "null" type to implicitely make the value required.
                    type_list = extras_schema[extra_key]["type"]
                    extras_schema[extra_key]["type"] = type_list[0]

                if "options" in extra["validation"]:
                    # Make sure we work on a copy of the options list.
                    options = list(extra["validation"]["options"])

                    # To still allow for "null" values, the enum needs to include "null"
                    # as well.
                    if not required:
                        options.append(None)

                    extras_schema[extra_key]["enum"] = options

                if "range" in extra["validation"]:
                    value_range = extra["validation"]["range"]

                    if value_range["min"] is not None:
                        extras_schema[extra_key]["minimum"] = value_range["min"]

                    if value_range["max"] is not None:
                        extras_schema[extra_key]["maximum"] = value_range["max"]

    return extras_schema


def get_json_schema_data(template, user):
    """Export a template as a JSON Schema file in JSON format.

    See :func:`get_export_data` for an explanation of the parameters and return value.
    """
    template_data = get_dict_data(template, {}, user)
    json_schema = {"$schema": "https://json-schema.org/draft/2020-12/schema"}

    if template.type == TemplateType.RECORD:
        # Add the fixed record metadata to the record properties.
        record_constraints = Record.Meta.check_constraints
        record_properties = {
            "identifier": {
                "type": "string",
                "pattern": "^[a-z0-9-_]+$",
                "maxLength": record_constraints["identifier"]["length"]["max"],
            },
            "title": {
                "type": "string",
                "minLength": 1,
                "maxLength": record_constraints["title"]["length"]["max"],
            },
            "type": {
                "type": ["string", "null"],
                "minLength": 1,
                "maxLength": record_constraints["type"]["length"]["max"],
            },
            "description": {
                "type": "string",
                "maxLength": record_constraints["description"]["length"]["max"],
            },
            "license": {
                "type": ["string", "null"],
                "minLength": 1,
            },
            "tags": {
                "type": "array",
                "items": {
                    "type": "string",
                    "minLength": 1,
                    "maxLength": Tag.Meta.check_constraints["name"]["length"]["max"],
                },
            },
        }

        for key, value in record_properties.items():
            # Skip all falsy default values.
            if template_data["data"].get(key):
                value["default"] = template_data["data"][key]

        # Add the extra metadata to the record properties.
        record_properties["extras"] = {
            "type": "object",
            "properties": _extras_to_json_schema(
                template_data["data"].get("extras", [])
            ),
        }

        # Add the record properties to the schema, along with all additional validation.
        json_schema.update(
            {
                "type": "object",
                "properties": record_properties,
                "required": ["identifier", "title"],
                "additionalProperties": False,
            }
        )

    elif template.type == TemplateType.EXTRAS:
        json_schema.update(
            {
                "type": "object",
                "properties": _extras_to_json_schema(template_data["data"]),
            }
        )

    json_data = formatted_json(json_schema)
    return BytesIO(json_data.encode())


def get_export_data(template, export_type, export_filter=None, user=None):
    """Export a template in a given format.

    :param template: The template to export.
    :param export_type: The export type, one of ``"json"`` or ``"json-schema"``.
    :param export_filter: (optional) A dictionary specifying various filters to adjust
        the returned export data, depending on the export and template type. Only usable
        in combination with the ``"json"`` export type. Note that the values in the
        example below represent the respective default values.

        **Example:**

        .. code-block:: python3

            {
                # Whether user information about the creator of the template should be
                # excluded.
                "user": False,
                # A dictionary specifying a filter mask of extra metadata keys to
                # exclude, e.g. {"sample_key": {}, "sample_list": {"0": {}}}. The value
                # of each key can either be an empty dictionary, to exclude the whole
                # extra, or another dictionary with the same possibilities as in the
                # parent dictionary. For list entries, indices need to be specified as
                # strings, starting at 0.
                "extras": {},
            }


    :param user: (optional) The user to check for various access permissions when
        generating the export data. Defaults to the current user.
    :return: The exported template data as an in-memory byte stream using
        :class:`io.BytesIO` or ``None`` if an unknown export type was given.
    """
    export_filter = export_filter if export_filter is not None else {}
    user = user if user is not None else current_user

    if export_type == const.EXPORT_TYPE_JSON:
        return get_json_data(template, export_filter, user)

    if export_type == const.EXPORT_TYPE_JSON_SCHEMA:
        return get_json_schema_data(template, user)

    return None
