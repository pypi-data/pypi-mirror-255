from amsdal_models.errors import AmsdalValidationError as AmsdalValidationError
from amsdal_models.schemas.data_models.core import DictSchema as DictSchema, LegacyDictSchema as LegacyDictSchema, TypeData as TypeData
from amsdal_models.schemas.data_models.schema import ObjectSchema as ObjectSchema
from amsdal_models.schemas.enums import CoreTypes as CoreTypes

class CheckDependenciesMixin:
    def check_dependencies(self, type_schemas: list[ObjectSchema], core_schemas: list[ObjectSchema], contrib_schemas: list[ObjectSchema], user_schemas: list[ObjectSchema]) -> None: ...
    @staticmethod
    def get_dependency_type_names(schema: ObjectSchema) -> set[str]: ...
