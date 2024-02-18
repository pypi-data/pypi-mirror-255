import abc
from _typeshed import Incomplete
from abc import ABC, abstractmethod
from amsdal_data.connections.base import ConnectionBase as ConnectionBase
from amsdal_utils.models.data_models.address import Address as Address
from amsdal_utils.models.data_models.table_schema import TableSchema as TableSchema

class TableSchemaServiceBase(ABC, metaclass=abc.ABCMeta):
    connection: Incomplete
    def __init__(self, connection: ConnectionBase) -> None: ...
    @abstractmethod
    def register_table(self, table_schema: TableSchema) -> tuple[str, bool]:
        """
        Creates a table in the database and
        returns the table name and flag indicating if the table was created or updated.
        """
    @abstractmethod
    def unregister_table(self, address: Address) -> None:
        """
        Unregister a table in the database.
        """
    @abstractmethod
    def resolve_table_name(self, address: Address) -> str: ...
    @abstractmethod
    def register_internal_tables(self) -> None: ...
