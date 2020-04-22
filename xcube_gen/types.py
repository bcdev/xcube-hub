from typing import Dict, Any, Mapping, Sequence, Union, Tuple

AnyDict = Dict[str, Any]

Error = Tuple[AnyDict, int]

JsonValue = Union[str, int, float, bool, type(None), Sequence, Mapping]
JsonObject = Mapping[str, JsonValue]


class Undefined:
    def __repr__(self):
        return 'undefined'

    def __str__(self):
        return 'undefined'


UNDEFINED = Undefined()
