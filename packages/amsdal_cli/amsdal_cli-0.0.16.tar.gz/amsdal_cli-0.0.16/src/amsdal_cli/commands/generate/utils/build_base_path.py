from pathlib import Path

import typer
from amsdal_utils.utils.text import to_snake_case
from rich import print

from amsdal_cli.commands.generate.enums import SOURCES_DIR
from amsdal_cli.utils.cli_config import CliConfig


def build_model_base_path(ctx: typer.Context, model_name: str) -> Path:
    cli_config: CliConfig = ctx.meta['config']
    model = to_snake_case(model_name)
    model_path = cli_config.app_directory / SOURCES_DIR / 'models' / model

    if cli_config.check_model_exists and not (
        (model_path / 'model.json').exists() or (model_path / 'model.py').exists()
    ):
        print(f'[red]The model "{model_name}" does not exist.[/red]')
        raise typer.Exit

    return model_path
