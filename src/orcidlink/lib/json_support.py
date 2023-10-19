from types import NoneType
from typing import Any, Dict, List

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

# Okay, try again but crude.

JSONObject = dict[str, Any]
JSONArray = list[Any]
JSONValue = str | int | float | NoneType | JSONObject | JSONArray
