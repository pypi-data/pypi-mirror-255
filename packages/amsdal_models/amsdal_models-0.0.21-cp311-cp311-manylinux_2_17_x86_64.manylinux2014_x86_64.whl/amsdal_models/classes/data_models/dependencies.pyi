from amsdal_models.enums import BaseClasses as BaseClasses, MetaClasses as MetaClasses
from amsdal_models.schemas.data_models.schema import ObjectSchema as ObjectSchema
from amsdal_models.schemas.manager import BuildSchemasManager as BuildSchemasManager
from pydantic import BaseModel
from typing import Any

class DependencyModelNames(BaseModel):
    type_model_names: list[str]
    core_model_names: list[str]
    contrib_model_names: list[str]
    user_model_names: list[str]
    reference_model_names: list[str]
    @classmethod
    def build_from_schemas_manager(cls, schemas_manager: BuildSchemasManager) -> DependencyModelNames: ...
    @classmethod
    def build_from_database(cls) -> DependencyModelNames: ...

class DependencyItem(BaseModel):
    module: tuple[str | None, str]
    def __eq__(self, other: Any) -> bool: ...
    def __hash__(self): ...
