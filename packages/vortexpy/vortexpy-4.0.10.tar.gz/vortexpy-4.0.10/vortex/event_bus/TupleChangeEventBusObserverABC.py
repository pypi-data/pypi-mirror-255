from abc import ABCMeta, abstractmethod

from vortex.event_bus.TupleChangeEventABC import TupleChangeEventABC


class TupleChangeEventBusObserverABC(metaclass=ABCMeta):
    @abstractmethod
    def notifyFromBus(self, event: TupleChangeEventABC) -> None:
        raise NotImplementedError(
            "TupleChangeEventBusObserverABC.notifyFromBus"
        )
