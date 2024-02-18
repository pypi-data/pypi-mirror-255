import json
from abc import ABCMeta


class TupleChangeEventABC(metaclass=ABCMeta):
    __eventType__ = None

    @classmethod
    def eventType(cls) -> str:
        return cls.__eventType__

    def __repr__(self):
        return json.dumps(
            {"class": self.__class__.__name__, "fields": self.__dict__}
        )
