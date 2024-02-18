from pathlib import Path

from amsdal_utils.models.enums import SchemaTypes
from pydantic import BaseModel


class SchemasDirectory(BaseModel):
    path: Path
    schema_type: SchemaTypes
