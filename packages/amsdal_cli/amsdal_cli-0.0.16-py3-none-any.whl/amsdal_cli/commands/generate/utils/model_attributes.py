import re
from typing import Any

import typer
from pydantic import BaseModel
from rich import print

from amsdal_cli.commands.generate.enums import AttributeType
from amsdal_cli.commands.generate.enums import JsonType
from amsdal_cli.commands.generate.enums import OptionName
from amsdal_cli.commands.generate.utils.cast_to_attribute_type import cast_to_attribute_type


class Attribute(BaseModel):
    class NotSet: ...

    name: str
    type: AttributeType
    reference: str | None = None
    default: Any = NotSet
    index: bool = False
    required: bool = False
    unique: bool = False
    item_key_type: str | None = None
    item_value_type: str | None = None

    @property
    def json_type(self) -> str | None:
        return self.resolve_attribute_type_to_json(self.type, reference_type=self.reference)

    @property
    def has_items(self) -> bool:
        return self.json_items is not None

    @property
    def json_items(self) -> dict[str, Any]:  # type: ignore[return]
        if self.reference and self.type == AttributeType.HAS_MANY:
            return {'type': self.reference}
        elif self.type == AttributeType.DICT and self.item_key_type and self.item_value_type:
            return {
                'key': {
                    'type': self.resolve_attribute_type_to_json(self.item_key_type, self.item_key_type),
                },
                'value': {
                    'type': self.resolve_attribute_type_to_json(self.item_value_type, self.item_value_type),
                },
            }

    @staticmethod
    def resolve_attribute_type_to_json(attribute_type: str | AttributeType, reference_type: str | None) -> str | None:
        try:
            match AttributeType(attribute_type):
                case AttributeType.STRING:
                    return JsonType.STRING.value
                case AttributeType.NUMBER:
                    return JsonType.NUMBER.value
                case AttributeType.BOOLEAN:
                    return JsonType.BOOLEAN.value
                case AttributeType.HAS_MANY:
                    return JsonType.ARRAY.value
                case AttributeType.DICT:
                    return JsonType.DICT.value
                case _:
                    return reference_type
        except ValueError:
            return reference_type


def parse_attributes(attrs: list[str]) -> list[Attribute]:
    attributes: dict[str, Attribute] = {}

    for _attr_item in attrs:
        if not _attr_item:
            continue

        attr_item = re.sub(r'\s+', ' ', _attr_item)

        for attr in attr_item.split(' '):
            [attr_name, _attr_type, *attr_options] = attr.split(':')
            attr_type = AttributeType(_attr_type)
            params: dict[str, Any] = {}

            if attr_name in attributes:
                print(f'[red]The "{attr_name}" attribute is duplicated![/red]')
                raise typer.Exit

            if attr_type in (AttributeType.BELONGS_TO, AttributeType.HAS_MANY):
                try:
                    params['reference'] = JsonType[AttributeType(attr_options[0].lower()).name].value
                except ValueError:
                    params['reference'] = attr_options[0]

                attr_options = attr_options[1:]
            elif attr_type == AttributeType.DICT:
                params['item_key_type'] = attr_options[0]
                params['item_value_type'] = attr_options[1]
                attr_options = attr_options[2:]

            for attr_option in attr_options:
                if attr_option.lower() == OptionName.INDEX.value:
                    params['index'] = True
                    continue

                # property can be marked as indexed + required + unique
                if attr_option.lower() == OptionName.REQUIRED.value:
                    params['required'] = True
                    continue

                # property can be marked as indexed + required + unique
                if attr_option.lower() == OptionName.UNIQUE.value:
                    params['unique'] = True
                    continue

                if '=' in attr_option:
                    _option, value = attr_option.split('=')
                    option = OptionName(_option)

                    match option:
                        case OptionName.DEFAULT:
                            params['default'] = cast_to_attribute_type(attr_type, value)
                        case _:
                            print(f'[red]Unknown option "{option}"[/red]')
                            raise typer.Exit

            attributes[attr_name] = Attribute(
                name=attr_name,
                type=attr_type,
                **params,
            )
    return list(attributes.values())
