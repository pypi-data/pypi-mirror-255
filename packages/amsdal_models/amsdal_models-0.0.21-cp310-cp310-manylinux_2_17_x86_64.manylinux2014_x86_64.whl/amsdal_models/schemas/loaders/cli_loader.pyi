from _typeshed import Incomplete
from amsdal_models.schemas.data_models.schema import ObjectSchema as ObjectSchema
from amsdal_models.schemas.loaders.base import ConfigLoaderBase as ConfigLoaderBase, ConfigReaderMixin as ConfigReaderMixin
from collections.abc import Iterator
from pathlib import Path

MODEL_JSON_FILE: str

class CliConfigLoader(ConfigReaderMixin, ConfigLoaderBase):
    _config_dir: Incomplete
    def __init__(self, config_dir: Path) -> None: ...
    def __str__(self) -> str: ...
    def iter_configs(self) -> Iterator[ObjectSchema]: ...
    def iter_json_files(self) -> Iterator[Path]: ...
