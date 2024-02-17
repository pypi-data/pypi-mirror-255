from amsdal_models.errors import AmsdalValidationError as AmsdalValidationError
from amsdal_models.schemas.data_models.schema import ObjectSchema as ObjectSchema
from amsdal_models.schemas.utils.merger import merge_schema as merge_schema
from typing import Any

class EnrichSchemasMixin:
    def enrich_configs(self, type_schemas: list[ObjectSchema], core_schemas: list[ObjectSchema], contrib_schemas: list[ObjectSchema], user_schemas: list[ObjectSchema]) -> tuple[list[ObjectSchema], list[ObjectSchema], list[ObjectSchema], list[ObjectSchema]]: ...
    def _enrich(self, type_schemas: list[ObjectSchema], schemas: list[ObjectSchema], extra_schemas: list[ObjectSchema] | None = ...) -> list[ObjectSchema]: ...
    @staticmethod
    def _decode_json(json_string: str) -> dict[str, Any]: ...
