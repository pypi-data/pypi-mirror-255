import typer

from amsdal_cli.commands.generate.app import sub_app
from amsdal_cli.commands.generate.enums import ModifierName
from amsdal_cli.commands.generate.utils.build_base_path import build_model_base_path
from amsdal_cli.utils.cli_config import CliConfig
from amsdal_cli.utils.copier import copy_blueprint


@sub_app.command(name='modifier')
def generate_modifier(
    ctx: typer.Context,
    modifier_name: ModifierName = typer.Argument(  # noqa: B008
        ...,
        help='The modifier name.',
    ),
    model: str = typer.Option(..., help='The model name. It should be provided in PascalCase.'),
) -> None:
    """
    Generates modifier file for specified model.
    """
    cli_config: CliConfig = ctx.meta['config']
    base_path = build_model_base_path(ctx, model)
    modifier_path = base_path / 'modifiers'

    copy_blueprint(
        source_file_path=cli_config.templates_path / 'modifier' / f'{modifier_name.value}.pyt',
        destination_path=modifier_path,
        destination_name=f'{modifier_name.value}.py',
        context={},
        confirm_overwriting=True,
    )
