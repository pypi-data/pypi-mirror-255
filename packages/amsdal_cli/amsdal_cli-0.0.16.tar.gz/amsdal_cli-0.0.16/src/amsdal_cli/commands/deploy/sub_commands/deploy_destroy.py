from pathlib import Path

from amsdal.manager import AmsdalManager
from amsdal_utils.config.manager import AmsdalConfigManager

from amsdal_cli.commands.deploy.app import sub_app


@sub_app.command(name='destroy')
def destroy_command(deployment_id: str) -> None:
    """
    Destroy the app on the server.
    """
    AmsdalConfigManager().load_config(Path('./config.yml'))
    manager = AmsdalManager()
    manager.authenticate()
    manager.destroy_deployment(deployment_id)
