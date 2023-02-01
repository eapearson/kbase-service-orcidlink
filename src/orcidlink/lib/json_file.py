import json
import os
from pathlib import Path
from typing import Any, Dict, List, Tuple, Union

from orcidlink.lib import utils

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


def get_json_file_path(name: str) -> str:
    root_path = Path(os.path.join(utils.module_dir(), "data"))
    if not root_path.exists():
        raise IOError("Root directory does not exist")

    filename = f"{name}.json"

    file_path = os.path.join(root_path, filename)

    if not Path(file_path).exists():
        raise IOError("File does not exist")

    return file_path


def get_json_file(name: str) -> Any:
    file_path = get_json_file_path(name)
    with open(file_path, "r") as db_file:
        return json.load(db_file)
