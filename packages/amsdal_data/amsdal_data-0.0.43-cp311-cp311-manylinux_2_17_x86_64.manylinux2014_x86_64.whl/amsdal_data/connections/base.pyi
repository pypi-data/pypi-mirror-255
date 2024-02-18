import abc
from abc import ABC, abstractmethod
from amsdal_data.table_schemas.base import TableSchemaServiceBase as TableSchemaServiceBase
from amsdal_utils.models.data_models.address import Address as Address
from amsdal_utils.query.data_models.order_by import OrderBy as OrderBy
from amsdal_utils.query.data_models.paginator import CursorPaginator as CursorPaginator, NumberPaginator as NumberPaginator
from amsdal_utils.query.data_models.query_specifier import QuerySpecifier as QuerySpecifier
from amsdal_utils.query.utils import Q as Q
from typing import Any

class Connectable(ABC, metaclass=abc.ABCMeta):
    @abstractmethod
    def connect(self, *args: Any, **kwargs: Any) -> None:
        """
        Connects to the database.
        :param kwargs: the connection parameters
        :type kwargs: Any

        :return: None
        """
    @abstractmethod
    def disconnect(self) -> None:
        """
        Disconnects from the database.

        :return: None
        """

class ConnectionBase(Connectable, ABC, metaclass=abc.ABCMeta):
    @abstractmethod
    def begin(self) -> None:
        """
        Begins a kind of transaction for this connection.

        :return: None
        """
    @abstractmethod
    def commit(self) -> None:
        """
        Commits (stores) the objects to the database.
        """
    @abstractmethod
    def revert(self) -> None:
        """
        Reverts the committed data.
        """
    @abstractmethod
    def on_transaction_complete(self) -> None:
        """
        Called when the transaction is complete for all connections successfully.
        You should not write to database in this method.
        """
    @abstractmethod
    def rollback(self) -> None:
        """
        Rollback the transaction itself.
        """
    @abstractmethod
    def query(self, address: Address, query_specifier: QuerySpecifier | None = None, conditions: Q | None = None, pagination: NumberPaginator | CursorPaginator | None = None, order_by: list[OrderBy] | None = None) -> list[dict[str, Any]]:
        """
        Queries the database for objects.

        :param address: the address of the objects
        :param query_specifier: the query specifier that allows to specify the fields to return and the distinct fields
        :param conditions: the conditions to filter the objects by
        :param pagination: the pagination object to paginate the objects
        :param order_by: the order by object to order the objects
        :return: list of objects data
        :rtype: list[dict[str, Any]]
        """
    @abstractmethod
    def count(self, address: Address, conditions: Q | None = None) -> int:
        """
        Returns the count of objects in the database.

        :param address: the address of the objects
        :param conditions: the conditions to filter the objects by
        :return: number of objects
        :rtype: int
        """
    @property
    @abstractmethod
    def table_schema_manager(self) -> TableSchemaServiceBase:
        """
        Returns the table schema manager related to this type of connection.

        :return: the table schema manager
        :rtype: TableSchemaServiceBase
        """
    @abstractmethod
    def prepare_connection(self) -> None:
        """
        Ensure all the necessary system entities are created.
        """
