from amsdal_data.connections.implementations.sqlite_state import SqliteStateConnection as SqliteStateConnection
from amsdal_data.table_schemas.base import TableSchemaServiceBase as TableSchemaServiceBase
from amsdal_data.table_schemas.data_models.sql_table_column import SqlTableColumn as SqlTableColumn
from amsdal_data.table_schemas.implementations.mixins.sql_statements_mixin import SqlStatementsMixin as SqlStatementsMixin
from amsdal_data.transactions.constants import TRANSACTION_CLASS_NAME as TRANSACTION_CLASS_NAME
from amsdal_utils.models.data_models.address import Address
from amsdal_utils.models.data_models.table_schema import TableSchema
from typing import Any

class SqliteHistoricalTableSchemaService(SqlStatementsMixin, TableSchemaServiceBase):
    connection: SqliteStateConnection
    def register_table(self, table_schema: TableSchema, *, is_internal_table: bool = False) -> tuple[str, bool]: ...
    def unregister_table(self, address: Address) -> None: ...
    def resolve_table_name(self, address: Address) -> str: ...
    @staticmethod
    def _build_select_table_name_statement(table_name: str) -> tuple[str, list[Any]]: ...
    def create_table(self, table_name: str, table_schema: TableSchema, *, is_internal_table: bool = False) -> None: ...
    def register_internal_tables(self) -> None: ...
