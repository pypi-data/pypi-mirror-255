import logging
from _weakrefset import WeakSet
from collections import defaultdict
from datetime import datetime
from typing import Optional, Type, Union

import pytz
from twisted.internet import reactor
from twisted.internet.defer import inlineCallbacks

from vortex.Tuple import Tuple
from vortex.TupleSelector import (
    TupleSelector,
    InvalidTupleSelectorNameException,
)
from vortex.handler.TupleChangeEventBusObserverABC import (
    TupleChangeEventBusObserverABC,
)

logger = logging.getLogger(__name__)


class TupleChangeEventBus:
    def __init__(self):
        self._weakObserversForAllTupleSelectorNames: WeakSet[
            TupleChangeEventBusObserverABC
        ] = WeakSet([])

        self._weakObserversBySelectorName: dict[
            str, WeakSet[TupleChangeEventBusObserverABC]
        ] = defaultdict(lambda: WeakSet([]))

    def notifyMany(self, tupleSelectors: list[TupleSelector]) -> None:
        for tupleSelector in tupleSelectors:
            self.notify(tupleSelector)

    def notify(self, tupleSelector: TupleSelector) -> None:
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
        the data that has changed, as close to the code that changes it as possible.

        Do not notify the bus of tuple selectors that need updating.

        Classes implementing TupleChangeEventBusObserverABC
        should observe changed data and themselves
        decide what tuple selectors they will
        notify their observers for.

        For example. If you have two tuple selectors:

        1) TupleSelector(MyTuple, {id:1})
        2) TupleSelector(ListOfMyTuples)

        TupleChangeEventBus.notify should be called for MyTuple
        just after changes are committed.

        TupleChangeEventBus.notify SHOULD NOT BE called for
        ListOfMyTuples

        A typical observer's method might look like this:

        ```python
            def notifyFromBus(self, tupleSelector: TupleSelector) -> None:
                if tupleSelector.isForTuple(MyTuple):
                    self.tupleDataObservable.notifyOfTupleUpdate(tupleSelector)
                    self.tupleDataObservable.notifyOfTupleUpdate(
                        TupleSelector(ListOfMyTuples)
                    )
                    return

                ...

        ```

        :param tupleSelector: The tuple selector that describes the tuple
        that has been changed. This change might be created, updated, or
        deleted.
        :return:
        """
        weakSets = [self._weakObserversForAllTupleSelectorNames]

        tupleSelectorName = TupleSelector.nameFromTuple(tupleSelector)

        if tupleSelectorName in self._weakObserversBySelectorName:
            weakSets.append(
                list(self._weakObserversBySelectorName[tupleSelectorName])
            )

        for weakSet in weakSets:
            for item in weakSet:
                if not item:
                    continue

                reactor.callLater(0, self._notify, item, tupleSelector)

    @inlineCallbacks
    def _notify(self, observable, tupleSelector):
        try:
            startDate = datetime.now(pytz.utc)
            yield observable.notifyFromBus(tupleSelector)

            # A blocking call taking more than 100ms is BAD
            # Otherwise a call taking more than a 1s is just poor performance.
            secondsTaken = (datetime.now(pytz.utc) - startDate).total_seconds()
            if 0.1 < secondsTaken:
                logger.debug(
                    "notifyFromBus took %s for %s, tupleSelector %s",
                    secondsTaken,
                    observable.__class__.__name__,
                    tupleSelector.toJsonStr(),
                )

        except Exception as e:
            logger.error(
                "Observable %s raised an error when being called with tupleSelector %s",
                observable.__class__.__name__,
                tupleSelector,
            )
            logger.exception(e)

    def addObserver(
        self,
        observer: TupleChangeEventBusObserverABC,
        tupleSelectorNameOrClass: Optional[
            Union[str, Type[Tuple], Tuple]
        ] = None,
    ) -> None:
        assert isinstance(
            observer, TupleChangeEventBusObserverABC
        ), "observer must be a TupleChangeEventBusObserverABC"

        if tupleSelectorNameOrClass is None:
            self._weakObserversForAllTupleSelectorNames.add(observer)
            return

        try:
            tupleSelectorName = TupleSelector.nameFromTuple(
                tupleSelectorNameOrClass
            )
        except InvalidTupleSelectorNameException:
            raise Exception(
                "tupleSelectorNameOrClass is not valid."
                " Maybe you need to add __tupleType__ to your custom TupleSelector class."
            )

        self._weakObserversBySelectorName[tupleSelectorName].add(observer)
