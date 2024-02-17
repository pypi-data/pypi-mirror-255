from _typeshed import Incomplete
from amsdal_models.classes.builder.ast_generator.data_models import CustomCodeAst as CustomCodeAst, NestedPropertyTypeAst as NestedPropertyTypeAst, PropertyAst as PropertyAst, PropertyValueAst as PropertyValueAst
from amsdal_models.classes.builder.ast_generator.dependency_generator import AstDependencyGenerator as AstDependencyGenerator
from amsdal_models.classes.builder.ast_generator.helpers.build_assign_node import build_assign_node as build_assign_node
from amsdal_models.classes.builder.ast_generator.helpers.build_validator_node import build_validator_node as build_validator_node
from amsdal_models.classes.builder.validator_resolver import ValidatorResolver as ValidatorResolver
from amsdal_models.classes.constants import BASE_OBJECT_TYPE as BASE_OBJECT_TYPE
from amsdal_models.classes.data_models.dependencies import DependencyModelNames as DependencyModelNames
from amsdal_models.classes.model import Model as Model, TypeModel as TypeModel
from amsdal_models.schemas.data_models.core import TypeData as TypeData
from amsdal_models.schemas.data_models.schema import PropertyData as PropertyData
from amsdal_utils.models.enums import SchemaTypes

class AstClassGenerator:
    _base_class: Incomplete
    _class_definition: Incomplete
    _ast_dependency_generator: Incomplete
    def __init__(self, models_module_name: str, base_class: type[Model | TypeModel], model_names: DependencyModelNames) -> None:
        '''
        Builds AST for class definition.
        :param models_module_name: The name of the module where models are located, usually it has "models" value.
        :param base_class: The base class for the class definition.
        It will be used in case the model\'s type is "object".
        :param model_names: All available model names.
        '''
    def register_class(self, class_name: str, extend_type: str) -> None: ...
    def add_class_data(self, schema_type: SchemaTypes, class_fingerprint: str): ...
    def add_class_property(self, property_name: str, property_config: PropertyData, *, is_required: bool) -> None: ...
    def add_properties_validators(self, property_name: str, property_config: PropertyData) -> None: ...
    def add_class_custom_code(self, custom_code: str) -> None: ...
    @property
    def model_source(self) -> str: ...
    @property
    def dependencies_source(self) -> str: ...
