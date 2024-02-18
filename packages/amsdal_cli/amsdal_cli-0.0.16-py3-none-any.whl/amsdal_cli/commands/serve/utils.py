import shutil
from pathlib import Path

from amsdal.configs.main import settings
from amsdal.manager import AmsdalManager
from amsdal_utils.config.manager import AmsdalConfigManager
from rich import print


def cleanup_app(output_path: Path) -> None:
    """
    Cleanup the generated models and files after stopping.
    """

    for path in (
        (output_path / 'models'),
        (output_path / 'schemas'),
        (output_path / 'fixtures'),
        (output_path / 'warehouse'),
        (output_path / 'static'),
    ):
        shutil.rmtree(str(path.resolve()))


def build_app_and_migrate(
    output_path: Path,
    app_source_path: Path,
    config_path: Path,
    *,
    apply_migrations: bool,
    apply_fixtures: bool = True,
) -> AmsdalManager:
    settings.override(APP_PATH=output_path)

    config_manager = AmsdalConfigManager()
    config_manager.load_config(config_path)

    amsdal_manager = AmsdalManager()
    amsdal_manager.pre_setup()

    print('[blue]Building models...[/blue]', end=' ')
    amsdal_manager.build_models(app_source_path / 'models')
    print('[green]OK![/green]')

    if apply_migrations:
        print('[blue]Apply migrations...[/blue]')
        amsdal_manager = AmsdalManager()

        if not amsdal_manager._is_setup:
            amsdal_manager.setup()

        if not amsdal_manager.is_authenticated:
            amsdal_manager.authenticate()

        amsdal_manager.migrate()
        print('[green]OK![/green]')

    print('[blue]Building fixtures...[/blue]', end=' ')
    amsdal_manager.build_fixtures(app_source_path / 'models')
    print('[green]OK![/green]')

    if apply_fixtures:
        print('[blue]Applying fixtures...[/blue]', end=' ')
        if not amsdal_manager._is_setup:
            amsdal_manager.setup()

        if not amsdal_manager.is_authenticated:
            amsdal_manager.authenticate()

        amsdal_manager.apply_fixtures()
        print('[green]OK![/green]')

    return amsdal_manager
