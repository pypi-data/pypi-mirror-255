from _typeshed import Incomplete
from amsdal_models.classes.base import BaseModel as BaseModel
from amsdal_models.classes.decorators.private_property import PrivateProperty as PrivateProperty
from amsdal_models.classes.utils import build_class_schema_reference as build_class_schema_reference
from amsdal_utils.models.data_models.metadata import Metadata
from amsdal_utils.utils.lazy_object import LazyObject
from typing import Any, ClassVar

logger: Incomplete

class MetadataHandler(BaseModel):
    _class_address: ClassVar[str]
    _object_id: str
    _object_version: str
    _metadata_lazy: LazyObject[Metadata]
    def __init__(self, **kwargs: Any) -> None: ...
    def _metadata(self) -> Metadata: ...
    def build_metadata(self) -> Metadata: ...
    def get_metadata(self) -> Metadata:
        """
        Returns the metadata object for this record.

        :return: Metadata object
        :rtype: Metadata
        """
