import json
import typing_extensions
from _typeshed import Incomplete
from amsdal_models.classes.base import BaseModel as BaseModel
from amsdal_models.classes.errors import ObjectAlreadyExistsError as ObjectAlreadyExistsError
from amsdal_models.classes.handlers.reference_handler import ReferenceHandler as ReferenceHandler
from amsdal_models.classes.mixins.model_hooks_mixin import ModelHooksMixin as ModelHooksMixin
from amsdal_models.managers.base_manager import BaseManager as BaseManager
from pydantic._internal._model_construction import ModelMetaclass
from typing import Any, ClassVar, Literal

IncEx: typing_extensions.TypeAlias
logger: Incomplete

class TypeModel(ModelHooksMixin, ReferenceHandler, BaseModel):
    @classmethod
    def convert_string_to_dict(cls, data: Any) -> Any: ...

class AmsdalModelMetaclass(ModelMetaclass):
    def __new__(mcs, cls_name: str, bases: tuple[type[Any], ...], namespace: dict[str, Any], *args: Any, **kwargs: Any) -> type: ...

class Model(TypeModel, metaclass=AmsdalModelMetaclass):
    """
    Base class for all model classes.
    """
    model_config: Incomplete
    objects: ClassVar[BaseManager]
    def __init__(self, **kwargs: Any) -> None:
        """
        Initializes the Model object. This method first calls the pre_init() hook, then calls the __init__() method
        of the parent class, and finally calls the post_init() hook.

        :param kwargs: The data to initialize the Model object with.
        """
    _is_new_object: bool
    def save(self, *, force_insert: bool = ..., using: str | None = ...) -> Model:
        """
        This method is used to save the record of Model object into the database.
        By default, the object will be updated in the database if it already exists.
        If force_insert is set to True, the object will be inserted into the database even if it already exists,
        which may result in an ObjectAlreadyExistsError.

        The method first checks if force_insert is True, and if the object already exists in the database.
        If it does, it raises an ObjectAlreadyExistsError.

        Then, depending on the object existence, the method either creates a new record in the database or updates
        the existing record. It also will trigger corresponding pre_create(), post_create() or pre_update() and
        post_update() hooks.

        Finally, the method returns the saved Model object.

        :param force_insert: A boolean indicating whether to force insert the object into the database,
                             even if it already exists.
        :return: The saved Model object.
        """
    def delete(self, using: str | None = ...) -> None:
        """
        This method is used to delete the existing record of Model object from the database. This method first
        calls the pre_delete() method, then deletes the record from the database by calling the _delete() method,
        and finally calls the post_delete() method. It changes the flag is_deleted to True in the metadata of the
        record.

        It does not return anything.

        :param using: The name of the database to use.
        :type using: str | None

        :return: None
        """
    @property
    def display_name(self) -> str:
        """
        This method is used to get the display name of the Model object. It returns the string representation of the
        object's address.

        :return: The display name of the Model object.
        :rtype: str
        """
    def _create(self, using: str | None) -> None: ...
    def _update(self, using: str | None) -> None: ...
    def _process_nested_objects(self) -> None: ...
    def _process_nested_field(self, field_value: Any) -> Any: ...
    def model_dump_refs(self, *, mode: Literal['json', 'python'] | str = ..., include: IncEx = ..., exclude: IncEx = ..., by_alias: bool = ..., exclude_unset: bool = ..., exclude_defaults: bool = ..., exclude_none: bool = ..., round_trip: bool = ..., warnings: bool = ...) -> dict[str, Any]:
        """
        This method is used to dump the record and it's references into a dictionary of data.

        :param mode: The mode in which `to_python` should run. If mode is 'json', the dictionary will only contain JSON
        serializable types. If mode is 'python', the dictionary may contain any Python objects.
        :type mode: Literal['json', 'python'] | str
        :param include: A list of fields to include in the output.
        :type include: set[int] | set[str] | dict[int, Any] | dict[str, Any] | None
        :param exclude: A list of fields to exclude from the output.
        :type exclude: set[int] | set[str] | dict[int, Any] | dict[str, Any] | None
        :param by_alias: Whether to use the field's alias in the dictionary key if defined.
        :type by_alias: bool
        :param exclude_unset: Whether to exclude fields that are unset or None from the output.
        :type exclude_unset: bool
        :param exclude_defaults: Whether to exclude fields that are set to their default value from the output.
        :type exclude_defaults: bool
        :param exclude_none: Whether to exclude fields that have a value of `None` from the output.
        :type exclude_none: bool
        :param round_trip: Whether to enable serialization and deserialization round-trip support.
        :type round_trip: bool
        :param warnings: Whether to log warnings when invalid fields are encountered.
        :type warnings: bool
        :return: A dictionary representation of the model.
        :rtype: dict[str, Any]
        """
    def model_dump(self, *, mode: Literal['json', 'python'] | str = ..., include: IncEx = ..., exclude: IncEx = ..., by_alias: bool = ..., exclude_unset: bool = ..., exclude_defaults: bool = ..., exclude_none: bool = ..., round_trip: bool = ..., warnings: bool = ...) -> dict[str, Any]:
        '''
        This method is used to dump the record dictionary of data, although the referenced objects will be represented
        in reference format. Here is example of reference format:

        >>> {
        >>>   "$ref": {
        >>>     "resource": "sqlite",
        >>>     "class_name": "Person",
        >>>     "class_version": "1234",
        >>>     "object_id": "4567",
        >>>     "object_version": "8901"
        >>>   }
        >>> }

        :param mode: The mode in which `to_python` should run. If mode is \'json\', the dictionary will only contain
        JSON serializable types. If mode is \'python\', the dictionary may contain any Python objects.
        :type mode: Literal[\'json\', \'python\'] | str
        :param include: A list of fields to include in the output.
        :type include: set[int] | set[str] | dict[int, Any] | dict[str, Any] | None
        :param exclude: A list of fields to exclude from the output.
        :type exclude: set[int] | set[str] | dict[int, Any] | dict[str, Any] | None
        :param by_alias: Whether to use the field\'s alias in the dictionary key if defined.
        :type by_alias: bool
        :param exclude_unset: Whether to exclude fields that are unset or None from the output.
        :type exclude_unset: bool
        :param exclude_defaults: Whether to exclude fields that are set to their default value from the output.
        :type exclude_defaults: bool
        :param exclude_none: Whether to exclude fields that have a value of `None` from the output.
        :type exclude_none: bool
        :param round_trip: Whether to enable serialization and deserialization round-trip support.
        :type round_trip: bool
        :param warnings: Whether to log warnings when invalid fields are encountered.
        :type warnings: bool
        :return: A dictionary representation of the model.
        :rtype: dict[str, Any]
        '''
    def model_dump_json_refs(self, *, indent: int | None = ..., include: IncEx = ..., exclude: IncEx = ..., by_alias: bool = ..., exclude_unset: bool = ..., exclude_defaults: bool = ..., exclude_none: bool = ..., round_trip: bool = ..., warnings: bool = ...) -> str:
        """
        Similar to model_dump_refs, but returns a JSON string instead of a dictionary.

        :param indent: Indentation to use in the JSON output. If None is passed, the output will be compact.
        :type indent: int | None
        :param include: A list of fields to include in the output.
        :type include: set[int] | set[str] | dict[int, Any] | dict[str, Any] | None
        :param exclude: A list of fields to exclude from the output.
        :type exclude: set[int] | set[str] | dict[int, Any] | dict[str, Any] | None
        :param by_alias: Whether to use the field's alias in the dictionary key if defined.
        :type by_alias: bool
        :param exclude_unset: Whether to exclude fields that are unset or None from the output.
        :type exclude_unset: bool
        :param exclude_defaults: Whether to exclude fields that are set to their default value from the output.
        :type exclude_defaults: bool
        :param exclude_none: Whether to exclude fields that have a value of `None` from the output.
        :type exclude_none: bool
        :param round_trip: Whether to enable serialization and deserialization round-trip support.
        :type round_trip: bool
        :param warnings: Whether to log warnings when invalid fields are encountered.
        :type warnings: bool
        :return: A JSON string representation of the model.
        :rtype: str
        """
    def model_dump_json(self, *, indent: int | None = ..., include: IncEx = ..., exclude: IncEx = ..., by_alias: bool = ..., exclude_unset: bool = ..., exclude_defaults: bool = ..., exclude_none: bool = ..., round_trip: bool = ..., warnings: bool = ...) -> str:
        """
        Similar to model_dump, but returns a JSON string instead of a dictionary.

        :param indent: Indentation to use in the JSON output. If None is passed, the output will be compact.
        :type indent: int | None
        :param include: A list of fields to include in the output.
        :type include: set[int] | set[str] | dict[int, Any] | dict[str, Any] | None
        :param exclude: A list of fields to exclude from the output.
        :type exclude: set[int] | set[str] | dict[int, Any] | dict[str, Any] | None
        :param by_alias: Whether to use the field's alias in the dictionary key if defined.
        :type by_alias: bool
        :param exclude_unset: Whether to exclude fields that are unset or None from the output.
        :type exclude_unset: bool
        :param exclude_defaults: Whether to exclude fields that are set to their default value from the output.
        :type exclude_defaults: bool
        :param exclude_none: Whether to exclude fields that have a value of `None` from the output.
        :type exclude_none: bool
        :param round_trip: Whether to enable serialization and deserialization round-trip support.
        :type round_trip: bool
        :param warnings: Whether to log warnings when invalid fields are encountered.
        :type warnings: bool
        :return: A JSON string representation of the model.
        :rtype: str
        """

class LegacyModel(TypeModel, metaclass=AmsdalModelMetaclass):
    model_config: Incomplete
