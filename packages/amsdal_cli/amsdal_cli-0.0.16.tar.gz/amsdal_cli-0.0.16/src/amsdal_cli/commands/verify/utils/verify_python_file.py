import ast
import traceback
from pathlib import Path

from amsdal_cli.commands.verify.models import VerifyError


def verify_python_file(python_file: Path) -> list[VerifyError]:
    try:
        with python_file.open('rt') as _file:
            ast.parse(_file.read())
    except Exception as ex:
        return [
            VerifyError(
                file_path=python_file,
                message='Cannot parse PY file',
                details=f'{ex}: {traceback.format_exc()}',
            ),
        ]

    return []
