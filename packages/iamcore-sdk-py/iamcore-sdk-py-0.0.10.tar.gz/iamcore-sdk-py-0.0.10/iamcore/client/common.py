from enum import Enum
import re
from typing import Any, Generator, TypeVar, Generic, List, Type

from iamcore.irn import IRN

from iamcore.client.exceptions import IAMException


def to_snake_case(field_name: str) -> str:
    return re.sub(r'([a-z0-9])([A-Z])', r'\1_\2', field_name).lower()


def to_dict(obj):
    if isinstance(obj, dict):
        data = {}
        for (k, v) in obj.items():
            data[k] = to_dict(v)
        return data
    elif isinstance(obj, IRN):
        return str(obj)
    elif hasattr(obj, "__iter__") and not isinstance(obj, str):
        return [to_dict(v) for v in obj]
    elif hasattr(obj, "__dict__"):
        data = dict([(key, to_dict(value))
                     for key, value in obj.__dict__.items()
                     if not callable(value) and not key.startswith('_')])
        return data
    else:
        return obj


def generic_search_all(auth_headers: dict[str, str], func, *vargs, **kwargs) -> Generator[Any, None, None]:
    if "page" in kwargs.keys():
        kwargs.pop("page")
    new_results = True
    page = 1
    cnt = 0
    while new_results:
        resp = func(auth_headers, *vargs, page=page, **kwargs)
        if not resp.data:
            break
        for d in resp.data:
            yield d
            cnt += 1
        new_results = cnt < resp.count
        page += 1


class SortOrder(Enum):
    asc = 1
    desc = 2


T = TypeVar('T')


class IamEntityResponse(Generic[T]):
    data: T

    def __init__(self, base_class: Type[T], data: dict):
        if isinstance(data, base_class):
            self.data = data
        elif isinstance(data, dict):
            self.data = base_class(**data)


class IamEntitiesResponse(Generic[T]):
    data: List[T]
    count: int
    page: int
    page_size: int

    def __init__(self, base_class: Type[T], data: List[dict], **kwargs):
        if not isinstance(data, list):
            raise IAMException(f"Unexpected response format")

        self.data = [
            base_class.of(item)
            for item in data
        ]

        for k, v in kwargs.items():
            attr = to_snake_case(k)
            setattr(self, attr, v)
