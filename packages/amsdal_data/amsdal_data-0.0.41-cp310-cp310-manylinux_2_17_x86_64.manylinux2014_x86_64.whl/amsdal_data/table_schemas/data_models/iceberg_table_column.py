from collections.abc import Callable
from datetime import date
from datetime import datetime
from enum import Enum
from typing import Any
from typing import ClassVar
from typing import Union

from pydantic import BaseModel


class IcebergDataTypes(str, Enum):
    BOOLEAN = 'boolean'
    INT = 'int'
    BIGINT = 'bigint'
    LONG = 'long'
    FLOAT = 'float'
    DOUBLE = 'double'
    DATE = 'date'
    TIME = 'time'
    TIMESTAMP = 'timestamp'
    STRING = 'string'
    UUID = 'uuid'
    BINARY = 'binary'
    STRUCT = 'struct'
    LIST = 'list'
    MAP = 'map'


python_to_iceberg_types = {
    bool: IcebergDataTypes.BOOLEAN,
    int: IcebergDataTypes.LONG,
    float: IcebergDataTypes.DOUBLE,
    str: IcebergDataTypes.STRING,
    bytes: IcebergDataTypes.BINARY,
    date: IcebergDataTypes.DATE,
    datetime: IcebergDataTypes.TIMESTAMP,
}


class ComplexType(BaseModel):
    to_sql: ClassVar[Callable[..., str]]
    _type_value: ClassVar[Callable[[Any, Union[IcebergDataTypes, 'ComplexType']], str]]

    def to_sql(self) -> str:  # type: ignore[no-redef]
        return 'string'

    def _type_value(self, value: Union[IcebergDataTypes, 'ComplexType']) -> str:  # type: ignore[no-redef]
        return value.to_sql() if isinstance(value, ComplexType) else value.value


class StructType(ComplexType):
    to_sql: ClassVar[Callable[..., str]]

    fields: dict[str, IcebergDataTypes | ComplexType]

    def to_sql(self) -> str:  # type: ignore[no-redef]
        return 'struct<{}>'.format(', '.join(f'{k}: {self._type_value(v)}' for k, v in self.fields.items()))


class MapType(ComplexType):
    to_sql: ClassVar[Callable[..., str]]

    key_type: IcebergDataTypes
    value_type: IcebergDataTypes | ComplexType

    def to_sql(self) -> str:  # type: ignore[no-redef]
        return f'map<{self.key_type.value}, {self._type_value(self.value_type)}>'


class ListType(ComplexType):
    to_sql: ClassVar[Callable[..., str]]

    element_type: IcebergDataTypes | ComplexType

    def to_sql(self) -> str:  # type: ignore[no-redef]
        return f'array<{self._type_value(self.element_type)}>'


class IcebergTableColumn(BaseModel):
    to_sql: ClassVar[Callable[..., str]]
    _to_sql_value: ClassVar[Callable[..., str]]

    cid: int
    name: str
    type: IcebergDataTypes | ComplexType
    notnull: int

    def to_sql(self) -> str:  # type: ignore[no-redef]
        statement = f'{self.name} {self.type_sql}'
        if self.notnull:
            statement += ' NOT NULL'

        return statement

    def _to_sql_value(self, value: Any) -> str:  # type: ignore[no-redef]
        if isinstance(value, str):
            return f"'{value}'"
        return str(value)

    @property
    def type_sql(self) -> str:
        if isinstance(self.type, ComplexType):
            return self.type.to_sql()

        if self.type == IcebergDataTypes.MAP:
            return 'map<string, string>'
        return self.type.value

    def __hash__(self) -> int:
        return hash(self.name)

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, IcebergTableColumn):
            return self.name == other.name
        return False


class IcebergTableColumnsSchema(BaseModel):
    to_sql: ClassVar[Callable[..., str]]

    columns: list['IcebergTableColumn']

    def to_sql(self) -> str:  # type: ignore[no-redef]
        columns_statement: list[str] = []

        for column in self.columns:
            columns_statement.append(column.to_sql())

        return ', '.join(columns_statement)
