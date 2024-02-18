import logging
from abc import ABC
from abc import abstractmethod
from typing import TYPE_CHECKING
from typing import Any

from amsdal_data.connections.base import ConnectionBase
from amsdal_data.manager import AmsdalDataManager
from amsdal_utils.classes.version_manager import ClassVersionManager
from amsdal_utils.config.manager import AmsdalConfigManager
from amsdal_utils.models.data_models.address import Address

if TYPE_CHECKING:
    from amsdal_models.querysets.base_queryset import QuerySetBase

logger = logging.getLogger(__name__)

DEFAULT_DB_ALIAS = 'default'
LAKEHOUSE_DB_ALIAS = 'lakehouse'


class ExecutorBase(ABC):
    queryset: 'QuerySetBase'

    def __init__(self, queryset: 'QuerySetBase') -> None:
        self.queryset = queryset
        self._config_manager = AmsdalConfigManager()

    def _get_connection_name(self) -> str:
        if self.queryset._using == DEFAULT_DB_ALIAS:
            return self._config_manager.get_connection_name_by_model_name(self.queryset.entity_name)

        if self.queryset._using == LAKEHOUSE_DB_ALIAS:
            return self._config_manager.get_config().resources_config.lakehouse

        return self.queryset._using

    def _get_connection(self) -> ConnectionBase:
        return AmsdalDataManager().get_connection_manager().get_connection(self._get_connection_name())

    @abstractmethod
    def query(self) -> list[dict[str, Any]]: ...

    @abstractmethod
    def count(self) -> int: ...


class Executor(ExecutorBase):
    def _address(self) -> Address:
        return Address(
            resource='',
            class_name=self.queryset.entity_name,
            class_version=ClassVersionManager().get_latest_class_version(self.queryset.entity_name).version,
            object_id='',
            object_version='',
        )

    def query(self) -> list[dict[str, Any]]:
        return self._get_connection().query(
            address=self._address(),
            query_specifier=self.queryset._query_specifier,
            conditions=self.queryset._conditions,
            pagination=self.queryset._paginator,
            order_by=self.queryset._order_by,
        )

    def count(self) -> int:
        return self._get_connection().count(
            address=self._address(),
            conditions=self.queryset._conditions,
        )
