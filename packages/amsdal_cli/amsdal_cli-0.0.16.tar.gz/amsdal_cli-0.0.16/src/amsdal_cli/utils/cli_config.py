from pathlib import Path

from pydantic import BaseModel
from pydantic import model_validator


class CliConfig(BaseModel):
    templates_path: Path
    config_path: Path = Path('/dev/null')
    http_port: int = 8080
    check_model_exists: bool = True
    json_indent: int = 4
    app_directory: Path = Path('/dev/null')

    @model_validator(mode='after')
    def validate_config_path(self) -> 'CliConfig':
        if self.app_directory == Path('/dev/null'):
            return self

        full_config_path: Path = self.app_directory / self.config_path
        self.config_path = full_config_path

        if not full_config_path.exists():
            msg = f'The "{full_config_path}" does not exists. Check ".amdsal-cli -> config_path".'
            raise ValueError(msg)

        return self
