from pathlib import Path

import typer
from amsdal.__about__ import __version__ as amsdal_version
from amsdal_utils.utils.text import slugify
from amsdal_utils.utils.text import to_snake_case
from rich import print

from amsdal_cli.app import app
from amsdal_cli.commands.generate.enums import SOURCES_DIR
from amsdal_cli.utils.copier import copy_blueprints_from_directory


@app.command(name='new')
def new_command(
    app_name: str = typer.Argument(
        ...,
        help='The Application name. For example: MyApplication',
    ),
    output_path: Path = typer.Argument(  # noqa: B008
        ...,
        help='Output path, where the app will be created.',
    ),
) -> None:
    """
    Generates a new AMSDAL application.
    """

    if not output_path.exists():
        print(f'[red]The output path "{output_path.resolve()}" does not exist.[/red]')
        raise typer.Exit

    if output_path.is_file():
        print(f'[red]The output path "{output_path.resolve()}" is not a directory.[/red]')
        raise typer.Exit

    output_path /= to_snake_case(app_name)

    if output_path.exists():
        if output_path.is_file():
            print(f'[red]The path "{output_path.resolve()}" is not a directory.[/red]')
            raise typer.Exit

        if any(output_path.iterdir()):
            print(f'[red]The directory "{output_path.resolve()}" is not empty.[/red]')
            raise typer.Exit

    copy_blueprints_from_directory(
        source_path=Path(__file__).parent / 'templates',
        destination_path=output_path,
        context={
            'application_name': app_name,
            'application_name_slugify': slugify(app_name),
            'amsdal_version': amsdal_version,
        },
    )
    (output_path / SOURCES_DIR).mkdir(exist_ok=True)

    print(f'[green]The application is successfully created in {output_path.resolve()}[/green]')
