from collections.abc import Callable
from collections.abc import Iterator
from pathlib import Path
from typing import Any

import typer

from amsdal_cli.utils.render_template import render

TEMPLATE_EXTENSIONS = {
    '.pyt': '.py',
}


def copy_blueprints_from_directory(
    source_path: Path,
    destination_path: Path,
    context: dict[str, Any],
) -> None:
    for file in walk(source_path):
        file_path = file.relative_to(source_path)
        destination_file_path = destination_path / _normalize_destination_file_ext(file_path)
        destination_file_path.parent.mkdir(parents=True, exist_ok=True)
        destination_file_path.write_text(render(file, context))


def copy_blueprint(
    source_file_path: Path,
    destination_path: Path,
    context: dict[str, Any],
    destination_name: str | None = None,
    *,
    confirm_overwriting: bool = True,
) -> None:
    destination_name = destination_name or source_file_path.name
    destination_file_path = destination_path / _normalize_destination_file_ext(Path(destination_name))

    write_file(
        render(source_file_path, context),
        destination_file_path,
        confirm_overwriting=confirm_overwriting,
    )


def write_file(
    content: str,
    destination_file_path: Path,
    *,
    confirm_overwriting: bool = True,
) -> None:
    if (
        destination_file_path.exists()
        and confirm_overwriting
        and not typer.confirm(
            f'The file "{destination_file_path.resolve()}" already exists. Would you like to overwrite it?',
        )
    ):
        raise typer.Exit

    destination_file_path.parent.mkdir(parents=True, exist_ok=True)
    destination_file_path.write_text(content)


def append_to_file(
    target_file: Path,
    destination_file: Path,
    transform: Callable[[str], str] | None = None,
) -> None:
    destination_file.parent.mkdir(parents=True, exist_ok=True)
    is_destination_exists = destination_file.exists()

    with (
        target_file.open('rt') as _target_file,
        destination_file.open('at') as _destination_file,
    ):
        if is_destination_exists:
            _destination_file.write('\n')

        content = _target_file.read()

        if transform:
            content = transform(content)

        _destination_file.write(content)
        _destination_file.write('\n')


def walk(path: Path) -> Iterator[Any]:
    if not path.exists():
        return

    for item in path.iterdir():
        if item.is_dir():
            yield from walk(item)
            continue
        yield item


def _normalize_destination_file_ext(file_name: Path) -> Path:
    for ext_tmpl, ext in TEMPLATE_EXTENSIONS.items():
        if file_name.name.endswith(ext_tmpl):
            return file_name.with_name(file_name.name.replace(ext_tmpl, ext))
    return file_name
