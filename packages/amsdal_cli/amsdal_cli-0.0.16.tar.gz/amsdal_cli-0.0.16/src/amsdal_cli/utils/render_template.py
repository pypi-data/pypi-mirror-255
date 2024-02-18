from pathlib import Path
from typing import Any

from jinja2 import Environment
from jinja2 import FileSystemLoader


def render(template_path: Path, context: dict[str, Any]) -> str:
    env = Environment(loader=FileSystemLoader(template_path.parent))  # noqa: S701
    template = env.get_template(template_path.name)

    return template.render({'ctx': context})
