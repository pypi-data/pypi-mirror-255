from pathlib import Path
from typing import Any

from pydantic import BaseModel


class VerifyError(BaseModel):
    file_path: Path
    message: str
    details: Any
