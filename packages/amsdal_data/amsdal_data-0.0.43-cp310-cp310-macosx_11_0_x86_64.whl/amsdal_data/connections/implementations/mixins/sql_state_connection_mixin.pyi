from amsdal_data.connections.implementations.mixins.sqlite_statements_mixin import SqliteStatementsMixin as SqliteStatementsMixin
from amsdal_data.table_schemas.constants import PRIMARY_PARTITION_KEY as PRIMARY_PARTITION_KEY
from amsdal_utils.models.data_models.address import Address as Address
from typing import Any

class SqlStateConnectionMixin(SqliteStatementsMixin):
    def _build_update_statement(self, address: Address, data: dict[str, Any]) -> tuple[str, tuple[Any, ...]]: ...
    def _get_table_name(self, address: Address) -> str: ...
