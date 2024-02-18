from amsdal_models.classes.base import BaseModel as BaseModel
from amsdal_models.classes.constants import CONTRIB_MODELS_MODULE as CONTRIB_MODELS_MODULE, CORE_MODELS_MODULE as CORE_MODELS_MODULE, TYPE_MODELS_MODULE as TYPE_MODELS_MODULE, USER_MODELS_MODULE as USER_MODELS_MODULE
from amsdal_models.classes.decorators.private_property import PrivateProperty as PrivateProperty
from amsdal_models.classes.model import Model as Model, TypeModel as TypeModel
from amsdal_models.enums import BaseClasses as BaseClasses, MetaClasses as MetaClasses
from amsdal_models.schemas.data_models.schema import ObjectSchema as ObjectSchema
from amsdal_utils.models.base import ModelBase
from amsdal_utils.models.data_models.reference import Reference as Reference
from amsdal_utils.models.enums import SchemaTypes
from typing import Union

def resolve_modes_module(models_module_name: str, schema_type: SchemaTypes) -> str: ...
def resolve_base_class_for_schema(schema: ObjectSchema) -> type[Union['Model', 'TypeModel']]: ...
def build_class_schema_reference(model_class: type[BaseModel]) -> Reference: ...
def get_custom_properties(model: type[ModelBase]) -> set[str]: ...
