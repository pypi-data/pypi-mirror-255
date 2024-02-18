import abc
from abc import ABC, abstractmethod
from amsdal_data.connections.base import ConnectionBase as ConnectionBase
from amsdal_utils.models.data_models.address import Address as Address
from typing import Any

class HistoricalConnectionBase(ConnectionBase, ABC, metaclass=abc.ABCMeta):
    @abstractmethod
    def put(self, address: Address, data: dict[str, Any]) -> None:
        """
        Adds/writes data to in scope of transaction.

        :param address: the address of the object
        :type address: Address
        :param data_type: the data type of the object
        :type data_type: DataTypes
        :param data: the object data to write
        :type data: dict[str, Any]
        :return: None
        """
