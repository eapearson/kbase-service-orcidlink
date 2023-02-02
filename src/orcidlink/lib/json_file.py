from typing import Dict, List, Tuple, Union

JSONLike = Union["JSONLikeObject", "JSONLikeArray", int, str, bool, None]

JSONLikeObject = Dict[str, JSONLike]
JSONLikeArray = List[JSONLike]


def get_prop(value: JSONLikeObject, path: List[str | int]) -> Tuple[JSONLike, bool]:
    temp: JSONLike = value
    for name in path:
        if isinstance(temp, dict):
            if isinstance(name, str):
                temp = temp.get(name)
                if temp is None:
                    return None, False
            else:
                raise ValueError("Path element not str")
        elif isinstance(temp, list):
            if isinstance(name, int):
                if name >= len(temp) or name < 0:
                    return None, False
                temp = temp[name]
            else:
                raise ValueError("Path element not int")
    return temp, True
