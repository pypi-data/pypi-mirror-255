from pathlib import Path
from typing import Any
from typing import Optional

import typer
from amsdal.migration.manager import MigrationManager
from amsdal_server.server import start
from amsdal_utils.lifecycle.consumer import LifecycleConsumer
from amsdal_utils.lifecycle.enum import LifecycleEvent
from amsdal_utils.lifecycle.producer import LifecycleProducer

from amsdal_cli.app import app
from amsdal_cli.commands.generate.enums import SOURCES_DIR
from amsdal_cli.commands.serve.services.supervisor import Supervisor
from amsdal_cli.commands.serve.utils import build_app_and_migrate
from amsdal_cli.commands.serve.utils import cleanup_app
from amsdal_cli.utils.cli_config import CliConfig


@app.command(name='serve')
def serve_command(
    ctx: typer.Context,
    *,
    cleanup: bool = typer.Option(
        False,
        help='Cleanup the generated models, warehouse and files after stopping',
    ),
    config: Optional[Path] = typer.Option(None, help='Path to custom config.yml file'),  # noqa: B008, UP007
    host: str = typer.Option('0.0.0.0', help='Host to run the server on'),  # noqa: S104
    port: Optional[int] = typer.Option(None, help='Port to run the server on'),  # noqa: UP007
    auto_reload: bool = typer.Option(
        True,
        help='Enable auto-reload of the server when files change',
    ),
    apply_migrations: bool = typer.Option(
        True,
        help='Apply migrations and fixtures to the database',
    ),
) -> None:
    """
    Build the app and generate the models and other files.
    """
    cli_config: CliConfig = ctx.meta['config']
    app_source_path = cli_config.app_directory / SOURCES_DIR
    server_port = port or cli_config.http_port

    if auto_reload:
        supervisor = Supervisor(
            app_source_path=app_source_path,
            output_path=cli_config.app_directory,
            config_path=config or cli_config.config_path,
            host=host,
            port=server_port,
            apply_migrations=apply_migrations,
        )
        try:
            supervisor.run()
        finally:
            supervisor.wait()

            if cleanup:
                cleanup_app(output_path=cli_config.app_directory)

    else:
        amsdal_manager = build_app_and_migrate(
            output_path=cli_config.app_directory,
            app_source_path=app_source_path,
            config_path=config or cli_config.config_path,
            apply_migrations=apply_migrations,
            apply_fixtures=apply_migrations,
        )
        amsdal_manager.build_static_files(app_source_path)
        amsdal_manager.build_transactions(app_source_path)

        class AmsdalInitConsumer(LifecycleConsumer):
            def on_event(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
                if not amsdal_manager._is_setup:
                    amsdal_manager.setup()

                if not amsdal_manager.is_authenticated:
                    amsdal_manager.authenticate()

                amsdal_manager.init_classes()
                amsdal_manager.init_class_versions(create_tables=True)

                migration_manager = MigrationManager(
                    schema_manager=amsdal_manager._schema_manager,
                    table_schema_manager=amsdal_manager._table_schemas_manager,
                    class_manager=amsdal_manager._class_manager,
                )

                migration_manager.refresh_state_db()

        LifecycleProducer.add_listener(
            LifecycleEvent.ON_SERVER_STARTUP,
            AmsdalInitConsumer,
            insert_first=True,
        )
        start(
            is_development_mode=False,
            host=host,
            port=server_port,
        )
