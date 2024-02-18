import asyncio
import inspect
import json
import os
from collections.abc import Callable
from functools import wraps
from typing import Any

from amsdal_utils.models.data_models.address import Address
from amsdal_utils.models.enums import Versions
from amsdal_utils.utils.identifier import get_identifier

from amsdal_data.connections.enums import CoreResource
from amsdal_data.data_models.transaction_context import TransactionContext
from amsdal_data.transactions.constants import TRANSACTION_CLASS_NAME


def transaction(name: str | Callable[..., Any] | None = None, **transaction_kwargs: Any) -> Callable[..., Any]:
    def _transaction(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Callable[..., Any]:
            with TransactionFlow(func, *args, transaction_kwargs=transaction_kwargs, **kwargs) as transaction_flow:
                result = func(*args, **kwargs)
                transaction_flow.set_return_value(result)
                return result

        @wraps(func)
        async def async_wrapper(*args: Any, **kwargs: Any) -> Callable[..., Any]:
            with TransactionFlow(func, *args, transaction_kwargs=transaction_kwargs, **kwargs) as transaction_flow:
                result = await func(*args, **kwargs)
                transaction_flow.set_return_value(result)
                return result

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return wrapper

    if name is None:
        return _transaction
    elif isinstance(name, str):
        _transaction.__transaction_name__ = name  # type: ignore[attr-defined]
        transaction_kwargs['label'] = name
        return _transaction

    return _transaction(name)


class TransactionFlow:
    def __init__(self, func: Callable[..., Any], *args: Any, transaction_kwargs: dict[str, Any], **kwargs: Any) -> None:
        self.return_value: Any = None
        self.context = TransactionContext(
            address=Address(
                resource=CoreResource.TRANSACTION,
                class_name=TRANSACTION_CLASS_NAME,
                class_version=Versions.LATEST,
                object_id=get_identifier(),
                object_version=Versions.LATEST,
            ),
            method_name=func.__name__,
            execution_location=os.path.abspath(inspect.getfile(func)),
            arguments=self._serialize_arguments({'args:': args, 'kwargs': kwargs}),
        )
        self.transaction_kwargs: dict[str, Any] = transaction_kwargs

        if 'label' not in self.transaction_kwargs:
            self.transaction_kwargs['label'] = func.__name__

    def __enter__(self) -> 'TransactionFlow':
        from amsdal_data.manager import AmsdalDataManager

        transaction_manager = AmsdalDataManager().get_transaction_manager()
        transaction_manager.begin(self.context, self.transaction_kwargs)
        return self

    def set_return_value(self, value: Any) -> None:
        self.return_value = value

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        from amsdal_data.manager import AmsdalDataManager

        data_manager = AmsdalDataManager()

        if exc_type is not None:
            transaction_manager = data_manager.get_transaction_manager()
            transaction_manager.rollback()
        else:
            transaction_manager = data_manager.get_transaction_manager()
            transaction_manager.commit(self.return_value)

    def _serialize_arguments(self, data: Any) -> Any:
        if isinstance(data, dict):
            return {self._serialize_arguments(k): self._serialize_arguments(v) for k, v in data.items()}
        elif isinstance(data, list | tuple | set):
            return [self._serialize_arguments(x) for x in data]

        try:
            json.dumps(data)
            return data
        except Exception:
            return str(data)
