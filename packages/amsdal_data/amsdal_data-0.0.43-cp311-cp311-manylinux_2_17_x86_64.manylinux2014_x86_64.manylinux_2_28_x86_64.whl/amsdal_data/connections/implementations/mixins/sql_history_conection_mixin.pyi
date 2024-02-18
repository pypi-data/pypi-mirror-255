from amsdal_data.connections.implementations.mixins.sqlite_statements_mixin import SqliteStatementsMixin as SqliteStatementsMixin
from amsdal_data.table_schemas.constants import PRIMARY_PARTITION_KEY as PRIMARY_PARTITION_KEY
from amsdal_utils.models.data_models.address import Address as Address
from amsdal_utils.query.utils import Q

class SqlHistoryConnectionMixin(SqliteStatementsMixin):
    def _get_table_names(self, address: Address) -> list[str]: ...
    @staticmethod
    def _build_queries_by_version(address: Address, conditions: Q | None = None) -> dict[str, Q]: ...
