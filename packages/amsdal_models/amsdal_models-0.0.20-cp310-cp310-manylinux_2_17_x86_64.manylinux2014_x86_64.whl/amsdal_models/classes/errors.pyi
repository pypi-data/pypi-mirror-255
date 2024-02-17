from _typeshed import Incomplete
from amsdal_utils.errors import AmsdalError
from amsdal_utils.models.data_models.address import Address as Address
from amsdal_utils.models.enums import SchemaTypes as SchemaTypes

class ObjectAlreadyExistsError(AmsdalError):
    address: Incomplete
    def __init__(self, address: Address) -> None: ...

class AmsdalClassError(AmsdalError): ...

class AmsdalClassNotFoundError(AmsdalClassError):
    model_name: Incomplete
    schema_type: Incomplete
    def __init__(self, model_name: str, schema_type: SchemaTypes) -> None: ...
