import logging
from _weakrefset import WeakSet
from collections import defaultdict
from datetime import datetime
from typing import Optional, Type, Union

import pytz
from twisted.internet import reactor
from twisted.internet.defer import inlineCallbacks

from vortex.TupleSelector import TupleSelector
from vortex.event_bus.TupleChangeEventABC import TupleChangeEventABC
from vortex.event_bus.TupleChangeEventBusObserverABC import (
    TupleChangeEventBusObserverABC,
)

logger = logging.getLogger(__name__)


class TupleChangeEventBus:
    def __init__(self):
        self._weakObserversForAllTupleChangeEventABCNames: WeakSet[
            TupleChangeEventBusObserverABC
        ] = WeakSet([])

        self._weakObserversBySelectorName: dict[
            str, WeakSet[TupleChangeEventBusObserverABC]
        ] = defaultdict(lambda: WeakSet([]))

    def notifyMany(self, events: list[TupleChangeEventABC]) -> None:
        for event in events:
            self.notify(event)

    def notify(self, event: TupleChangeEventABC) -> None:
        """
        Notify

        Notify the bus of a change to a tuple.

        This bus does not automatically call
        TupleDataObservableHandler.notifyOfTupleUpdate(...)
        that must be done by classes implementing
        TupleChangeEventBusObserverABC

        IMPORTANT: You can use this bus for whatever you like,
        however, see best practices.

        BEST PRACTICE: Only notify the bus of precisely
        the data that has changed, as close to the code that changes it as
         possible.

        Do not notify the bus of tuple selectors that need updating.

        Classes implementing TupleChangeEventBusObserverABC
        should observe changed data and themselves
        decide what tuple selectors they will
        notify their observers for.

        For example. If you have two tuple selectors:

        1) TupleChangeEventABC(MyTuple, {id:1})
        2) TupleChangeEventABC(ListOfMyTuples)

        TupleChangeEventBus.notify should be called for MyTuple
        just after changes are committed.

        TupleChangeEventBus.notify SHOULD NOT BE called for
        ListOfMyTuples

        A typical observer's method might look like this:

        ```python
            def notifyFromBus(self, event: TupleChangeEventABC) -> None:
                if event.isForTuple(MyTuple):
                    self.tupleDataObservable.notifyOfTupleUpdate(event)
                    self.tupleDataObservable.notifyOfTupleUpdate(
                        TupleChangeEventABC(ListOfMyTuples)
                    )
                    return

                ...

        ```

        :param event: The tuple selector that describes the tuple
        that has been changed. This change might be created, updated, or
        deleted.
        :return:
        """
        weakSets = [self._weakObserversForAllTupleChangeEventABCNames]

        eventName = event.eventType()

        if eventName in self._weakObserversBySelectorName:
            weakSets.append(list(self._weakObserversBySelectorName[eventName]))

        for weakSet in weakSets:
            for item in weakSet:
                if not item:
                    continue

                # noinspection PyUnresolvedReferences
                reactor.callLater(0, self._notify, item, event)

    @inlineCallbacks
    def _notify(
        self,
        observable: TupleChangeEventBusObserverABC,
        event: TupleChangeEventABC,
    ):
        try:
            startDate = datetime.now(pytz.utc)
            yield observable.notifyFromBus(event)

            # A blocking call taking more than 100ms is BAD
            # Otherwise a call taking more than a 1s is just poor performance.
            secondsTaken = (datetime.now(pytz.utc) - startDate).total_seconds()
            if 0.1 < secondsTaken:
                logger.debug(
                    "notifyFromBus took %s for %s, event %s",
                    secondsTaken,
                    observable.__class__.__name__,
                    event,
                )

        except Exception as e:
            logger.error(
                "Observable %s raised an error"
                " when being called with event %s",
                observable.__class__.__name__,
                event,
            )
            logger.exception(e)

    def addObserver(
        self,
        observer: TupleChangeEventBusObserverABC,
        eventNameOrClass: Optional[
            Union[
                str,
                Type[TupleChangeEventABC],
                TupleChangeEventABC,
            ]
        ] = None,
    ) -> None:
        assert isinstance(
            observer, TupleChangeEventBusObserverABC
        ), "observer must be a TupleChangeEventBusObserverABC"

        if eventNameOrClass is None:
            self._weakObserversForAllTupleChangeEventABCNames.add(observer)
            return

        eventName = self._nameFromEvent(eventNameOrClass)

        self._weakObserversBySelectorName[eventName].add(observer)

    # noinspection PyMethodMayBeStatic
    def _nameFromEvent(
        self,
        nameOrTuple: Optional[
            Union[str, Type[TupleChangeEventABC], TupleChangeEventABC]
        ],
    ) -> Optional[str]:
        # When the TupleSelector is reconstructed / deserialize,
        # it's constructed with
        # no arguments
        if nameOrTuple is None:
            return None

        if isinstance(nameOrTuple, str):
            name = nameOrTuple

        elif isinstance(nameOrTuple, TupleChangeEventABC):
            name = nameOrTuple.eventType()

        elif issubclass(nameOrTuple, TupleChangeEventABC):
            name = nameOrTuple.eventType()

        else:
            raise Exception(
                "Argument should be of type "
                "Union[str, Type[TupleChangeEventABC], TupleChangeEventABC]"
            )

        if name == TupleSelector.tupleName():
            raise Exception(
                "We've found the name of TupleSelector.tupleType(),"
                "which means we've been passed a TupleSelector."
            )

        return name
