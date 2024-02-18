import logging
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Optional

import pytz
from twisted.internet.task import LoopingCall

from vortex.DeferUtil import deferToThreadWrapWithLogger
from vortex.Payload import Payload
from vortex.PayloadEnvelope import PayloadEnvelope
from vortex.TupleActionVortex import TupleActionVortex
from vortex.TupleSelector import TupleSelector
from vortex.data_loader.TupleDataLoaderTupleABC import TupleDataLoaderTupleABC
from vortex.data_loader.TupleDataLoaderTuples import (
    _LockDataTupleAction,
    _DataLockStatusTuple,
)
from vortex.handler.TupleDataObservableHandler import TupleDataObservableHandler

logger = logging.getLogger(__name__)


class _DataLockStatusTupleSelector:
    """Data lock status Tuple Selector

    This class provides some consistency on how the data lock status
    tuple selector is structured.
    """

    DATA_TUPLE_SELECTOR_KEY = "dataTupleSelector"

    @classmethod
    def getDataTupleSelector(
        cls, tupleSelector: TupleSelector
    ) -> TupleSelector:
        assert tupleSelector.name == _DataLockStatusTuple.tupleType(), (
            "_DataLockStatusTupleSelector"
            " tupleSelector.name is not _DataLockStatusTuple.tupleType()"
        )
        return tupleSelector.selector[cls.DATA_TUPLE_SELECTOR_KEY]

    @classmethod
    def makeLockTupleSelector(
        cls, dataTupleSelector: TupleSelector
    ) -> TupleSelector:
        return TupleSelector(
            name=_DataLockStatusTuple.tupleType(),
            selector={
                _DataLockStatusTupleSelector.DATA_TUPLE_SELECTOR_KEY: dataTupleSelector
            },
        )


class _LockState:
    LOCK_EXPIRE = timedelta(hours=2)

    def __init__(
        self,
        tupleDataSelector: TupleSelector,
        lockedByUserUuid: str,
        lockedByVortexUuid: str,
        lockedByDelegateUuid: str,
        liveUpdateDataTuple: TupleDataLoaderTupleABC,
    ):
        self.tupleDataSelector = tupleDataSelector
        self.lockedByUserUuid = lockedByUserUuid
        self.lockedByVortexUuid = lockedByVortexUuid
        self.lockedByDelegateUuid = lockedByDelegateUuid
        self.liveUpdateDataTuple: TupleDataLoaderTupleABC = liveUpdateDataTuple

        self.lockStart = datetime.now(pytz.UTC)
        self.lockTouched = datetime.now(pytz.UTC)

    def touch(self, liveUpdateData: TupleDataLoaderTupleABC):
        self.lockTouched = datetime.now(pytz.UTC)
        self.liveUpdateDataTuple = liveUpdateData

    @property
    def expired(self) -> bool:
        return (self.lockTouched + self.LOCK_EXPIRE) < datetime.now(pytz.UTC)

    @property
    def autoExpireDate(self) -> datetime:
        return self.lockTouched + self.LOCK_EXPIRE


