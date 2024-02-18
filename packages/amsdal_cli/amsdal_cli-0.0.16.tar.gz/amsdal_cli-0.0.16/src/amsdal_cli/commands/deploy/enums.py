from enum import Enum


class OutputFormat(str, Enum):
    """
    Output format for CLI commands.
    """

    DEFAULT = 'default'
    JSON = 'json'
    WIDE = 'wide'


class DeployType(str, Enum):
    LAKEHOUSE_ONLY = 'lakehouse_only'
    INCLUDE_STATE_DB = 'include_state_db'


class StateOption(str, Enum):
    SQLITE = 'sqlite'
    POSTGRES = 'postgres'


class LakehouseOption(str, Enum):
    SPARK = 'spark'
    POSTGRES = 'postgres'
