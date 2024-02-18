"""
 * Created by Synerty Pty Ltd
 *
 * This software is open source, the MIT license applies.
 *
 * Website : https://www.synerty.com
 * Support : support@synerty.com
"""
import logging
from typing import Dict
from typing import Type
from typing import Union

from twisted.internet.defer import Deferred
from twisted.internet.defer import inlineCallbacks

from vortex.Payload import Payload
from vortex.PayloadEnvelope import PayloadEnvelope
from vortex.TupleAction import TupleActionABC
from vortex.TupleActionVortex import TupleActionVortex
from vortex.TupleSelector import TupleSelector
from vortex.data_loader.TupleDataLiveLockManager import (
    TupleDataLiveLockManager,
)
from vortex.data_loader.TupleDataLoaderDelegate import (
    TupleDataLoaderDelegateABC,
)
from vortex.data_loader.TupleDataLoaderTupleABC import TupleDataLoaderTupleABC
from vortex.data_loader.TupleDataLoaderTuples import (
    _DataLoaderTupleAction,
    _LockDataTupleAction,
    _DataLockStatusTuple,
    _DataLoaderTupleActionResponseTuple,
)
from vortex.handler.TupleActionProcessor import TupleActionProcessor
from vortex.handler.TupleActionProcessor import TupleActionProcessorDelegateABC
from vortex.handler.TupleDataObservableHandler import TupleDataObservableHandler
from vortex.handler.TupleDataObservableHandler import TuplesProviderABC

logger = logging.getLogger(__name__)


