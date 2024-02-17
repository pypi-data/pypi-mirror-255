from abc import ABC
from abc import abstractmethod
from typing import Any

from amsdal_utils.models.data_models.address import Address

from amsdal_data.connections.base import ConnectionBase


class StateConnectionBase(ConnectionBase, ABC):
    @abstractmethod
    def insert(self, address: Address, data: dict[str, Any]) -> None:
        """
        Inserts data to in scope of transaction.

        :param address: the address of the object
        :type address: Address
        :param data: the object data to write
        :type data: dict[str, Any]
        :return: None
        """
        ...

    @abstractmethod
    def update(self, address: Address, data: dict[str, Any]) -> None:
        """
        Updates data to in scope of transaction.

        :param address: the address of the object
        :type address: Address
        :param data: the object data to write
        :type data: dict[str, Any]
        :return: None
        """
        ...

    @abstractmethod
    def delete(self, address: Address) -> None:
        """
        Deletes data to in scope of transaction.

        :param address: the address of the object
        :type address: Address
        :return: None
        """
        ...