class TupleDataLiveLockManager:
    LOCK_CHECK_SECONDS = 5

    def __init__(self):
        self._lockStateByDataSelectorByDataTupleType: dict[
            str, [str, _LockState]
        ] = defaultdict(dict)
        self._lockExpiredLoopingCall = LoopingCall(self._checkLockExpired)
        self._observer: Optional[TupleDataObservableHandler] = None

    def start(self, observer: TupleDataObservableHandler):
        self._observer = observer
        self._lockExpiredLoopingCall.start(self.LOCK_CHECK_SECONDS)

    def shutdown(self):
        self._observer = None
        self._lockExpiredLoopingCall.stop()
        self._lockExpiredLoopingCall = None

    def _checkLockExpired(self):
        for (
            dataTupleType,
            lockStateByDataSelector,
        ) in list(self._lockStateByDataSelectorByDataTupleType.items()):
            for (
                tupleSelectorStr,
                lockState,
            ) in list(lockStateByDataSelector.items()):
                if lockState.expired:
                    logger.info(
                        "Unlocking. Lock expired for %s", tupleSelectorStr
                    )
                    self.unlock(lockState.tupleDataSelector)

    def _lock(
        self,
        tupleAction: _LockDataTupleAction,
        tupleActionVortex: TupleActionVortex,
    ) -> None:
        tupleDataSelector: TupleSelector = tupleAction.tupleDataSelector
        tupleSelectorStr = tupleDataSelector.toJsonStr()
        tupleDataType = tupleDataSelector.name

        lockStateByDataSelector = self._lockStateByDataSelectorByDataTupleType[
            tupleDataType
        ]
        lockState = lockStateByDataSelector.get(
            tupleSelectorStr,
            _LockState(
                tupleDataSelector=tupleDataSelector,
                lockedByUserUuid=tupleAction.userUuid,
                lockedByVortexUuid=tupleActionVortex.uuid,
                lockedByDelegateUuid=tupleAction.delegateUuid,
                liveUpdateDataTuple=tupleAction.liveUpdateDataTuple,
            ),
        )

        assert lockState.lockedByUserUuid == tupleAction.userUuid, (
            "TupleDataLiveLockManager: We received a lock action from a user"
            " that does not have the lock."
        )

        assert tupleAction.liveUpdateDataTuple, (
            "TupleDataLiveLockManager: We received an empty"
            " tupleAction.liveUpdateDataTuple"
        )

        lockState.touch(tupleAction.liveUpdateDataTuple)
        lockStateByDataSelector[tupleSelectorStr] = lockState

        self._observer.notifyOfTupleUpdate(
            _DataLockStatusTupleSelector.makeLockTupleSelector(
                lockState.tupleDataSelector
            )
        )

    def hasLock(self, tupleDataSelector: TupleSelector, userUuid: str) -> bool:
        tupleSelectorStr = tupleDataSelector.toJsonStr()
        tupleDataType = tupleDataSelector.name

        lock = self._lockStateByDataSelectorByDataTupleType[tupleDataType].get(
            tupleSelectorStr
        )

        return lock and lock.lockedByUserUuid == userUuid

    def isLocked(self, tupleDataSelector: TupleSelector) -> bool:
        tupleSelectorStr = tupleDataSelector.toJsonStr()
        tupleDataType = tupleDataSelector.name

        return bool(
            self._lockStateByDataSelectorByDataTupleType[tupleDataType].get(
                tupleSelectorStr
            )
        )

    def unlock(self, tupleDataSelector: TupleSelector) -> None:
        tupleSelectorStr = tupleDataSelector.toJsonStr()
        tupleDataType = tupleDataSelector.name

        lockState = self._lockStateByDataSelectorByDataTupleType[
            tupleDataType
        ].pop(tupleSelectorStr)

        self._observer.notifyOfTupleUpdate(
            _DataLockStatusTupleSelector.makeLockTupleSelector(
                lockState.tupleDataSelector
            )
        )

    @deferToThreadWrapWithLogger(logger)
    def makeLockVortexMsg(
        self, filt: dict, lockTupleSelector: TupleSelector
    ) -> bytes:
        dataTupleSelector = _DataLockStatusTupleSelector.getDataTupleSelector(
            lockTupleSelector
        )
        dataTupleType = dataTupleSelector.name
        lockStateByDataSelector = self._lockStateByDataSelectorByDataTupleType[
            dataTupleType
        ]
        lockState = lockStateByDataSelector.get(dataTupleSelector.toJsonStr())

        if lockState is None:
            results = [_DataLockStatusTuple(locked=False)]

        else:
            results = [
                _DataLockStatusTuple(
                    locked=True,
                    lockedByUserUuid=lockState.lockedByUserUuid,
                    lockAutoExpireDate=lockState.autoExpireDate,
                    liveUpdateDataTuple=lockState.liveUpdateDataTuple,
                )
            ]

        payloadEnvelope = PayloadEnvelope(filt=filt)
        payloadEnvelope.encodedPayload = Payload(
            filt=filt, tuples=results
        ).toEncodedPayload()
        return payloadEnvelope.toVortexMsg()

    @deferToThreadWrapWithLogger(logger)
    def makeDataVortexMsg(
        self, filt: dict, dataTupleSelector: TupleSelector
    ) -> bytes:
        dataTupleType = dataTupleSelector.name
        lockStateByDataSelector = self._lockStateByDataSelectorByDataTupleType[
            dataTupleType
        ]
        lockState = lockStateByDataSelector.get(dataTupleSelector.toJsonStr())

        results = lockState.liveUpdateDataTuple

        payloadEnvelope = PayloadEnvelope(filt=filt)
        payloadEnvelope.encodedPayload = Payload(
            filt=filt, tuples=results
        ).toEncodedPayload()
        return payloadEnvelope.toVortexMsg()

    @deferToThreadWrapWithLogger(logger)
    def processLockTupleAction(
        self,
        tupleAction: _LockDataTupleAction,
        tupleActionVortex: TupleActionVortex,
    ):
        if tupleAction.lock:
            self._lock(tupleAction, tupleActionVortex)
        else:
            self.unlock(tupleAction.tupleDataSelector)

        return
