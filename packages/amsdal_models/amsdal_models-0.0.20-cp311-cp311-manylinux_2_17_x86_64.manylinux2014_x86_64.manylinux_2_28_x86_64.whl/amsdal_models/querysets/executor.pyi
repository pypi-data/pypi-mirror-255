import abc
from _typeshed import Incomplete
from abc import ABC, abstractmethod
from amsdal_data.connections.base import ConnectionBase
from amsdal_models.querysets.base_queryset import QuerySetBase as QuerySetBase
from amsdal_utils.models.data_models.address import Address
from typing import Any

logger: Incomplete
DEFAULT_DB_ALIAS: str
LAKEHOUSE_DB_ALIAS: str

class ExecutorBase(ABC, metaclass=abc.ABCMeta):
    queryset: QuerySetBase
    _config_manager: Incomplete
    def __init__(self, queryset: QuerySetBase) -> None: ...
    def _get_connection_name(self) -> str: ...
    def _get_connection(self) -> ConnectionBase: ...
    @abstractmethod
    def query(self) -> list[dict[str, Any]]: ...
    @abstractmethod
    def count(self) -> int: ...

class Executor(ExecutorBase):
    def _address(self) -> Address: ...
    def query(self) -> list[dict[str, Any]]: ...
    def count(self) -> int: ...
