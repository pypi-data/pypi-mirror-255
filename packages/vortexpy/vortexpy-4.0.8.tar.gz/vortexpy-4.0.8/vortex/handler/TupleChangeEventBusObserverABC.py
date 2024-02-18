from abc import ABCMeta, abstractmethod

from vortex.TupleSelector import TupleSelector


class TupleChangeEventBusObserverABC(metaclass=ABCMeta):
    @abstractmethod
    def notifyFromBus(
        self,
        tupleSelector: TupleSelector,
    ) -> None:
        pass
