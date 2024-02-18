from _typeshed import Incomplete
from amsdal_models.classes.builder.ast_generator.class_generator import AstClassGenerator as AstClassGenerator
from amsdal_models.classes.data_models.dependencies import DependencyModelNames as DependencyModelNames
from amsdal_models.classes.model import Model as Model, TypeModel as TypeModel
from amsdal_models.schemas.data_models.schema import ObjectSchema as ObjectSchema
from amsdal_models.schemas.utils.schema_fingerprint import calculate_schema_fingerprint as calculate_schema_fingerprint
from amsdal_utils.models.enums import SchemaTypes as SchemaTypes
from functools import cached_property as cached_property

class ClassSourceBuilder:
    ast_generator: AstClassGenerator
    _schema: Incomplete
    _schema_type: Incomplete
    _base_class: Incomplete
    def __init__(self, models_module_name: str, schema: ObjectSchema, schema_type: SchemaTypes, base_class: type[Model | TypeModel], model_names: DependencyModelNames) -> None: ...
    @cached_property
    def model_class_source(self) -> str: ...
    @cached_property
    def dependencies_source(self) -> str: ...
    def _build_class_source(self) -> str: ...
