from amsdal_cli.app import app
from amsdal_cli.commands.deploy.app import sub_app
from amsdal_cli.commands.deploy.sub_commands import *  # noqa

app.add_typer(sub_app, name='deploy')
