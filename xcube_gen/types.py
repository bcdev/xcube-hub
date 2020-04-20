from typing import Dict, Any

AnyDict = Dict[str, Any]


class Undefined:
    def __repr__(self):
        return 'undefined'

    def __str__(self):
        return 'undefined'


UNDEFINED = Undefined()
