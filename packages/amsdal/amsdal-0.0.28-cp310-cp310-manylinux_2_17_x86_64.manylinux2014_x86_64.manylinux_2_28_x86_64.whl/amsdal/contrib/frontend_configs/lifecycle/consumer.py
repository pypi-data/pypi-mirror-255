import logging
from typing import Any

from amsdal_models.schemas.data_models.core import LegacyDictSchema
from amsdal_models.schemas.data_models.schema import PropertyData
from amsdal_models.schemas.enums import CoreTypes
from amsdal_utils.lifecycle.consumer import LifecycleConsumer
from amsdal_utils.models.data_models.address import Address
from amsdal_utils.models.enums import Versions

logger = logging.getLogger(__name__)

core_to_frontend_types = {
    CoreTypes.NUMBER.value: 'number',
    CoreTypes.BOOLEAN.value: 'checkbox',
    CoreTypes.STRING.value: 'text',
    CoreTypes.ANYTHING.value: 'text',
    CoreTypes.BINARY.value: 'text',
}


def process_property(field_name: str, property_data: PropertyData) -> dict[str, Any]:
    type_definition: dict[str, Any]
    if property_data.type in core_to_frontend_types:
        type_definition = {
            'type': core_to_frontend_types[property_data.type],
        }
    elif property_data.type == CoreTypes.ARRAY.value:
        type_definition = {
            'type': 'array',
            'control': process_property(f'{field_name}_items', property_data.items),  # type: ignore[arg-type]
        }
    elif property_data.type == CoreTypes.DICTIONARY.value:
        if isinstance(property_data.items, LegacyDictSchema):
            type_definition = {
                'type': 'dict',
                'control': process_property(
                    f'{field_name}_items',
                    PropertyData(
                        type=property_data.items.key_type,
                        items=None,
                        title=None,
                        read_only=False,
                        options=None,
                        default=None,
                    ),
                ),
            }
        else:
            type_definition = {
                'type': 'dict',
                'control': process_property(
                    f'{field_name}_items',
                    property_data.items.key,  # type: ignore[union-attr, arg-type]
                ),
            }
    else:
        type_definition = {
            'type': 'object_latest',
            'entityType': property_data.type,
        }

    if getattr(property_data, 'default', None) is not None:
        type_definition['value'] = property_data.default

    if getattr(property_data, 'options', None) is not None:
        type_definition['options'] = [
            {
                'label': option.key,
                'value': option.value,
            }
            for option in property_data.options  # type: ignore[union-attr]
        ]

    return {
        'name': field_name,
        'label': property_data.title if hasattr(property_data, 'title') and property_data.title else field_name,
        **type_definition,
    }


def populate_frontend_config_with_values(config: dict[str, Any], values: dict[str, Any]) -> dict[str, Any]:
    if config.get('controls') and isinstance(config['controls'], list):
        for control in config['controls']:
            populate_frontend_config_with_values(control, values)

    if config.get('name') in values:
        config['value'] = values[config['name']]
    return config


def get_values_from_response(response: dict[str, Any]) -> dict[str, Any]:
    if 'rows' not in response or not response['rows']:
        return {}

    for row in response['rows']:
        if '_metadata' in row and row['_metadata'].get('next_version') is None:
            return row

    return response['rows'][0]


def get_default_control(class_name: str) -> dict[str, Any]:
    from amsdal.schemas.manager import SchemaManager
    from models.contrib.frontend_control_config import FrontendControlConfig  # type: ignore[import-not-found]

    schema = SchemaManager().get_schema_by_name(class_name)

    if schema is None:
        return {}

    return FrontendControlConfig(
        type='group',
        name=class_name,
        label=class_name,
        controls=(
            [process_property(field_name, property_data) for field_name, property_data in schema.properties.items()]
            if schema.properties
            else []
        ),
    ).model_dump(
        exclude_none=True,
    )


class ProcessResponseConsumer(LifecycleConsumer):
    def on_event(
        self,
        request: Any,
        response: dict[str, Any],
    ) -> None:
        from models.contrib.frontend_model_config import FrontendModelConfig  # type: ignore[import-not-found]

        class_name = None
        values = {}
        if hasattr(request, 'query_params') and 'class_name' in request.query_params:
            class_name = request.query_params['class_name']

        if hasattr(request, 'path_params') and 'address' in request.path_params:
            class_name = Address.from_string(request.path_params['address']).class_name
            values = get_values_from_response(response)

        if class_name:
            config = (
                FrontendModelConfig.objects.all()
                .first(
                    class_name=class_name,
                    _metadata__is_deleted=False,
                    _address__object_version=Versions.LATEST,
                )
                .execute()
            )

            if config and config.control:
                response['control'] = populate_frontend_config_with_values(
                    config.control.model_dump(exclude_none=True), values
                )
            else:
                response['control'] = populate_frontend_config_with_values(get_default_control(class_name), values)
