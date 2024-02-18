"""
 * Created by Synerty Pty Ltd
 *
 * This software is open source, the MIT license applies.
 *
 * Website : http://www.synerty.com
 * Support : support@synerty.com
"""
import json
from typing import Dict, Optional, Union, Type

from vortex.Tuple import Tuple, addTupleType


class InvalidTupleSelectorNameException(Exception):
    pass


@addTupleType
class TupleSelector(Tuple):
    __tupleType__ = "vortex.TupleSelector"
    __slots__ = ["name", "selector"]

    # name: str = TupleField(comment="The tuple name this selector is for")
    # selector: Dict[str, Any] = TupleField(comment="The values to select")

    def __init__(
        self,
        name: Optional[Union[str, Type[Tuple], Tuple]] = None,
        selector: Optional[Dict] = None,
    ) -> None:
        Tuple.__init__(self)
        self.name = self.nameFromTuple(name)
        self.selector = selector if selector else {}

    def __eq__(self, y):
        return self.toJsonStr() == y.toJsonStr()

    def __hash__(self):
        return hash(self.toJsonStr())

    # noinspection PyMethodMayBeStatic
    @classmethod
    def nameFromTuple(
        cls, nameOrTuple: Optional[Union[str, Type[Tuple], Tuple]]
    ) -> Optional[str]:
        # When the TupleSelector is reconstructed / deserialised, it's constructed with
        # no arguments
        if nameOrTuple is None:
            return None

        if isinstance(nameOrTuple, str):
            name = nameOrTuple

        elif isinstance(nameOrTuple, Tuple):
            name = nameOrTuple.tupleType()

        elif issubclass(nameOrTuple, Tuple):
            name = nameOrTuple.tupleType()

        else:
            raise Exception(
                "Argument should be of type Union[str, Type[Tuple], Tuple]"
            )

        if name == TupleSelector.tupleName():
            raise InvalidTupleSelectorNameException(
                "We've found the name of TupleSelector.tupleType(),"
                "which means we've been passed a TupleSelector."
            )

        return name

    def isForTuple(
        self, nameOrTuple: Optional[Union[str, Type[Tuple], Tuple]]
    ) -> bool:
        return self.name == self.nameFromTuple(nameOrTuple)

    def toJsonStr(self) -> str:
        """To Json Str

        This method dumps the c{TupleSelector} data to a json string.

        It sorts the dict keys and
        """
        fieldJsonDict = self.toJsonField(self.selector)
        return json.dumps(
            {"name": self.name, "selector": fieldJsonDict}, sort_keys=True
        )

    @classmethod
    def fromJsonStr(cls, jsonStr: str) -> "TupleSelector":
        """From Json Str

        This method creates a new c{TupleSelector} from the ordered json string dumped
        from .toJsonStr

        """
        data = json.loads(jsonStr)
        newTs = TupleSelector(name=data["name"], selector={})
        newTs.selector = newTs.fromJsonField(data["selector"])
        return newTs

    def __repr__(self):
        return self.toJsonStr()
