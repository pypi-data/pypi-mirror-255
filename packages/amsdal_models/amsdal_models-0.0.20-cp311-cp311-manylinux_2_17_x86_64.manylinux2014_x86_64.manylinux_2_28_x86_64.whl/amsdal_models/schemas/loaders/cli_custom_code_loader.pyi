from _typeshed import Incomplete
from amsdal_models.schemas.data_models.custom_code import CustomCodeSchema as CustomCodeSchema
from amsdal_models.schemas.data_models.schema import ObjectSchema as ObjectSchema
from amsdal_models.schemas.loaders.base import ConfigReaderMixin as ConfigReaderMixin, CustomCodeLoaderBase as CustomCodeLoaderBase
from collections.abc import Iterator
from pathlib import Path

HOOKS: str
MODIFIERS: str
PROPERTIES: str
MODEL_JSON_FILE: str
logger: Incomplete

class CliCustomCodeLoader(ConfigReaderMixin, CustomCodeLoaderBase):
    _schema_dir: Incomplete
    def __init__(self, schema_dir: Path) -> None: ...
    def __str__(self) -> str: ...
    def iter_custom_code(self) -> Iterator[CustomCodeSchema]: ...
    def read_custom_code_from_model_directory(self, model_directory: Path, object_config: ObjectSchema) -> CustomCodeSchema: ...
    def read_custom_code_from_subdirectory(self, model_directory: Path, subdirectory: str) -> list[str]: ...
    def iter_model_directories(self) -> Iterator[tuple[Path, ObjectSchema]]: ...
