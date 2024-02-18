from _typeshed import Incomplete
from collections.abc import Iterator
from pathlib import Path
from pydantic import BaseModel as BaseModel

logger: Incomplete

def load_object_schema_from_json_file(file_path: Path, model_cls: type[BaseModel]) -> Iterator[BaseModel]: ...
