from _typeshed import Incomplete
from amsdal_models.schemas.data_models.schema import ObjectSchema as ObjectSchema
from amsdal_models.schemas.loaders.base import CustomCodeLoaderBase as CustomCodeLoaderBase

logger: Incomplete

class CustomCodeExtender:
    _custom_code_reader: Incomplete
    _custom_code_schemas: Incomplete
    _used_custom_codes: Incomplete
    def __init__(self, custom_code_reader: CustomCodeLoaderBase) -> None: ...
    def extend(self, config: ObjectSchema) -> None: ...
    def post_extend(self) -> None: ...
