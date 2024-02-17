from amsdal_models.enums import MetaClasses as MetaClasses
from amsdal_models.schemas.data_models.core import TypeData as TypeData
from pydantic import BaseModel, Field as Field
from typing import Annotated, Any

class OptionItemData(BaseModel):
    key: str
    value: Any

class PropertyData(TypeData, extra='allow'):
    title: str | None
    options: list[OptionItemData] | None
    read_only: bool

class ObjectSchema(BaseModel, extra='allow'):
    title: Annotated[str, None]
    type: str
    required: Annotated[list[str], None]
    default: Any
    properties: dict[str, PropertyData] | None
    options: list[OptionItemData] | None
    meta_class: str
    custom_code: str | None
    def __hash__(self) -> int: ...
