from enum import Enum

class ModifyOperation(str, Enum):
    CREATE: str
    UPDATE: str
    DELETE: str

class CoreResource(str, Enum):
    TRANSACTION: str
    LOCK: str
