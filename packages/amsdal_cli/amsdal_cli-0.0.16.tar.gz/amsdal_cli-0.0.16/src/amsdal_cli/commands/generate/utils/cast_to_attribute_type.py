from typing import Any

from amsdal_cli.commands.generate.enums import AttributeType


def cast_to_attribute_type(
    attr_type: AttributeType,
    value: str,
) -> Any:
    if value.lower() == 'null':
        return None

    match attr_type:
        case AttributeType.NUMBER:
            return float(value)
        case AttributeType.BOOLEAN:
            return value.lower() == 'true'
        case _:
            return value
