from typing import Dict, List, Union

JSONLike = Union["JSONLikeObject", "JSONLikeArray", int, str, bool]

JSONLikeObject = Dict[str, JSONLike]
JSONLikeArray = List[JSONLike]

JSONLikeCollection = JSONLikeObject | JSONLikeArray
