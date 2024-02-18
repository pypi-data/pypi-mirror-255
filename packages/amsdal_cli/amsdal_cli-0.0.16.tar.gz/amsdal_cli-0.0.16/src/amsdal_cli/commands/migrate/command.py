from pathlib import Path

import typer
from amsdal.manager import AmsdalManager
from rich import print

from amsdal_cli.app import app
from amsdal_cli.commands.build.utils.build_app import build_app
from amsdal_cli.commands.generate.enums import SOURCES_DIR
from amsdal_cli.utils.cli_config import CliConfig


@app.command(name='migrate')
def migrate_command(
    ctx: typer.Context,
    output: Path = typer.Argument('.', help='Path to output directory'),  # noqa: B008
    *,
    config: Path = typer.Option(None, help='Path to custom config.yml file'),  # noqa: B008
) -> None:
    """
    Apply migrations and fixtures to the database.
    """
    cli_config: CliConfig = ctx.meta['config']
    app_source_path = cli_config.app_directory / SOURCES_DIR

    build_app(
        app_source_path=app_source_path,
        config_path=config or cli_config.config_path,
        output=output,
    )
    amsdal_manager = AmsdalManager()

    print('[blue]Apply migrations...[/blue]')
    amsdal_manager.setup()
    amsdal_manager.authenticate()
    amsdal_manager.migrate()
    amsdal_manager.apply_fixtures()
    print('[green]OK![/green]')
