from typing import Dict, Any, Mapping, Sequence, Union

AnyDict = Dict[str, Any]

JsonValue = Union[str, int, float, bool, type(None), Sequence, Mapping]
JsonObject = Mapping[str, JsonValue]


class Undefined:
    def __repr__(self):
        return 'undefined'

    def __str__(self):
        return 'undefined'


UNDEFINED = Undefined()
