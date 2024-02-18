import json

from sqlalchemy import TypeDecorator, JSON
from typing import Any

from vortex.Tuple import Tuple


class VortexTupleJSON(TypeDecorator):
    impl = JSON()

    def __init__(self, TupleClass, *args: Any, **kwargs: Any):
        super().__init__(self, *args, **kwargs)
        self._TupleClass = TupleClass

    def process_bind_param(self, value: Tuple, dialect):
        return json.dumps(value.tupleToRestfulJsonDict())

    def process_result_value(self, value, dialect):
        valueDict = json.loads(value)

        return Tuple.restfulJsonDictToTupleWithValidation(
            valueDict, self._TupleClass
        )
