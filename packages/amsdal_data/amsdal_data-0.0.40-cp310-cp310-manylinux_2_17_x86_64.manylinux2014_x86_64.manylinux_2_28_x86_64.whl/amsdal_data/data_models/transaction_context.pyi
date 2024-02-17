from amsdal_data.connections.enums import ModifyOperation as ModifyOperation
from amsdal_utils.models.data_models.address import Address as Address
from pydantic import BaseModel
from typing import Any, Optional

class TransactionContext(BaseModel):
    address: Address
    method_name: str
    execution_location: str
    arguments: dict[str, Any] | None
    return_value: Any | None
    changes: list[tuple[ModifyOperation, Address, dict[str, Any]]]
    parent: Optional['TransactionContext']
    @property
    def is_top_level(self) -> bool: ...
