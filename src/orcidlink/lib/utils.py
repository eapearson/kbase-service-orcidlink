from __future__ import annotations

import os
import time
from datetime import datetime, timezone


def module_dir() -> str:
    my_dir = os.path.dirname(__file__)
    return os.path.realpath(os.path.join(my_dir, "../../.."))


# JSONLike = Union['JSONLikeDict', 'JSONLikeArray', int, str, bool, None]
#
# JSONLikeDict = Dict[str, JSONLike]
# JSONLikeArray = List[JSONLike]


# def get_prop(value: JSONLikeDict, path: List[str | int]) -> Tuple[JSONLike, bool]:
#     temp: JSONLike = value
#     for name in path:
#         if isinstance(temp, dict):
#             if isinstance(name, str):
#                 temp = temp.get(name)
#                 if temp is None:
#                     return None, False
#             else:
#                 raise ValueError('Path element not str')
#         elif isinstance(temp, list):
#             if isinstance(name, int):
#                 if name >= len(temp) or name < 0:
#                     return None, False
#                 temp = temp[name]
#             else:
#                 raise ValueError('Path element not int')
#     return temp, True
#
#
# def set_prop(value: JSONLikeDict, path: List[str | int], new_value: JSONLike) -> None:
#     temp: JSONLike = value
#     *head, tail = path
#     for name in head:
#         if isinstance(temp, dict):
#             if isinstance(name, str):
#                 if name not in temp:
#                     raise ValueError(
#                         f"Cannot set prop; path element '{name}' not not str for dict"
#                     )
#                 temp = temp.get(name)
#             else:
#                 f"Cannot set prop; cannot path element '{name}' not str for dict"
#         elif isinstance(temp, list):
#             if isinstance(name, int):
#                 if name >= len(temp) or name < 0:
#                     raise ValueError(
#                         f"Cannot set prop; cannot get path element '{name}' in array"
#                     )
#                 temp = temp[name]
#             else:
#                 raise ValueError(
#                     f"Cannot set prop; path element '{name}' not not int for array"
#                 )
#         else:
#             raise ValueError("Cannot set prop; reached leaf too early")
#
#     # should be on a leaf node. what is it?
#     if isinstance(temp, dict):
#         if isinstance(tail, str):
#             if tail not in temp:
#                 raise ValueError(
#                     f"Cannot set prop; cannot get leaf element '{tail}' in dict"
#                 )
#             temp[tail] = new_value
#         else:
#             f"Cannot set prop; cannot path element '{name}' not str for dict"
#     elif isinstance(temp, list):
#         if isinstance(tail, int):
#             if tail >= len(temp) or tail < 0:
#                 raise ValueError(
#                     f"Cannot set prop; cannot get leaf element '{tail}' in array"
#                 )
#             temp[tail] = new_value
#         else:
#             raise ValueError(
#                 f"Cannot set prop; leaf path element '{tail}' is not int for array"
#             )
#     else:
#         raise ValueError("Cannot set prop; leaf is not a dict or list")
#
#
# def get_raw_prop(value: JSONLikeDict, path: List[str | int], default_value=JSONLike) -> JSONLike:
#     found_value, found = get_prop(value, path)
#     if found:
#         return found_value
#     return default_value
#
#
# def get_string_prop(value: JSONLikeDict, path: List[str | int], default_value: str | None = None) -> str | None:
#     found_value, found = get_prop(value, path)
#     if found:
#         return str(found_value)
#     return default_value
#
#
# def get_int_prop(value: JSONLikeDict, path: List[str | int], default_value: int | None = None) -> int | None:
#     found_value, found = get_prop(value, path)
#     if found:
#         return int(found_value)
#     return default_value


def current_time_millis() -> int:
    return int(round(time.time() * 1000))


def epoch_time_millis() -> int:
    epoch_time = datetime.now(tz=timezone.utc).timestamp()
    return int(epoch_time * 1000)


def make_date(
    year: int | None = None, month: int | None = None, day: int | None = None
) -> str:
    if year is not None:
        if month is not None:
            if day is not None:
                return f"{year}/{month}/{day}"
            else:
                return f"{year}/{month}"
        else:
            return f"{year}"
    else:
        return "** invalid date **"
