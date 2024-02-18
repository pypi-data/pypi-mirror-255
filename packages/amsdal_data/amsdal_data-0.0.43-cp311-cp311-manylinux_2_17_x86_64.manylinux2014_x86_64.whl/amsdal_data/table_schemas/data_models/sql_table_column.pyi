from collections.abc import Callable as Callable
from pydantic import BaseModel
from typing import Any, ClassVar

class SqlTableColumnsSchema(BaseModel):
    to_sql: ClassVar[Callable[..., str]]
    columns: list['SqlTableColumn']
    def to_sql(self, column_separator: str = '`') -> str: ...

class SqlTableColumn(BaseModel):
    to_sql: ClassVar[Callable[..., str]]
    _to_sql_value: ClassVar[Callable[..., str]]
    cid: int
    name: str
    type: str
    notnull: int
    dflt_value: Any
    pk: int
    def to_sql(self, column_separator: str = '`') -> str: ...
    def _to_sql_value(self, value: Any) -> str: ...
    def __hash__(self) -> int: ...
    def __eq__(self, other: Any) -> bool: ...
