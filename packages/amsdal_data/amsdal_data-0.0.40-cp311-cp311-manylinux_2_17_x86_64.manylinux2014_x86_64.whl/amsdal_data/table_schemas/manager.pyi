from _typeshed import Incomplete
from amsdal_data.manager import AmsdalDataManager as AmsdalDataManager
from amsdal_data.table_schemas.base import TableSchemaServiceBase as TableSchemaServiceBase
from amsdal_data.transactions.manager import AmsdalTransactionManager as AmsdalTransactionManager
from amsdal_utils.models.data_models.address import Address as Address
from amsdal_utils.models.data_models.table_schema import TableSchema as TableSchema
from amsdal_utils.utils.singleton import Singleton

class TableSchemasManager(metaclass=Singleton):
    _tables: Incomplete
    def __init__(self) -> None: ...
    def register_table(self, table_schema: TableSchema) -> tuple[str, bool]:
        """
        Check, register and creates a new table in the database through connection.

        :param table_schema: TableSchema object
        :type table_schema: TableSchema
        :return: Table name and a boolean, if it's true it means the table was created, otherwise - updated.
        :rtype: tuple[str, bool]
        """
    def unregister_table(self, address: Address) -> None: ...
    @staticmethod
    def resolve_table_schema_services(address: Address) -> list[TableSchemaServiceBase]: ...
