from typing import Any

from amsdal_utils.query.data_models.order_by import OrderBy
from amsdal_utils.query.enums import OrderDirection


def get_nested_value(item: dict[str, Any], field_name: str) -> Any:
    keys = field_name.split('__')
    value = item
    for key in keys:
        value = value.get(key, None)
        if value is None:
            break
    return value


def sort_items(items: list[dict[str, Any]], order_by_list: list[OrderBy] | None) -> list[dict[str, Any]]:
    if not order_by_list:
        return items

    for order_by in reversed(order_by_list):
        items.sort(
            key=lambda item: get_nested_value(item, order_by.field_name) or 0,
            reverse=(order_by.direction == OrderDirection.DESC),
        )
    return items
