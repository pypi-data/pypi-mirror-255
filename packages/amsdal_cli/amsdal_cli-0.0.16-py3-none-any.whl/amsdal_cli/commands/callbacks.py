import json
import os
from json import JSONDecodeError
from pathlib import Path

import typer
from rich import print

from amsdal_cli.utils.cli_config import CliConfig

COMMANDS_DO_NOT_REQUIRE_APP_PATH = ('new', 'write_logs')


def init_app_context(ctx: typer.Context) -> None:
    """
    AMSDAL CLI - a tool that provides the ability to create a new app,
    generate models, transactions, build, serve, and other useful features
    for the efficient building of new apps using AMSDAL Framework.
    """
    if not ctx.invoked_subcommand:
        return

    templates_path = Path(__file__).parent / ctx.invoked_subcommand / 'templates'

    if ctx.invoked_subcommand in COMMANDS_DO_NOT_REQUIRE_APP_PATH:
        ctx.meta['config'] = CliConfig(templates_path=templates_path)

        return

    app_path = Path(os.getcwd())
    cli_config = app_path / '.amsdal-cli'

    if not cli_config.exists():
        print(f'[red]The directory "{app_path.resolve()}" does not contain AMSDAL application.[/red]')
        print('Use the "amsdal new --help" command to see details about how to create an application.')
        raise typer.Exit(1)

    with cli_config.open('rt') as config_file:
        try:
            ctx.meta['config'] = CliConfig(
                app_directory=app_path,
                templates_path=templates_path,
                **json.loads(config_file.read()),
            )
        except JSONDecodeError as err:
            print(f'[red]The config file "{cli_config.resolve()}" is corrupted.[/red]')
            raise typer.Exit(1) from err
