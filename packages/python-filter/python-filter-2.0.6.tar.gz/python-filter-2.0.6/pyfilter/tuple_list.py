from typing import Optional, Callable, Any
from pydantic import validate_call

from .list import ListFilter

class TupleListFilter(ListFilter):
    @validate_call
    def __init__(self, items: list[tuple]) -> None:
        super().__init__(items)
        self._items = items

    @validate_call
    def get_with_value(self, value: Any) -> Optional[tuple]:
        for x in self._items:
            if value in x:
                return x

    @validate_call
    def filter_with_value(self, value: Any) -> list[tuple]:
        tuples = [x for x in self._items if value in x]
        return tuples

    @validate_call
    def get_with_index(self, index: int) -> Optional[tuple]:
        if 0 <= index < len(self._items):
            return self._items[index]

    @validate_call
    def filter_with_indexes(self, indexes: list[int]) -> list[tuple]:
        tuples = [ self._items[index] for index in indexes if 0 <= index < len(self._items) ]
        return tuples

    @validate_call
    def map(self, func: Callable[[int, tuple], Any]) -> list[tuple]:
        results = super().map(func)
        return results

    @validate_call
    def for_each(self, func: Callable[[int, tuple], Any]) -> None:
        super().for_each(func)

    @validate_call
    def filter(self, func: Callable[[int, tuple], Any]) -> list[tuple]:
        values = super().filter(func)
        return values

    @validate_call
    def find(self, func: Callable[[int, tuple], Any]) -> Optional[tuple]:
        result = super().find(func)
        return result

__all__ = [ "TupleListFilter" ]