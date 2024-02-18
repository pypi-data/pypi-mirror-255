from typing import Optional, Callable, Any, Self
from pydantic import validate_call
import json

class ListFilter:
    @validate_call
    def __init__(self, items: list) -> None:
        self._items = items

    @validate_call
    def get_with_value(self, value: Any) -> Optional[Any]:
        for x in self._items:
            if value in x:
                return x

    @validate_call
    def reverse(self) -> list[Any]:
        items_copy = self._items.copy()
        items_copy.reverse()
        return items_copy

    @validate_call
    def to_json(self, ident: Optional[int] = None
    ) -> str:
        return json.dumps(
            self._items,
            indent = ident
        )

    @classmethod
    @validate_call
    def from_json(cls, json_text: str) -> Self:
        return cls(json.loads(json_text))

    @validate_call
    def map(self, func: Callable[[int, Any], Any]) -> list[Any]:
        results = []

        for i, value in enumerate(self._items):
            result = func(i, value)
            results.append(result)

        return results

    @validate_call
    def for_each(self, func: Callable[[int, Any], Any]) -> None:
        for i, value in enumerate(self._items):
            func(i, value)

    @validate_call
    def filter(self, func: Callable[[int, Any], Any]) -> list[Any]:
        values = []

        for i, value in enumerate(self._items):
            is_valid = func(i, value)

            if is_valid:
                values.append(value)

        return values

    @validate_call
    def find(self, func: Callable[[int, Any], Any]) -> Optional[Any]:
        for i, value in enumerate(self._items):
            is_valid = func(i, value)

            if is_valid:
                return value

    @property
    def length(self) -> int:
        return len(self._items)

__all__ = [ "ListFilter" ]