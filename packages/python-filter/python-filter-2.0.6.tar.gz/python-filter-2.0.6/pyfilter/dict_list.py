from typing import Optional, Callable, Any
from pydantic import validate_call
from .list import ListFilter

class DictListFilter(ListFilter):
    @validate_call
    def __init__(self, items: list[dict]) -> None:
        super().__init__(items)
        self._items = items

    @validate_call
    def get_with_key_value(self, key, value: Any) -> Optional[dict]:
        for x in  self._items:

            if x[key] == value:
                return x

    @validate_call
    def sort_by_key(self, key: Any, reverse: bool = False) -> list[dict]:
        items_copy = self._items.copy()

        items_copy.sort(
            key = lambda x: x.get(key),
            reverse = reverse
        )

        return items_copy

    @validate_call
    def get_keys(self) -> list[Any]:
        keys = set()

        for dict_ in self._items:
            keys.update(dict_.keys())
            
        return list(keys)

    @validate_call
    def get_values(self) -> list[Any]:
        values = []

        for dict_ in self._items:
            values.extend(dict_.values())

        return values

    @validate_call
    def get_with_key(self, key) -> Optional[dict]:
        for x in  self._items:

            if key in x.keys():
                return x
    
    @validate_call
    def filter_with_key_values(self, key, values: list) -> list[dict]:
        dicts = []

        for value in values:
            for x in self._items:
                if x[key] == value:
                    dicts.append(x)

        return dicts

    @validate_call
    def filter_with_keys(self, keys: list) -> list[dict]:
        dicts = []

        for key in keys:
            for x in self._items:
                if key in x.keys():
                    dicts.append(x)

        return dicts

    @validate_call
    def filter_with_key_value(self, key, value) -> list[dict]:
        dicts = [ x for x in  self._items if x[key] == value ]
        return dicts

    @validate_call
    def filter_with_key(self, key) -> list[dict]:
        dicts = [ x for x in  self._items if key in x.keys() ]
        return dicts
    
    @validate_call
    def for_each_dict_pop_keys(self, keys: list) -> list[dict]:
        new_items = []

        for x in self._items:
            for key in keys:
                x.pop(key)

            new_items.append(x)

        return new_items

    @validate_call
    def merge_dicts(self) -> dict:
        new_dict = {}

        for x in self._items:
            for key in x.keys():
                if not key in new_dict.keys():
                    new_dict[key] = x[key]

                else:
                    raise Exception(f"Duplicate key: {key}")

        return new_dict

    @validate_call
    def categorize_dicts_by_key_value(self, key) -> dict[str, list]:
        dict_: dict[str, list] = {}

        for x in self._items:
            new_key = x[key]
            
            if new_key in dict_:
                dict_[new_key].append(x)

            else:
                dict_[new_key] = []
                dict_[new_key].append(x)

        return dict_

    @validate_call
    def map(self, func: Callable[[int, dict], Any]) -> list[dict]:
        results = super().map(func)
        return results

    @validate_call
    def for_each(self, func: Callable[[int, dict], Any]) -> None:
        super().for_each(func)

    @validate_call
    def filter(self, func: Callable[[int, dict], Any]) -> list[dict]:
        values = super().filter(func)
        return values

    @validate_call
    def find(self, func: Callable[[int, dict], Any]) -> Optional[dict]:
        result = super().find(func)
        return result

__all__ = [ "DictListFilter" ]