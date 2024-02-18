from collections.abc import Callable
from typing import Any
from typing import ClassVar

from pydantic import BaseModel


class SqlTableColumnsSchema(BaseModel):
    to_sql: ClassVar[Callable[..., str]]

    columns: list['SqlTableColumn']

    def to_sql(self, column_separator: str = '`') -> str:  # type: ignore[no-redef]
        columns_statement: list[str] = []
        pks = []

        for column in self.columns:
            columns_statement.append(column.to_sql(column_separator))

            if column.pk:
                pks.append((column.name, column.pk))

        if pks:
            pks = sorted(pks, key=lambda item: item[1])
            columns_statement.append(f'PRIMARY KEY ({", ".join([pk[0] for pk in pks])})')

        return ', '.join(columns_statement)


class SqlTableColumn(BaseModel):
    to_sql: ClassVar[Callable[..., str]]
    _to_sql_value: ClassVar[Callable[..., str]]

    cid: int
    name: str
    type: str
    notnull: int
    dflt_value: Any
    pk: int

    def to_sql(self, column_separator: str = '`') -> str:  # type: ignore[no-redef]
        statement = f'{column_separator}{self.name}{column_separator} {self.type}'
        if self.notnull:
            statement += ' NOT NULL'
        if self.dflt_value:
            statement += f' DEFAULT {self._to_sql_value(self.dflt_value)}'
        return statement

    def _to_sql_value(self, value: Any) -> str:  # type: ignore[no-redef]
        if isinstance(value, str):
            return f"'{value}'"
        return str(value)

    def __hash__(self) -> int:
        return hash(self.name)

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, SqlTableColumn):
            return self.name == other.name
        return False
