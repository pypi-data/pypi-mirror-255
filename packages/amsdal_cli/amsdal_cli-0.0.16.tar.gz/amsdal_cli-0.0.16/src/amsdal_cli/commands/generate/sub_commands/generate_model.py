import json
from typing import Any

import typer
from amsdal_utils.utils.text import classify
from amsdal_utils.utils.text import to_snake_case
from rich import print

from amsdal_cli.commands.generate.app import sub_app
from amsdal_cli.commands.generate.enums import MODEL_JSON_FILE
from amsdal_cli.commands.generate.enums import SOURCES_DIR
from amsdal_cli.commands.generate.enums import ModelFormat
from amsdal_cli.commands.generate.utils.model_attributes import parse_attributes
from amsdal_cli.utils.cli_config import CliConfig
from amsdal_cli.utils.copier import write_file


@sub_app.command(name='model')
def generate_model(
    ctx: typer.Context,
    model_name: str = typer.Argument(
        ...,
        help='The model name. It should be provided in PascalCase.',
    ),
    model_format: ModelFormat = typer.Option(ModelFormat.JSON.value, '--format'),  # noqa: B008
    attrs: list[str] = typer.Option(  # noqa: B008
        (None,),
        '--attributes',
        '-attrs',
    ),
    unique: list[str] = typer.Option(  # noqa: B008
        (None,),
        '--unique',
        '-u',
    ),
) -> None:
    """
    Generates model file.

    Example of usage:

    >>> bin/cli --app-path ./apps/my_app/ generate model UserProfile --format json -attrs "name:string \
        email:string:index age:number:default=18"
    """

    if model_format == ModelFormat.PY:
        print('[red]The PY format is not supported for now.[/red]')
        raise typer.Exit

    cli_config: CliConfig = ctx.meta['config']
    model_name = classify(model_name)
    name = to_snake_case(model_name)

    output_path = cli_config.app_directory / SOURCES_DIR / 'models' / name
    parsed_attrs = parse_attributes(attrs)

    schema: dict[str, Any] = {
        'title': model_name,
        'type': 'object',
        'properties': {},
        'required': [attr.name for attr in parsed_attrs if attr.required],
        'indexed': [attr.name for attr in parsed_attrs if attr.index],
    }

    unique_attrs: list[str | tuple[str, ...]] = [attr.name for attr in parsed_attrs if attr.unique]

    for _unique in filter(None, unique):
        _unique_attrs = tuple(map(str.strip, _unique.split(',')))

        if _unique_attrs not in unique_attrs:
            unique_attrs.append(_unique_attrs)

    if unique_attrs:
        schema['unique_properties'] = unique_attrs

    for attr in parsed_attrs:
        property_info: dict[str, Any] = {
            'title': attr.name,
            'type': attr.json_type,
        }

        if attr.has_items:
            property_info['items'] = attr.json_items

        if attr.default != attr.NotSet:
            property_info['default'] = attr.default

        schema['properties'][attr.name] = property_info

    write_file(
        json.dumps(schema, indent=cli_config.json_indent),
        destination_file_path=output_path / MODEL_JSON_FILE,
        confirm_overwriting=True,
    )
