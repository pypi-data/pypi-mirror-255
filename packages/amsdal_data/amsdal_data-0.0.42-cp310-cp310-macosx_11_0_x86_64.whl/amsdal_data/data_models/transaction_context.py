from typing import Any
from typing import Optional

from amsdal_utils.models.data_models.address import Address
from pydantic import BaseModel
from pydantic import Field

from amsdal_data.connections.enums import ModifyOperation


class TransactionContext(BaseModel):
    address: Address
    method_name: str
    execution_location: str
    arguments: dict[str, Any] | None = None
    return_value: Any | None = None
    changes: list[tuple[ModifyOperation, Address, dict[str, Any]]] = Field(default_factory=list)
    parent: Optional['TransactionContext'] = None

    @property
    def is_top_level(self) -> bool:
        return self.parent is None
