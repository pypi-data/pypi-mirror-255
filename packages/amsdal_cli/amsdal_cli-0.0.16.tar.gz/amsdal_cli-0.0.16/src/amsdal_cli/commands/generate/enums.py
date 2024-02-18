from enum import Enum

SOURCES_DIR = 'src'
MODEL_JSON_FILE = 'model.json'
MODEL_PY_FILE = 'model.py'
FIXTURES_JSON_FILE = 'fixtures.json'


class HookName(str, Enum):
    PRE_INIT = 'pre_init'
    POST_INIT = 'post_init'
    PRE_CREATE = 'pre_create'
    POST_CREATE = 'post_create'
    PRE_UPDATE = 'pre_update'
    POST_UPDATE = 'post_update'
    PRE_DELETE = 'pre_delete'
    POST_DELETE = 'post_delete'


class ModifierName(str, Enum):
    CONSTRUCTOR = 'constructor'
    DISPLAY_NAME = 'display_name'
    VERSION_NAME = 'version_name'


class ModelFormat(str, Enum):
    JSON = 'json'
    PY = 'py'


class AttributeType(str, Enum):
    STRING = 'string'
    NUMBER = 'number'
    BOOLEAN = 'boolean'
    BELONGS_TO = 'belongs-to'
    HAS_MANY = 'has-many'
    DICT = 'dict'


class JsonType(str, Enum):
    STRING = 'string'
    NUMBER = 'number'
    BOOLEAN = 'boolean'
    ARRAY = 'array'
    DICT = 'dictionary'


class OptionName(str, Enum):
    INDEX = 'index'
    DEFAULT = 'default'
    REQUIRED = 'required'
    UNIQUE = 'unique'
