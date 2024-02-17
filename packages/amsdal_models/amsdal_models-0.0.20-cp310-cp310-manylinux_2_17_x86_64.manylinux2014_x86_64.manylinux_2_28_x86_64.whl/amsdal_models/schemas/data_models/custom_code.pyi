from pydantic import BaseModel, Field as Field
from typing import Annotated

class CustomCodeSchema(BaseModel):
    name: Annotated[str, None]
    code: str
    @property
    def property_names(self) -> list[str]: ...
