from _typeshed import Incomplete
from amsdal_data.data_models.lock_object import LockObject as LockObject
from amsdal_data.lock.base import LockBase as LockBase
from amsdal_utils.models.data_models.address import Address as Address
from typing import Any

class ThreadLock(LockBase):
    """
    A thread lock implementation of the LockBase class.
    """
    def connect(self, *args: Any, **kwargs: Any) -> None: ...
    def disconnect(self) -> None: ...
    locks: Incomplete
    lock_data: Incomplete
    def __init__(self) -> None: ...
    def acquire(self, target_address: Address, *, timeout_ms: int = -1, blocking: bool = True, metadata: dict[str, Any] | None = None) -> bool:
        """
        Acquire the lock for a specific target (resource) with optional timeout, blocking and metadata parameters.

        :param target_address: The target address to acquire the lock for.
        :type target_address: Address
        :param timeout_ms: The timeout in milliseconds.
        :type timeout_ms: int
        :param blocking: Whether to block until the lock is acquired.
        :type blocking: bool
        :param metadata: The metadata to store with the lock.
        :type metadata: dict[str, Any]
        :return: Whether the lock was acquired.
        :rtype: bool
        """
    def release(self, target_address: Address) -> None:
        """
        Release the lock for a specific target (resource).

        There is no return value.

        :param target_address: The target address to release the lock for.
        :type target_address: Address
        :raises RuntimeError: If the lock is not acquired.
        :return: None
        """
