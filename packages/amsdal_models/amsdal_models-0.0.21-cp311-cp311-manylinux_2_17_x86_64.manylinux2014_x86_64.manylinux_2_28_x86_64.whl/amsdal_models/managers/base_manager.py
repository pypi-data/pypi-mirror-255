import logging
from typing import TYPE_CHECKING
from typing import Any

from amsdal_utils.query.utils import Q

from amsdal_models.querysets.base_queryset import QuerySet
from amsdal_models.querysets.base_queryset import QuerySetOne
from amsdal_models.querysets.base_queryset import QuerySetOneRequired

if TYPE_CHECKING:
    from amsdal_models.classes.model import Model

logger = logging.getLogger(__name__)


class BaseManager:
    """
    Base manager for creating QuerySets for models.
    """

    model: type['Model']

    def copy(self, cls: type['Model']) -> 'BaseManager':
        manager = self.__class__()
        manager.model = cls

        return manager

    def get_queryset(self) -> 'QuerySet':
        return QuerySet(self.model)

    def using(self, value: str) -> 'QuerySet':
        return self.get_queryset().using(value)

    def all(self) -> 'QuerySet':
        return self.get_queryset()

    def only(self, fields: list[str]) -> 'QuerySet':
        return self.get_queryset().only(fields=fields)

    def distinct(self, fields: list[str]) -> 'QuerySet':
        return self.get_queryset().distinct(fields=fields)

    def filter(self, *args: Q, **kwargs: Any) -> 'QuerySet':
        return self.get_queryset().filter(*args, **kwargs)

    def exclude(self, *args: Q, **kwargs: Any) -> 'QuerySet':
        return self.get_queryset().exclude(*args, **kwargs)

    def get(self, *args: Q, **kwargs: Any) -> 'QuerySetOneRequired':
        return QuerySetOneRequired._from_queryset(
            self.get_queryset().filter(*args, **kwargs),
        )

    def get_or_none(self, *args: Q, **kwargs: Any) -> 'QuerySetOne':
        return QuerySetOne._from_queryset(
            self.get_queryset().filter(*args, **kwargs),
        )
