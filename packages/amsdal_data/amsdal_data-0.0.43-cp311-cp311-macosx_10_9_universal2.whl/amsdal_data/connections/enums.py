from enum import Enum


class ModifyOperation(str, Enum):
    CREATE = 'create'
    UPDATE = 'update'
    DELETE = 'delete'


class CoreResource(str, Enum):
    TRANSACTION = 'transaction'
    LOCK = 'lock'
