from typing import Annotated
from typing import Any

from pydantic import BaseModel
from pydantic import Field

from amsdal_models.enums import MetaClasses
from amsdal_models.schemas.data_models.core import TypeData


class OptionItemData(BaseModel):
    key: str
    value: Any


class PropertyData(TypeData, extra='allow'):
    title: str | None = None
    options: list[OptionItemData] | None = None
    read_only: bool = False


class ObjectSchema(BaseModel, extra='allow'):
    title: Annotated[str, Field(..., min_length=1, max_length=255)]
    type: str = 'object'
    required: Annotated[list[str], Field(default_factory=list)]
    default: Any = None
    properties: dict[str, PropertyData] | None = None
    options: list[OptionItemData] | None = None
    meta_class: str = MetaClasses.CLASS_OBJECT.value
    custom_code: str | None = None

    def __hash__(self) -> int:
        return hash(f'{self.title}::{self.type}')
