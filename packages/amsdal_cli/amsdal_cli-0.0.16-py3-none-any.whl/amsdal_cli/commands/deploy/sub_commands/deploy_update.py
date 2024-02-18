import datetime
import json
from pathlib import Path

from amsdal.manager import AmsdalManager
from amsdal_utils.config.manager import AmsdalConfigManager
from rich import print
from rich.table import Table

from amsdal_cli.commands.deploy.app import sub_app
from amsdal_cli.commands.deploy.enums import OutputFormat


@sub_app.command(name='update')
def update_command(deployment_id: str, output: OutputFormat = OutputFormat.DEFAULT) -> None:
    """
    Update the app status.
    """
    AmsdalConfigManager().load_config(Path('./config.yml'))
    manager = AmsdalManager()
    manager.authenticate()
    deployment = manager.update_deployment_status(deployment_id)

    if deployment:
        if output == OutputFormat.JSON:
            print(json.dumps(deployment.dict(), indent=4))
        else:
            data_table = Table()

            data_table.add_column('Deploy ID', justify='center')
            data_table.add_column('Status', justify='center')
            data_table.add_column('Updated', justify='center')

            if output == OutputFormat.WIDE:
                data_table.add_column('Created At', justify='center')
                data_table.add_column('Last Update At', justify='center')

            updated_str = 'true' if deployment.updated else 'false'

            if output == OutputFormat.WIDE:
                data_table.add_row(
                    deployment.deployment_id,
                    deployment.status,
                    updated_str,
                    datetime.datetime.fromtimestamp(
                        deployment.created_at / 1000,
                        tz=datetime.timezone.utc,
                    ).strftime('%Y-%m-%d %H:%M:%S %Z'),
                    datetime.datetime.fromtimestamp(
                        deployment.last_update_at / 1000,
                        tz=datetime.timezone.utc,
                    ).strftime('%Y-%m-%d %H:%M:%S %Z'),
                )
            else:
                data_table.add_row(
                    deployment.deployment_id,
                    deployment.status,
                    updated_str,
                )

            print(data_table)
