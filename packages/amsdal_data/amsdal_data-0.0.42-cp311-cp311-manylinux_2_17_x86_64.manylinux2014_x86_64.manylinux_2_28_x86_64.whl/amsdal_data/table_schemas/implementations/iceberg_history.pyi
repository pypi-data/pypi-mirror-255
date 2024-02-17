from _typeshed import Incomplete
from amsdal_data.connections.implementations.iceberg_history import IcebergHistoricalConnection as IcebergHistoricalConnection
from amsdal_data.table_schemas.base import TableSchemaServiceBase as TableSchemaServiceBase
from amsdal_data.table_schemas.data_models.iceberg_table_column import ComplexType as ComplexType, IcebergTableColumnsSchema as IcebergTableColumnsSchema
from amsdal_data.transactions.constants import TRANSACTION_CLASS_NAME as TRANSACTION_CLASS_NAME
from amsdal_utils.models.data_models.address import Address
from amsdal_utils.models.data_models.table_schema import TableColumnSchema, TableSchema

address_struct: Incomplete
reference_struct: Incomplete

class IcebergTableColumnSchema(TableColumnSchema):
    type: type | ComplexType

class IcebergHistoryTableSchemaService(TableSchemaServiceBase):
    connection: IcebergHistoricalConnection
    def register_table(self, table_schema: TableSchema) -> tuple[str, bool]: ...
    def resolve_table_name(self, address: Address) -> str: ...
    def _build_create_table_statement(self, table_name: str, table_schema: TableSchema) -> str: ...
    def create_table(self, table_name: str, table_schema: TableSchema) -> None: ...
    def unregister_table(self, address: Address) -> None: ...
    def register_internal_tables(self) -> None: ...
