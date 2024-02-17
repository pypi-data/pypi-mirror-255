from _typeshed import Incomplete
from amsdal_models.schemas.data_models.schema import ObjectSchema as ObjectSchema
from amsdal_models.schemas.loaders.base import FixturesLoaderBase as FixturesLoaderBase
from collections.abc import Iterator
from pathlib import Path

FIXTURES: str
logger: Incomplete
FIXTURES_JSON_FILE: str
MODEL_JSON_FILE: str

class CliFixturesLoader(FixturesLoaderBase):
    models_with_fixtures: Incomplete
    def __init__(self, schema_dir: Path) -> None: ...
    def iter_fixtures(self) -> Iterator[Path]: ...
    def iter_fixture_files(self) -> Iterator[Path]: ...
    def __str__(self) -> str: ...
