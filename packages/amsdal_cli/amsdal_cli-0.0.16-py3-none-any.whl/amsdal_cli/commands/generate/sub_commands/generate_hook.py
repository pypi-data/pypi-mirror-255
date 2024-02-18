import typer

from amsdal_cli.commands.generate.app import sub_app
from amsdal_cli.commands.generate.enums import HookName
from amsdal_cli.commands.generate.utils.build_base_path import build_model_base_path
from amsdal_cli.utils.cli_config import CliConfig
from amsdal_cli.utils.copier import copy_blueprint


@sub_app.command(name='hook')
def generate_hook(
    ctx: typer.Context,
    hook_name: HookName = typer.Argument(  # noqa: B008
        ...,
        help='The hook name.',
    ),
    model: str = typer.Option(..., help='The model name. It should be provided in PascalCase.'),
) -> None:
    """
    Generates hook file for specified model.
    """
    cli_config: CliConfig = ctx.meta['config']
    base_path = build_model_base_path(ctx, model)
    output_path = base_path / 'hooks'

    copy_blueprint(
        source_file_path=cli_config.templates_path / 'hook.pyt',
        destination_path=output_path,
        destination_name=f'{hook_name.value}.py',
        context={
            'hook_name': hook_name.value,
            'is_init': hook_name in (HookName.PRE_INIT, HookName.POST_INIT),
        },
        confirm_overwriting=True,
    )
