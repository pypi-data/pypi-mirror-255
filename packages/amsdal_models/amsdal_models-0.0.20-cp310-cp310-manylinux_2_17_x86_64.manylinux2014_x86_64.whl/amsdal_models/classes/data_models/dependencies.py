import json
from typing import Any

from amsdal_utils.models.enums import SchemaTypes
from pydantic import BaseModel
from pydantic import Field

from amsdal_models.enums import BaseClasses
from amsdal_models.enums import MetaClasses
from amsdal_models.schemas.data_models.schema import ObjectSchema
from amsdal_models.schemas.manager import BuildSchemasManager


class DependencyModelNames(BaseModel):
    type_model_names: list[str] = Field(default_factory=list)
    core_model_names: list[str] = Field(default_factory=list)
    contrib_model_names: list[str] = Field(default_factory=list)
    user_model_names: list[str] = Field(default_factory=list)
    reference_model_names: list[str] = Field(default_factory=list)

    @classmethod
    def build_from_schemas_manager(cls, schemas_manager: BuildSchemasManager) -> 'DependencyModelNames':
        return cls(
            type_model_names=[schema.title for schema in schemas_manager.type_schemas],
            core_model_names=[schema.title for schema in schemas_manager.core_schemas],
            contrib_model_names=[schema.title for schema in schemas_manager.contrib_schemas],
            user_model_names=[schema.title for schema in schemas_manager.user_schemas],
            reference_model_names=[
                *[
                    _schema.title
                    for _schema in schemas_manager.core_schemas
                    if _schema.meta_class == MetaClasses.CLASS_OBJECT.value
                ],
                *[
                    _schema.title
                    for _schema in schemas_manager.contrib_schemas
                    if _schema.meta_class == MetaClasses.CLASS_OBJECT.value
                ],
                *[
                    _schema.title
                    for _schema in schemas_manager.user_schemas
                    if _schema.meta_class == MetaClasses.CLASS_OBJECT.value
                ],
            ],
        )

    @classmethod
    def build_from_database(cls) -> 'DependencyModelNames':
        from models.core.class_object import ClassObject  # type: ignore[import-not-found]
        from models.type.object import Object  # type: ignore[import-not-found]

        objects = Object.objects.all().execute()
        class_objects = ClassObject.objects.all().execute()
        type_names = [obj.title for obj in objects if obj.title != BaseClasses.CLASS_OBJECT.value]
        core_names = [BaseClasses.CLASS_OBJECT.value]
        core_names.extend(
            [obj.title for obj in class_objects if obj.get_metadata().class_schema_type == SchemaTypes.CORE.value]
        )
        contrib_names = [
            obj.title for obj in class_objects if obj.get_metadata().class_schema_type == SchemaTypes.CONTRIB.value
        ]
        user_names = [
            obj.title for obj in class_objects if obj.get_metadata().class_schema_type == SchemaTypes.USER.value
        ]
        reference_model_names = []

        for _obj in class_objects:
            object_schema = ObjectSchema(**json.loads(_obj.class_schema))

            if object_schema.meta_class == MetaClasses.CLASS_OBJECT.value:
                reference_model_names.append(_obj.title)

        return cls(
            type_model_names=type_names,
            core_model_names=core_names,
            contrib_model_names=contrib_names,
            user_model_names=user_names,
            reference_model_names=reference_model_names,
        )


class DependencyItem(BaseModel):
    module: tuple[str | None, str]

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, DependencyItem):
            return self.module == other.module
        return False

    def __hash__(self):
        return hash(self.module)
