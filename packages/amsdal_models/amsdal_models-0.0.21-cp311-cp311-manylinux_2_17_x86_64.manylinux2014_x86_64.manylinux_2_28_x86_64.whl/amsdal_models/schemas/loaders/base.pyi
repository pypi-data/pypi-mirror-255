import abc
from abc import ABC, abstractmethod
from amsdal_models.schemas.data_models.custom_code import CustomCodeSchema as CustomCodeSchema
from amsdal_models.schemas.data_models.options import OptionSchema as OptionSchema
from amsdal_models.schemas.data_models.schema import ObjectSchema as ObjectSchema
from amsdal_models.schemas.loaders.utils import load_object_schema_from_json_file as load_object_schema_from_json_file
from collections.abc import Iterator
from pathlib import Path

class ConfigLoaderBase(ABC, metaclass=abc.ABCMeta):
    @abstractmethod
    def iter_configs(self) -> Iterator[ObjectSchema]: ...
    @abstractmethod
    def __str__(self) -> str: ...

class OptionsLoaderBase(ABC, metaclass=abc.ABCMeta):
    @abstractmethod
    def iter_options(self) -> Iterator[OptionSchema]: ...
    @abstractmethod
    def __str__(self) -> str: ...

class CustomCodeLoaderBase(ABC, metaclass=abc.ABCMeta):
    @abstractmethod
    def iter_custom_code(self) -> Iterator[CustomCodeSchema]: ...
    @abstractmethod
    def __str__(self) -> str: ...

class TransactionsLoaderBase(ABC, metaclass=abc.ABCMeta):
    @abstractmethod
    def iter_transactions(self) -> Iterator[Path]: ...
    @abstractmethod
    def __str__(self) -> str: ...

class StaticsLoaderBase(ABC, metaclass=abc.ABCMeta):
    @abstractmethod
    def iter_static(self) -> Iterator[Path]: ...
    @abstractmethod
    def __str__(self) -> str: ...

class FixturesLoaderBase(ABC, metaclass=abc.ABCMeta):
    @abstractmethod
    def iter_fixtures(self) -> Iterator[Path]: ...
    @abstractmethod
    def iter_fixture_files(self) -> Iterator[Path]: ...
    @abstractmethod
    def __str__(self) -> str: ...

class ConfigReaderMixin:
    @classmethod
    def is_schema_file(cls, json_file: Path) -> bool: ...
    @staticmethod
    def read_configs_from_file(json_file: Path) -> Iterator[ObjectSchema]: ...
