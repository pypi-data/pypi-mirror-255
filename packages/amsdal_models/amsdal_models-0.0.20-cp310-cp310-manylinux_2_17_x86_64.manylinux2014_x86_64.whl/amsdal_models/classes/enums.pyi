from amsdal_models.enums import MetaClasses as MetaClasses
from amsdal_models.schemas.data_models.schema import ObjectSchema as ObjectSchema
from enum import Enum

class CoreModules(str, Enum):
    REFERENCE: str

class SystemModules(str, Enum):
    DICT: str
    LIST: str
    ANY: str
    TYPE: str
    OPTIONAL: str
    UNION: str
    CLASS_VAR: str
    FIELD_VALIDATOR: str
    FIELD_DICTIONARY_VALIDATOR: str
    FIELD_OPTIONS_VALIDATOR: str

class ModelType(str, Enum):
    TYPE: str
    MODEL: str
    @classmethod
    def from_schema(cls, schema: ObjectSchema) -> ModelType: ...
