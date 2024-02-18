import datetime
import json
from pathlib import Path

from amsdal.manager import AmsdalManager
from amsdal_utils.config.manager import AmsdalConfigManager
from rich import print
from rich.table import Table

from amsdal_cli.commands.deploy.app import sub_app
from amsdal_cli.commands.deploy.enums import OutputFormat


@sub_app.command(name='list')
def list_command(output: OutputFormat = OutputFormat.DEFAULT) -> None:
    """
    List the apps on the server.
    """
    AmsdalConfigManager().load_config(Path('./config.yml'))
    manager = AmsdalManager()
    manager.authenticate()
    list_response = manager.list_deployments()

    if not list_response:
        return

    if output in (OutputFormat.DEFAULT, OutputFormat.WIDE):
        if not list_response.deployments:
            print('No deployments found.')

        else:
            data_table = Table()

            data_table.add_column('Deploy ID', justify='center')
            data_table.add_column('Status', justify='center')

            if output == OutputFormat.WIDE:
                data_table.add_column('Created At', justify='center')
                data_table.add_column('Last Update At', justify='center')

            for deployment in list_response.deployments:
                if output == OutputFormat.WIDE:
                    data_table.add_row(
                        deployment.deployment_id,
                        deployment.status,
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
                    )

            print(data_table)

    else:
        print(json.dumps(list_response.dict(), indent=4))
