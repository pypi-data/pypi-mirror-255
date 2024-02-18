from abc import ABC
from abc import abstractmethod

from amsdal_utils.models.data_models.address import Address
from amsdal_utils.models.data_models.table_schema import TableSchema

from amsdal_data.connections.base import ConnectionBase


class TableSchemaServiceBase(ABC):
    def __init__(self, connection: ConnectionBase):
        self.connection = connection

    @abstractmethod
    def register_table(self, table_schema: TableSchema) -> tuple[str, bool]:
        """
        Creates a table in the database and
        returns the table name and flag indicating if the table was created or updated.
        """
        ...

    @abstractmethod
    def unregister_table(self, address: Address) -> None:
        """
        Unregister a table in the database.
        """
        ...

    @abstractmethod
    def resolve_table_name(self, address: Address) -> str: ...

    @abstractmethod
    def register_internal_tables(self) -> None: ...
