import importlib
from types import ModuleType
from typing import Any

from pydantic import Field
from pydantic import field_validator
from pydantic_settings import BaseSettings
from pydantic_settings import SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(case_sensitive=True)

    COMMANDS: list[str] = Field(
        default=[
            'amsdal_cli.commands.new',
            'amsdal_cli.commands.generate',
            'amsdal_cli.commands.verify',
            'amsdal_cli.commands.build',
            'amsdal_cli.commands.serve',
            'amsdal_cli.commands.migrate',
            'amsdal_cli.commands.deploy',
            'amsdal_cli.commands.restore',
        ]
    )

    @field_validator('COMMANDS')
    @classmethod
    def load_commands(cls, value: list[Any]) -> list[ModuleType]:
        commands: list[ModuleType] = []

        for module in value:
            if isinstance(module, str):
                commands.append(importlib.import_module(f'{module}.command'))

        return commands


settings = Settings()
