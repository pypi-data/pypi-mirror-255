from amsdal_models.schemas.data_models.schema import OptionItemData as OptionItemData
from pydantic import BaseModel, Field as Field
from typing import Annotated

class OptionSchema(BaseModel):
    title: Annotated[str, None]
    values: list[OptionItemData]
