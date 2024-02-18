from _typeshed import Incomplete
from amsdal_models.classes.decorators.private_property import PrivateProperty as PrivateProperty
from amsdal_models.classes.handlers.metadata_handler import MetadataHandler as MetadataHandler
from typing import Any

logger: Incomplete

class ObjectIdHandler(MetadataHandler):
    _object_id: str
    _object_version: str
    _is_new_object: bool
    _is_new_object_version: bool
    def __init__(self, **kwargs: Any) -> None: ...
    def object_id(self) -> str:
        """
        Object identifier. This is a unique identifier for the record. This is a UUID.

        :return: UUID string of the object ID
        :rtype: str
        """
    def is_new_object(self) -> bool:
        """
        Returns True if the object is new and has not been saved to the database.

        :return: boolean flag indicating if the object is new
        :rtype: bool
        """
    def object_version(self) -> str:
        """
        Version identifier. This is a unique identifier for the version of the record. This is a UUID.

        :return: UUID string of the version
        :rtype: str
        """
    def is_new_object_version(self) -> bool:
        """
        Returns True if the object version is new and has not been saved to the database yet.

        :return: boolean flag indicating if the object version is new
        :rtype: bool
        """
