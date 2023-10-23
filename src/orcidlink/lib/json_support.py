from types import NoneType
from typing import Any, Dict, List, Tuple, cast

# JSONString = str
# JSONNumber = Union[int, float]
# JSONBoolean = bool
# JSONNull = NoneType
# # JSONArray = ForwardRef('JSONArray')
# # JSONObject = ForwardRef('JSONObject')
# # JSONValue = JSONString | JSONNumber | JSONBoolean | JSONNull | 'JSONArray' | 'JSONObject'
# JSONValue = Union[JSONString, JSONNumber, JSONBoolean, JSONNull , 'JSONArray', 'JSONObject']
# JSONArray = list[JSONValue]
# JSONObject = dict[JSONString, JSONValue]

JSONValue = (
    str | int | float | bool | NoneType | List["JSONValue"] | Dict[str, "JSONValue"]
)

JSONObject = Dict[str, JSONValue]

JSONArray = List[JSONValue]


def as_json_object(value: Any) -> JSONObject:
    if isinstance(value, dict):
        return cast(value, JSONObject)
    else:
        raise ValueError("Not a JSON object")


def json_path(value: JSONValue, path: List[str | int]) -> Tuple[bool, JSONValue]:
    """
    Dig into a JSON Object or Array to locate the element on the path.
    """
    temp = value
    for element in path:
        if isinstance(element, str):
            if isinstance(temp, dict):
                if element in temp:
                    temp = temp[element]
                else:
                    return False, None
            else:
                return False, None
        else:
            if isinstance(temp, list):
                if element in temp:
                    temp = temp[element]
                else:
                    return False, None
            else:
                return False, None
    return True, temp


# Okay, try again but crude.

# JSONObject = dict[str, Any]
# JSONArray = list[Any]
# JSONValue = str | int | float | NoneType | JSONObject | JSONArray
