from pathlib import Path

import typer
from rich import print


def build_config_file(
    output_path: Path,
    config_path: Path,
    *,
    no_input: bool,
) -> None:
    print('[blue]Building config.yml file...[/blue]', end=' ')

    if not config_path.exists() or not config_path.name.endswith('.yml'):
        print(f'\n[red]Config file "{config_path.resolve()}" does not exist or has wrong extension.[/red]')
        raise typer.Exit(1)

    config_destination = output_path / 'config.yml'

    if (
        no_input
        or not config_destination.exists()
        or (
            typer.confirm(
                f'\nThe config file "{config_destination.resolve()}" already exists. Would you like to overwrite it?',
            )
        )
    ):
        config_destination.parent.mkdir(parents=True, exist_ok=True)
        config_destination.touch(exist_ok=True)

        with config_path.open('rt') as _file:
            config_destination.write_text(_file.read())

    print('[green]OK![/green]')
