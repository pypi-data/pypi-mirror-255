import typer

from amsdal_cli.commands.callbacks import init_app_context

app = typer.Typer(
    name='amsdal',
    callback=init_app_context,
    invoke_without_command=True,
)
