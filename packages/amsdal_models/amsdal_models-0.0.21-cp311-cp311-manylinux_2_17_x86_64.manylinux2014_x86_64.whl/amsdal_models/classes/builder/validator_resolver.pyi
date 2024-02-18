from amsdal_models.classes.builder.validators.dict_validators import validate_non_empty_keys as validate_non_empty_keys
from amsdal_models.classes.builder.validators.options_validators import validate_options as validate_options
from amsdal_models.schemas.data_models.schema import PropertyData as PropertyData
from collections.abc import Callable as Callable
from typing import Any, ClassVar

class ValidatorResolver:
    TYPE_BASED_VALIDATORS: ClassVar[dict[str, Any]]
    @classmethod
    def process_property(cls, property_name: str, property_config: PropertyData) -> list[tuple[str, Callable[[Any, list[Any]], Any], list[Any] | None]]: ...
