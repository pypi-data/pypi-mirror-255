import json
import logging
from typing import Any
from typing import ClassVar
from typing import Literal

import typing_extensions
from amsdal_data.manager import AmsdalDataManager
from amsdal_data.operations.enums import OperationType
from amsdal_data.transactions.decorators import transaction
from pydantic import ConfigDict
from pydantic import Field
from pydantic import model_validator
from pydantic._internal._model_construction import ModelMetaclass
from typing_extensions import dataclass_transform

from amsdal_models.classes.base import BaseModel
from amsdal_models.classes.errors import ObjectAlreadyExistsError
from amsdal_models.classes.handlers.reference_handler import ReferenceHandler
from amsdal_models.classes.mixins.model_hooks_mixin import ModelHooksMixin
from amsdal_models.managers.base_manager import BaseManager

# should be `set[int] | set[str] | dict[int, IncEx] | dict[str, IncEx] | None`, but mypy can't cope
IncEx: typing_extensions.TypeAlias = 'set[int] | set[str] | dict[int, Any] | dict[str, Any] | None'

logger = logging.getLogger(__name__)


class TypeModel(
    ModelHooksMixin,
    ReferenceHandler,
    BaseModel,
):
    @model_validator(mode='before')
    @classmethod
    def convert_string_to_dict(cls, data: Any) -> Any:
        # in case of some connections we may have strings saved in DB for nested fields
        if isinstance(data, str):
            try:
                data = json.loads(data)
            except json.JSONDecodeError:
                pass

        return data


@dataclass_transform(kw_only_default=True, field_specifiers=(Field,))
class AmsdalModelMetaclass(ModelMetaclass):
    def __new__(
        mcs,  # noqa: N804
        cls_name: str,
        bases: tuple[type[Any], ...],
        namespace: dict[str, Any],
        *args: Any,
        **kwargs: Any,
    ) -> type:
        cls = super().__new__(mcs, cls_name, bases, namespace, *args, **kwargs)

        if 'objects' in namespace:
            namespace['objects'].model = cls
        else:
            for base in bases:
                if hasattr(base, 'objects'):
                    cls.objects = base.objects.copy(cls=cls)  # type: ignore[attr-defined]
                    break

        return cls  # type: ignore[no-any-return]


