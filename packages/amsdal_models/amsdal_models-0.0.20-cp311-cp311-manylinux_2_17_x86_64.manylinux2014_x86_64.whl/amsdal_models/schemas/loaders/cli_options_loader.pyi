from _typeshed import Incomplete
from amsdal_models.schemas.data_models.options import OptionSchema as OptionSchema
from amsdal_models.schemas.loaders.base import OptionsLoaderBase as OptionsLoaderBase
from amsdal_models.schemas.loaders.utils import load_object_schema_from_json_file as load_object_schema_from_json_file
from collections.abc import Iterator
from pathlib import Path

logger: Incomplete

class CliOptionsLoader(OptionsLoaderBase):
    _app_root: Incomplete
    def __init__(self, config_dir: Path) -> None: ...
    def __str__(self) -> str: ...
    def iter_options(self) -> Iterator[OptionSchema]: ...
    def iter_json_files(self) -> Iterator[Path]: ...
    @staticmethod
    def read_options_from_file(json_file: Path) -> Iterator[OptionSchema]: ...
