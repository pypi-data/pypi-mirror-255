from _typeshed import Incomplete
from amsdal_models.classes.model import Model as Model
from amsdal_models.querysets.errors import MultipleObjectsReturnedError as MultipleObjectsReturnedError, ObjectDoesNotExistError as ObjectDoesNotExistError
from amsdal_models.querysets.executor import DEFAULT_DB_ALIAS as DEFAULT_DB_ALIAS, Executor as Executor
from amsdal_utils.query.utils import Q
from typing import Any, Optional, TypeVar

logger: Incomplete
QuerySetType = TypeVar('QuerySetType', bound='QuerySetBase')

class QuerySetBase:
    """
    Base class for QuerySets.
    """
    _entity: Incomplete
    _paginator: Incomplete
    _order_by: Incomplete
    _query_specifier: Incomplete
    _conditions: Incomplete
    _using: Incomplete
    def __init__(self, entity: type['Model']) -> None: ...
    @property
    def entity_name(self) -> str: ...
    def using(self, value: str) -> QuerySetType: ...
    @classmethod
    def _from_queryset(cls, queryset: QuerySetBase) -> QuerySetType: ...
    def _copy(self) -> QuerySetType: ...
    def __copy__(self) -> QuerySetType: ...
    def only(self, fields: list[str]) -> QuerySetType:
        """
        Limit the number of fields to be returned.


        :param fields: the fields to be returned
        :type fields: list[str]

        :rtype: QuerySetType
        """
    def distinct(self, fields: list[str]) -> QuerySetType:
        """
        Return only distinct (different) values.

        :param fields: the fields to be distinct
        :type fields: list[str]

        :rtype: QuerySetType
        """
    def filter(self, *args: Q, **kwargs: Any) -> QuerySetType:
        """
        Apply filters to the query. The filters are combined with AND.

        :param args: the filters to be applied
        :type args: Q
        :param kwargs: the filters to be applied
        :type kwargs: Any

        :rtype: QuerySetType
        """
    def exclude(self, *args: Q, **kwargs: Any) -> QuerySetType:
        """
        Exclude filters from the query. The filters are combined with AND.

        :param args: the filters to be applied
        :type args: Q
        :param kwargs: the filters to be applied
        :type kwargs: Any

        :rtype: QuerySetType
        """
    def _execute_query(self) -> list[dict[str, Any]]: ...
    def _execute_count(self) -> int: ...
    def _filter(self, *args: Q, negated: bool = ..., **kwargs: Any) -> QuerySetType: ...
    def order_by(self, *args: str) -> QuerySetType:
        """
        Order the query by the given fields.

        :param args: the fields to order by
        :type args: str

        :rtype: QuerySetType
        """
    def __getitem__(self, index: slice | int) -> QuerySetType: ...
    def _create_instance(self, **kwargs: Any) -> Model: ...

class QuerySet(QuerySetBase):
    """
    Interface to access the database.
    """
    def get(self, *args: Q, **kwargs: Any) -> QuerySetOneRequired:
        """
        Change the QuerySet to a QuerySetOneRequired. Query execution will return a single item or raise an error.

        :param args: the filters to be applied
        :type args: Q
        :param kwargs: the filters to be applied
        :type kwargs: Any

        :rtype: QuerySetOneRequired
        """
    def get_or_none(self, *args: Q, **kwargs: Any) -> QuerySetOne:
        """
        Change the QuerySet to a QuerySetOne. Query execution will return a single item or None.

        :param args: the filters to be applied
        :type args: Q
        :param kwargs: the filters to be applied
        :type kwargs: Any

        :rtype: QuerySetOneRequired
        """
    def first(self, *args: Q, **kwargs: Any) -> QuerySetOne:
        """
        Change the QuerySet to a QuerySetOne. Query execution will return the first item or None.

        :param args: the filters to be applied
        :type args: Q
        :param kwargs: the filters to be applied
        :type kwargs: Any

        :rtype: QuerySetOneRequired
        """
    def count(self) -> QuerySetCount:
        """
        Change the QuerySet to a QuerySetCount. Query execution will return the count of items.
        """
    def execute(self) -> list['Model']:
        """
        Return the list of items.

        :rtype: list[Model]
        """
    def only(self, fields: list[str]) -> QuerySet: ...
    def distinct(self, fields: list[str]) -> QuerySet: ...
    def filter(self, *args: Q, **kwargs: Any) -> QuerySet: ...
    def exclude(self, *args: Q, **kwargs: Any) -> QuerySet: ...
    def order_by(self, *args: str) -> QuerySet: ...

class QuerySetOne(QuerySetBase):
    """
    QuerySet class for models. QuerySet is executed to a single model object or None.
    """
    _raise_on_multiple: bool
    def __init__(self, entity: type['Model']) -> None: ...
    def only(self, fields: list[str]) -> QuerySetOne: ...
    def distinct(self, fields: list[str]) -> QuerySetOne: ...
    def filter(self, *args: Q, **kwargs: Any) -> QuerySetOne: ...
    def exclude(self, *args: Q, **kwargs: Any) -> QuerySetOne: ...
    def order_by(self, *args: str) -> QuerySetOne: ...
    def execute(self) -> Optional['Model']:
        """
        Query the database and return the single item or None.

        :raises MultipleObjectsReturnedError: If multiple items are found.

        :rtype: Model | None
        """

class QuerySetOneRequired(QuerySetOne):
    """
    QuerySet class for models. QuerySet is executed to a single model object or raises an error.
    """
    def only(self, fields: list[str]) -> QuerySetOneRequired: ...
    def distinct(self, fields: list[str]) -> QuerySetOneRequired: ...
    def filter(self, *args: Q, **kwargs: Any) -> QuerySetOneRequired: ...
    def exclude(self, *args: Q, **kwargs: Any) -> QuerySetOneRequired: ...
    def order_by(self, *args: str) -> QuerySetOneRequired: ...
    def execute(self) -> Model:
        """
        Return the single item.

        :raises ObjectDoesNotExistError: If no items are found.

        :rtype: Model

        """

class QuerySetCount(QuerySetBase):
    """
    QuerySet class for models. QuerySet is executed to a count of items.
    """
    def only(self, fields: list[str]) -> QuerySetCount: ...
    def distinct(self, fields: list[str]) -> QuerySetCount: ...
    def filter(self, *args: Q, **kwargs: Any) -> QuerySetCount: ...
    def exclude(self, *args: Q, **kwargs: Any) -> QuerySetCount: ...
    def order_by(self, *args: str) -> QuerySetCount: ...
    def execute(self) -> int:
        """
        Return the count of items.

        :rtype: int
        """
