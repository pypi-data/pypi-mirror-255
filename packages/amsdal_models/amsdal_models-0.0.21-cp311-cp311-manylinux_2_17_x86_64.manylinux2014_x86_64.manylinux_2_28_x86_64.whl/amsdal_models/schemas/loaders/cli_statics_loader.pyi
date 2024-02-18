from _typeshed import Incomplete
from amsdal_models.schemas.loaders.base import StaticsLoaderBase as StaticsLoaderBase
from collections.abc import Iterator
from pathlib import Path

class CliStaticsLoader(StaticsLoaderBase):
    _app_root: Incomplete
    def __init__(self, app_root: Path) -> None: ...
    def iter_static(self) -> Iterator[Path]: ...
    def __str__(self) -> str: ...