class Model(TypeModel, metaclass=AmsdalModelMetaclass):
    """
    Base class for all model classes.
    """

    model_config = ConfigDict(validate_assignment=True)

    objects: ClassVar[BaseManager] = BaseManager()
    """Manager for the Model class."""

    def __init__(self, **kwargs: Any) -> None:
        """
        Initializes the Model object. This method first calls the pre_init() hook, then calls the __init__() method
        of the parent class, and finally calls the post_init() hook.

        :param kwargs: The data to initialize the Model object with.
        """
        is_new_object = not kwargs.get('_object_id', None)

        self.pre_init(is_new_object=is_new_object, kwargs=kwargs)
        super().__init__(**kwargs)
        self.post_init(is_new_object=is_new_object, kwargs=kwargs)

    @transaction
    def save(self, *, force_insert: bool = False, using: str | None = None) -> 'Model':
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
        if force_insert:
            if self.objects.filter(_address__object_id=self._object_id).count().execute():
                raise ObjectAlreadyExistsError(address=self._metadata.address)

            self._is_new_object = True

        _is_new_object = self._is_new_object

        if _is_new_object:
            self._create(using=using)
        else:
            self._update(using=using)

        return self

    @transaction
    def delete(self, using: str | None = None) -> None:
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
        self.pre_delete()

        if not self._metadata.is_latest:
            msg = 'Error! Trying to make a new version of an object that is not the latest version!'
            raise ValueError(msg)

        operations_manager = AmsdalDataManager().get_operations_manager()
        operations_manager.perform_operation(obj=self, operation=OperationType.DELETE, using=using)
        self.post_delete()

    @property
    def display_name(self) -> str:
        """
        This method is used to get the display name of the Model object. It returns the string representation of the
        object's address.

        :return: The display name of the Model object.
        :rtype: str
        """
        return str(self.get_metadata().address)

    def _create(self, using: str | None) -> None:
        self.pre_create()
        self._process_nested_objects()
        # TODO: check uniqueness
        operations_manager = AmsdalDataManager().get_operations_manager()
        operations_manager.perform_operation(obj=self, operation=OperationType.CREATE, using=using)
        self.post_create()
        self._is_new_object = False

    def _update(self, using: str | None) -> None:
        self.pre_update()

        if not self._metadata.is_latest:
            msg = 'Error! Trying to make a new version of an object that is not the latest version!'
            raise ValueError(msg)

        self._process_nested_objects()
        operations_manager = AmsdalDataManager().get_operations_manager()
        operations_manager.perform_operation(obj=self, operation=OperationType.UPDATE, using=using)
        self.post_update()

    def _process_nested_objects(self) -> None:
        for field in sorted(self.model_fields_set):
            setattr(self, field, self._process_nested_field(getattr(self, field)))

    def _process_nested_field(self, field_value: Any) -> Any:
        if isinstance(field_value, Model):
            if field_value.is_new_object:
                field_value.save()
            return field_value.get_metadata().reference
        elif isinstance(field_value, list | set | tuple):
            return [self._process_nested_field(item) for item in field_value]
        elif isinstance(field_value, dict):
            return {
                self._process_nested_field(key): self._process_nested_field(value) for key, value in field_value.items()
            }
        return field_value

    def model_dump_refs(
        self,
        *,
        mode: Literal['json', 'python'] | str = 'python',
        include: IncEx = None,
        exclude: IncEx = None,
        by_alias: bool = False,
        exclude_unset: bool = False,
        exclude_defaults: bool = False,
        exclude_none: bool = False,
        round_trip: bool = False,
        warnings: bool = True,
    ) -> dict[str, Any]:
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
        return super().model_dump_refs(
            mode=mode,
            include=include,
            exclude=exclude,
            by_alias=by_alias,
            exclude_unset=exclude_unset,
            exclude_defaults=exclude_defaults,
            exclude_none=exclude_none,
            round_trip=round_trip,
            warnings=warnings,
        )

    def model_dump(
        self,
        *,
        mode: Literal['json', 'python'] | str = 'python',
        include: IncEx = None,
        exclude: IncEx = None,
        by_alias: bool = False,
        exclude_unset: bool = False,
        exclude_defaults: bool = False,
        exclude_none: bool = False,
        round_trip: bool = False,
        warnings: bool = True,
    ) -> dict[str, Any]:
        """
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

        :param mode: The mode in which `to_python` should run. If mode is 'json', the dictionary will only contain
        JSON serializable types. If mode is 'python', the dictionary may contain any Python objects.
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
        return super().model_dump(
            mode=mode,
            include=include,
            exclude=exclude,
            by_alias=by_alias,
            exclude_unset=exclude_unset,
            exclude_defaults=exclude_defaults,
            exclude_none=exclude_none,
            round_trip=round_trip,
            warnings=warnings,
        )

    def model_dump_json_refs(
        self,
        *,
        indent: int | None = None,
        include: IncEx = None,
        exclude: IncEx = None,
        by_alias: bool = False,
        exclude_unset: bool = False,
        exclude_defaults: bool = False,
        exclude_none: bool = False,
        round_trip: bool = False,
        warnings: bool = True,
    ) -> str:
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

        return super().model_dump_json_refs(
            indent=indent,
            include=include,
            exclude=exclude,
            by_alias=by_alias,
            exclude_unset=exclude_unset,
            exclude_defaults=exclude_defaults,
            exclude_none=exclude_none,
            round_trip=round_trip,
            warnings=warnings,
        )

    def model_dump_json(
        self,
        *,
        indent: int | None = None,
        include: IncEx = None,
        exclude: IncEx = None,
        by_alias: bool = False,
        exclude_unset: bool = False,
        exclude_defaults: bool = False,
        exclude_none: bool = False,
        round_trip: bool = False,
        warnings: bool = True,
    ) -> str:
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

        return super().model_dump_json(
            indent=indent,
            include=include,
            exclude=exclude,
            by_alias=by_alias,
            exclude_unset=exclude_unset,
            exclude_defaults=exclude_defaults,
            exclude_none=exclude_none,
            round_trip=round_trip,
            warnings=warnings,
        )


class LegacyModel(TypeModel, metaclass=AmsdalModelMetaclass):
    model_config = ConfigDict(extra='allow')
