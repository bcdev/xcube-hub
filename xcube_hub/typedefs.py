from typing import Dict, Any, List, Tuple, Union

AnyDict = Dict[str, Any]

Error = Tuple[AnyDict, int]

JsonValue = Union[str, int, float, bool, type(None), Tuple, List, Dict]
JsonObject = Dict[str, JsonValue]


class Undefined:
    def __repr__(self):
        return 'undefined'

    def __str__(self):
        return 'undefined'


UNDEFINED = Undefined()
