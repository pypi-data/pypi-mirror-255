import abc
from abc import ABC, abstractmethod
from amsdal_data.connections.base import ConnectionBase as ConnectionBase
from amsdal_utils.models.data_models.address import Address as Address
from typing import Any

class StateConnectionBase(ConnectionBase, ABC, metaclass=abc.ABCMeta):
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
    @abstractmethod
    def delete(self, address: Address) -> None:
        """
        Deletes data to in scope of transaction.

        :param address: the address of the object
        :type address: Address
        :return: None
        """
