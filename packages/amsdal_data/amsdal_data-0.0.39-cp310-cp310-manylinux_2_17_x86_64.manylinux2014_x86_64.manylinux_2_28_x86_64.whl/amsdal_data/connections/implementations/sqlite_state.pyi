import sqlite3
from _typeshed import Incomplete
from amsdal_data.connections.enums import ModifyOperation as ModifyOperation
from amsdal_data.connections.errors import AmsdalConnectionError as AmsdalConnectionError
from amsdal_data.connections.implementations.mixins.sql_state_connection_mixin import SqlStateConnectionMixin as SqlStateConnectionMixin
from amsdal_data.connections.state_base import StateConnectionBase as StateConnectionBase
from amsdal_data.table_schemas.base import TableSchemaServiceBase as TableSchemaServiceBase
from amsdal_data.table_schemas.constants import PRIMARY_PARTITION_KEY as PRIMARY_PARTITION_KEY
from amsdal_utils.models.data_models.address import Address as Address
from amsdal_utils.query.data_models.order_by import OrderBy as OrderBy
from amsdal_utils.query.data_models.paginator import CursorPaginator as CursorPaginator, NumberPaginator as NumberPaginator
from amsdal_utils.query.data_models.query_specifier import QuerySpecifier as QuerySpecifier
from amsdal_utils.query.utils import Q
from pathlib import Path
from typing import Any

logger: Incomplete

class SqliteStateConnection(SqlStateConnectionMixin, StateConnectionBase):
    _is_revert_enabled: Incomplete
    _revert_data: Incomplete
    _connection: Incomplete
    def __init__(self, *, is_revert_supported: bool = True) -> None: ...
    @property
    def table_schema_manager(self) -> TableSchemaServiceBase: ...
    def connect(self, db_path: Path, **kwargs: Any) -> None:
        """
        Connects to the SQLite database. Raises an AmsdalConnectionError if the connection is already established.
        :param db_path: the path to the database
        :type db_path: Path
        :param kwargs: the connection parameters
        :type kwargs: Any

        :return: None
        """
    def disconnect(self) -> None: ...
    def _add_revert_data(self, operation: ModifyOperation, address: Address, data: dict[str, Any]) -> None: ...
    def insert(self, address: Address, data: dict[str, Any]) -> None: ...
    def update(self, address: Address, data: dict[str, Any]) -> None: ...
    def delete(self, address: Address) -> None: ...
    def begin(self) -> None: ...
    def commit(self) -> None: ...
    def revert(self) -> None: ...
    def rollback(self) -> None: ...
    def on_transaction_complete(self) -> None:
        """Transaction is completed successfully. Clear the revert data."""
    def query(self, address: Address, query_specifier: QuerySpecifier | None = None, conditions: Q | None = None, pagination: NumberPaginator | CursorPaginator | None = None, order_by: list[OrderBy] | None = None) -> list[dict[str, Any]]: ...
    def _get_record(self, address: Address) -> dict[str, Any]: ...
    def execute(self, query: str, *args: Any) -> sqlite3.Cursor: ...
    def count(self, address: Address, conditions: Q | None = None) -> int: ...
    def prepare_connection(self) -> None: ...
