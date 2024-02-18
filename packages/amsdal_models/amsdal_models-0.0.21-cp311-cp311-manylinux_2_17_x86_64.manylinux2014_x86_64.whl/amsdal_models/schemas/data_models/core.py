from typing import Any
from typing import Union

from pydantic import BaseModel


class DictSchema(BaseModel):
    key: 'TypeData'
    value: 'TypeData'


class LegacyDictSchema(BaseModel):
    key_type: str
    value_type: str


class TypeData(BaseModel):
    type: str
    items: Union['TypeData', DictSchema, LegacyDictSchema] | None = None
    default: Any = None