class TupleDataLoader(TupleActionProcessorDelegateABC, TuplesProviderABC):
    """Tuple Data Loader

    The `TupleDataLoader class is responsible for maintaining the
    `TupleDataObservableHandler` and `TupleActionProcessor` pair for each module
    which uses TupleForms. Forms (`Tuple`) and their corresponding
    delegate (`TupleDataLoaderDelegateABC`) are registered with the modules form loader
    using the `setDelegate` method. `TupleDataLoader`s lifecycle should be
    managed with the `shutdown` method in the UI controllers
    `shutdown` method. The `TupleDataLoader` can (should??) be initialized in
    the `start` method of the UI controller.

    Each instance of the `TupleDataLoader` registers itself as the delegate for
    every form (which itself is a `TupleActionABC`) registered with it. The
    `TupleDataLoaderDelegateABC` methods are used for handling reads and writes.

    TODO: Locking

    """

    def __init__(
        self,
        observable: TupleDataObservableHandler,
        actionProcessor: TupleActionProcessor,
    ):
        self._observable = observable
        self._actionProcessor = actionProcessor
        self._lockManager = TupleDataLiveLockManager()

        self._registeredDataDelegateByDataType: Dict[
            str, TupleDataLoaderDelegateABC
        ] = {}

        self._lockingUuidByTs: Dict[TupleSelector, str] = {}

    def start(self):
        """Start

        Start all registered handlers

        """
        self._lockManager.start(self._observable)

        self._observable.addTupleProvider(
            _DataLockStatusTuple.tupleType(), self
        )

        self._actionProcessor.setDelegate(
            _DataLoaderTupleAction.tupleType(),
            self,
        )
        self._actionProcessor.setDelegate(
            _LockDataTupleAction.tupleType(), self
        )

        for entry in self._registeredDataDelegateByDataType.values():
            entry.start()

    def shutdown(self) -> None:
        """Shutdown

        Shutdown the observable and action processor managed with this
        TupleDataLoader and the registered handlers

        :return: None
        """
        for tupleDataType, delegate in list(
            self._registeredDataDelegateByDataType.items()
        ):
            delegate.shutdown()
            self._registeredDataDelegateByDataType.pop(tupleDataType)

        self._lockManager.shutdown()
        self._observable.shutdown()
        self._actionProcessor.shutdown()

    def setDelegate(
        self,
        DataTuple: Union[Type[TupleDataLoaderTupleABC], str],
        delegate: TupleDataLoaderDelegateABC,
    ) -> None:
        """Set Delegate

        Sets `self` as the delegate for `DataClass` which is a TupleActionABC
        and registers `handler` as the form data handler for `FormClass` which
        is used for reading and writing the data

        :param DataTuple: `Tuple` to register the handler for
        :param delegate: Instance of `TupleDataLoaderDelegateABC` that provides R/W
        :return: None
        """
        tupleType = (
            DataTuple if isinstance(DataTuple, str) else DataTuple.tupleType()
        )

        self._observable.addTupleProvider(tupleType, self)
        self._registeredDataDelegateByDataType[tupleType] = delegate

    @inlineCallbacks
    def makeVortexMsg(
        self, filt: dict, tupleSelector: TupleSelector
    ) -> Union[Deferred, bytes]:
        if tupleSelector.name == _DataLockStatusTuple.tupleType():
            return (
                yield self._lockManager.makeLockVortexMsg(filt, tupleSelector)
            )

        # If we have the lock, then return the live data.
        if self._lockManager.isLocked(tupleSelector):
            return (
                yield self._lockManager.makeDataVortexMsg(filt, tupleSelector)
            )

        # noinspection PyArgumentList
        return (yield self._makeVortexMsgFromDelegate(filt, tupleSelector))

    @inlineCallbacks
    def _makeVortexMsgFromDelegate(
        self, filt: dict, tupleSelector: TupleSelector
    ) -> Union[Deferred, bytes]:
        tupleType = tupleSelector.name

        if tupleType not in self._registeredDataDelegateByDataType:
            raise ValueError(
                f"Delegate for {tupleType} not registered with "
                f"{self.__class__}"
            )

        delegate = self._registeredDataDelegateByDataType[tupleType]
        result = yield delegate.loadData(tupleSelector)

        results = [result]

        payloadEnvelope = PayloadEnvelope(filt=filt)
        payloadEnvelope.encodedPayload = yield Payload(
            filt=filt, tuples=results
        ).toEncodedPayloadDefer()
        vortexMsg = yield payloadEnvelope.toVortexMsgDefer()

        return vortexMsg

    @inlineCallbacks
    def processTupleAction(
        self,
        tupleAction: TupleActionABC,
        tupleActionVortex: TupleActionVortex,
    ) -> Deferred:
        if isinstance(tupleAction, _DataLoaderTupleAction):
            return (
                yield self._processCrudTupleAction(
                    tupleAction, tupleActionVortex
                )
            )

        if isinstance(tupleAction, _LockDataTupleAction):
            return (
                yield self._lockManager.processLockTupleAction(
                    tupleAction, tupleActionVortex
                )
            )

        raise NotImplementedError(
            "Unsupported tuple action type: %s", tupleAction
        )

    @inlineCallbacks
    def _processCrudTupleAction(
        self,
        tupleAction: _DataLoaderTupleAction,
        _: TupleActionVortex,  # tupleActionVortex
    ):
        if tupleAction.action in (
            tupleAction.DELETE_ACTION,
            tupleAction.STORE_ACTION,
            tupleAction.LOAD_ACTION,
        ):
            if not tupleAction.tupleDataSelector:
                raise Exception(
                    f"CREATE and STORE requires tupleAction.tupleDataSelector"
                    f" {tupleAction}"
                )

        if tupleAction.action in (
            tupleAction.STORE_ACTION,
            tupleAction.CREATE_ACTION,
        ):
            if not tupleAction.dataTuple:
                raise Exception(
                    f"CREATE and STORE requires tupleAction.dataTuple"
                    f" {tupleAction.tupleDataSelector}"
                )

        tupleDataSelector: TupleSelector = tupleAction.tupleDataSelector

        if tupleAction.action == tupleAction.STORE_ACTION:
            if tupleDataSelector.name != tupleAction.dataTuple.tupleType():
                raise Exception(
                    f"STORE requires"
                    f" tupleAction.dataTuple={tupleAction.dataTuple}"
                    f" must match tupleDataSelector.name={tupleDataSelector.name}"
                )

        tupleType = None
        if tupleDataSelector:
            tupleType = tupleDataSelector.name

        elif tupleAction.dataTuple:
            tupleType = tupleAction.dataTuple.tupleType()

        # This should never happen with the checks above
        if not tupleType:
            raise Exception("tupleDataSelector and dataTuple are both None")

        if tupleType not in self._registeredDataDelegateByDataType:
            raise ValueError(
                f"Delegate for {tupleType} not registered with "
                f"{self.__class__}"
            )

        delegate = self._registeredDataDelegateByDataType[tupleType]

        if tupleDataSelector and self._lockManager.isLocked(tupleDataSelector):
            if not self._lockManager.hasLock(
                tupleDataSelector, tupleAction.userUuid
            ):
                raise Exception("User does not have lock for editing")

        # TODO: Add username checking based on
        #  ISession(tupleActionVortex.httpSession).userName
        # TODO: Add some kind of random token we give to user that gets
        #  lock.

        response = _DataLoaderTupleActionResponseTuple()
        if tupleAction.action == tupleAction.CREATE_ACTION:
            response.tupleDataSelector = yield delegate.createData(
                tupleAction.dataTuple
            )
            assert isinstance(response.tupleDataSelector, TupleSelector), (
                "TupleDataLoader: CREATE_ACTION did not"
                " return instance of TupleSelector"
            )
            tupleDataSelector = response.tupleDataSelector

        elif tupleAction.action == tupleAction.STORE_ACTION:
            maybeTupleSelector = yield delegate.storeData(
                tupleAction.dataTuple, tupleDataSelector
            )

            # Unlock from the old Selector
            if self._lockManager.isLocked(tupleDataSelector):
                self._lockManager.unlock(tupleDataSelector)

            if maybeTupleSelector:
                assert isinstance(maybeTupleSelector, TupleSelector), (
                    "TupleDataLoader: STORE_ACTION did not"
                    " return instance of Optional[TupleSelector]"
                )
                response.tupleData = maybeTupleSelector
                tupleDataSelector = maybeTupleSelector

            response.tupleData = yield delegate.loadData(tupleDataSelector)

        elif tupleAction.action == tupleAction.LOAD_ACTION:
            response.tupleData = yield delegate.loadData(tupleDataSelector)
            assert isinstance(response.tupleData, TupleDataLoaderTupleABC), (
                "TupleDataLoader: LOAD_ACTION did not"
                " return instance of TupleDataLoaderTupleABC"
            )
            if self._lockManager.isLocked(tupleDataSelector):
                self._lockManager.unlock(tupleDataSelector)

        elif tupleAction.action == tupleAction.DELETE_ACTION:
            yield delegate.deleteData(tupleDataSelector)
            if self._lockManager.isLocked(tupleDataSelector):
                self._lockManager.unlock(tupleDataSelector)

        self._observable.notifyOfTupleUpdate(tupleDataSelector)

        return response
