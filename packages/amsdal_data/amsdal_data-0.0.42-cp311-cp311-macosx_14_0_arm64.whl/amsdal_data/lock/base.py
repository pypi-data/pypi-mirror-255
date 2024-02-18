from abc import ABC
from abc import abstractmethod
from typing import Any

from amsdal_utils.models.data_models.address import Address

from amsdal_data.connections.base import Connectable


class LockBase(Connectable, ABC):
    @abstractmethod
    def acquire(
        self,
        target_address: Address,
        *,
        timeout_ms: int = -1,
        blocking: bool = True,
        metadata: dict[str, Any] | None = None,
    ) -> bool: ...

    @abstractmethod
    def release(self, target_address: Address) -> None: ...
