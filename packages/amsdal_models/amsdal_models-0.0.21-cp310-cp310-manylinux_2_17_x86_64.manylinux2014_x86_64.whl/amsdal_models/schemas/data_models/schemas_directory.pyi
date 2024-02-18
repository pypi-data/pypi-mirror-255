from amsdal_utils.models.enums import SchemaTypes as SchemaTypes
from pathlib import Path
from pydantic import BaseModel

class SchemasDirectory(BaseModel):
    path: Path
    schema_type: SchemaTypes
