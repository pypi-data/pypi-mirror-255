from pathlib import Path

from amsdal.configs.main import settings
from amsdal.manager import AmsdalManager
from amsdal_utils.config.manager import AmsdalConfigManager
from rich import print

from amsdal_cli.commands.build.utils.build_config_file import build_config_file


def build_app(
    app_source_path: Path,
    config_path: Path,
    output: Path = Path('.'),
) -> None:
    settings.override(APP_PATH=output)
    config_manager = AmsdalConfigManager()
    config_manager.load_config(config_path)
    amsdal_manager = AmsdalManager()
    amsdal_manager.pre_setup()

    print('[blue]Building models...[/blue]', end=' ')
    amsdal_manager.build_models(app_source_path / 'models')
    print('[green]OK![/green]')

    if output == Path('.'):
        print('[yellow]No output directory specified, skipping config.yml generation[/yellow]')
    else:
        # build config file
        build_config_file(
            output_path=output,
            config_path=config_path,
            no_input=True,
        )

    print('[blue]Building transactions...[/blue]', end=' ')
    amsdal_manager.build_transactions(app_source_path)
    print('[green]OK![/green]')

    print('[blue]Building static files...[/blue]', end=' ')
    amsdal_manager.build_static_files(app_source_path)
    print('[green]OK![/green]')

    print('[blue]Building fixtures...[/blue]', end=' ')
    amsdal_manager.build_fixtures(app_source_path / 'models')
    print('[green]OK![/green]')
