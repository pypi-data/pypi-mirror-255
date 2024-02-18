from amsdal_utils.models.base import ModelBase
from amsdal_utils.models.enums import SchemaTypes as SchemaTypes
from typing import ClassVar

class BaseModel(ModelBase):
    schema_type: ClassVar[SchemaTypes]
    class_fingerprint: ClassVar[str]
