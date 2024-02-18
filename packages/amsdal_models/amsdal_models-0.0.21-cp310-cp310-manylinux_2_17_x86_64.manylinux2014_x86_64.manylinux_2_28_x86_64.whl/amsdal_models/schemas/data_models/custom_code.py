import re
from typing import Annotated

from pydantic import BaseModel
from pydantic import Field


class CustomCodeSchema(BaseModel):
    name: Annotated[str, Field(..., min_length=1, max_length=255)]
    code: str

    @property
    def property_names(self) -> list[str]:
        return re.findall('@property.*?def (.*?)\\(', self.code, re.DOTALL)
