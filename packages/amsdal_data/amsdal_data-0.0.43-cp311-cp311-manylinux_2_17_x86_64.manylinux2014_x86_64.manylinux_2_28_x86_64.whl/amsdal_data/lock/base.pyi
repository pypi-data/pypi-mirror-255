import abc
from abc import ABC, abstractmethod
from amsdal_data.connections.base import Connectable as Connectable
from amsdal_utils.models.data_models.address import Address as Address
from typing import Any

class LockBase(Connectable, ABC, metaclass=abc.ABCMeta):
    @abstractmethod
    def acquire(self, target_address: Address, *, timeout_ms: int = -1, blocking: bool = True, metadata: dict[str, Any] | None = None) -> bool: ...
    @abstractmethod
    def release(self, target_address: Address) -> None: ...
