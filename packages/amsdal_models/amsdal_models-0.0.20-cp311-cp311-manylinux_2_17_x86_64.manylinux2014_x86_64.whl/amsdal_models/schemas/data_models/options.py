from typing import Annotated

from pydantic import BaseModel
from pydantic import Field

from amsdal_models.schemas.data_models.schema import OptionItemData


class OptionSchema(BaseModel):
    title: Annotated[str, Field(..., min_length=1, max_length=255)]
    values: list[OptionItemData]
