from typing import Any
from typing import Literal

import typing_extensions
from amsdal_utils.models.data_models.reference import Reference
from pydantic import PrivateAttr
from pydantic import model_serializer

from amsdal_models.classes.handlers.object_id_handler import ObjectIdHandler

# should be `set[int] | set[str] | dict[int, IncEx] | dict[str, IncEx] | None`, but mypy can't cope
IncEx: typing_extensions.TypeAlias = 'set[int] | set[str] | dict[int, Any] | dict[str, Any] | None'


class ReferenceHandler(ObjectIdHandler):
    _serialize_with_refs: bool = PrivateAttr(default=False)
    _exclude_none: bool = PrivateAttr(default=False)

    @model_serializer
    def ser_model(self) -> dict[str, Any]:
        from amsdal_models.classes.base import BaseModel
        from amsdal_models.classes.helpers.reference_loader import ReferenceLoader
        from amsdal_models.classes.model import Model

        data: dict[str, Any] = {}
        stack_context = {
            id(self): data,
        }

        def _serialize_value(_value: Any, _stack_context: dict[Any, dict[str, Any]]) -> Any:
            _value_id = id(_value)
            ref_hash: int | None = None

            if _stack_context is not None and _value_id in _stack_context:
                return _stack_context[_value_id]

            if isinstance(_value, Reference):
                ref_hash = hash(_value)

                if _stack_context is not None and ref_hash in _stack_context:
                    return _stack_context[ref_hash]

                if self._serialize_with_refs:
                    _value = _value.model_dump(exclude_none=self._exclude_none)
                else:
                    _value = ReferenceLoader(_value).load_reference()

                if _stack_context is not None:
                    _stack_context[ref_hash] = _value

            if isinstance(_value, BaseModel):
                if _stack_context is not None:
                    _stack_context[_value_id] = {}

                    if ref_hash is not None:
                        _stack_context[ref_hash] = _stack_context[_value_id]

                if self._serialize_with_refs and isinstance(_value, Model):
                    _value = _value.get_metadata().reference.model_dump(exclude_none=self._exclude_none)
                else:
                    _dict_value = {}

                    for _field in _value.model_fields:
                        _field_value = getattr(_value, _field)

                        if isinstance(_field_value, list):
                            _field_value = [_serialize_value(item, stack_context) for item in _field_value]
                        elif isinstance(_field_value, dict):
                            _field_value = {
                                key: _serialize_value(item, stack_context) for key, item in _field_value.items()
                            }

                        if _field_value is not None or not self._exclude_none:
                            _dict_value[_field] = _serialize_value(_field_value, stack_context)

                    _value = _dict_value

                if _stack_context is not None:
                    _stack_context[_value_id].update(_value)
            return _value

        for field_name in self.model_fields:
            value = getattr(self, field_name)
            value = _serialize_value(value, stack_context)

            if isinstance(value, list):
                value = [_serialize_value(item, stack_context) for item in value]
            elif isinstance(value, dict):
                value = {key: _serialize_value(item, stack_context) for key, item in value.items()}

            if value is not None or not self._exclude_none:
                data[field_name] = value

        if self.__pydantic_extra__:
            for field_name, value in self.__pydantic_extra__.items():
                data[field_name] = value

        return data

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
        self._serialize_with_refs = True
        self._exclude_none = exclude_none
        return super(ObjectIdHandler, self).model_dump(
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
        self._serialize_with_refs = False
        self._exclude_none = exclude_none
        return super(ObjectIdHandler, self).model_dump(
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
        self._serialize_with_refs = True
        self._exclude_none = exclude_none
        return super(ObjectIdHandler, self).model_dump_json(
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
        self._serialize_with_refs = False
        self._exclude_none = exclude_none
        return super(ObjectIdHandler, self).model_dump_json(
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
