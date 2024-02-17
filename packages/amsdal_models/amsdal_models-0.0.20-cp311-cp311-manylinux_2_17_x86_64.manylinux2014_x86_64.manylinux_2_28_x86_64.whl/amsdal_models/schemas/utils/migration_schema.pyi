from amsdal_models.classes.model import Model as Model
from amsdal_models.schemas.data_models.schema import ObjectSchema as ObjectSchema, PropertyData as PropertyData
from amsdal_models.schemas.enums import CoreTypes as CoreTypes
from amsdal_utils.models.data_models.table_schema import TableColumnSchema, TableSchema

def object_schema_to_table_schema(object_schema: ObjectSchema) -> TableSchema:
    """
    Convert ObjectSchema to TableSchema.

    :param object_schema: ObjectSchema object
    :type object_schema: ObjectSchema
    :return: TableSchema object
    :rtype: TableSchema
    """
def _process_properties(properties: dict[str, PropertyData] | None, required: list[str]) -> list[TableColumnSchema]: ...
def _process_property_type(property_type: str) -> type | Model: ...
