from abc import ABC
from abc import abstractmethod
from typing import Any

from amsdal_utils.models.data_models.address import Address

from amsdal_data.connections.base import ConnectionBase


class HistoricalConnectionBase(ConnectionBase, ABC):
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
        ...
