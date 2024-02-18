from typing import Optional

from vortex.Tuple import addTupleType, TupleField, Tuple
from vortex.TupleAction import TupleActionABC
from vortex.TupleSelector import TupleSelector
from vortex.data_loader.TupleDataLoaderTupleABC import TupleDataLoaderTupleABC


@addTupleType
class _DataLoaderTupleAction(TupleActionABC):
    __tupleType__ = "vortex._DataLoaderTupleAction"

    CREATE_ACTION = "create"
    STORE_ACTION = "store"
    LOAD_ACTION = "load"
    DELETE_ACTION = "delete"

    userUuid: str = TupleField()
    delegateUuid: str = TupleField()
    dataTuple: TupleDataLoaderTupleABC = TupleField()
    action: str = TupleField()
    tupleDataSelector: TupleSelector = TupleField()


@addTupleType
class _DataLoaderTupleActionResponseTuple(Tuple):
    __tupleType__ = "vortex._DataLoaderTupleActionResponseTuple"

    tupleData: Optional[TupleDataLoaderTupleABC] = TupleField()
    tupleDataSelector: Optional[TupleSelector] = TupleField()


@addTupleType
class _LockDataTupleAction(TupleActionABC):
    __tupleType__ = "vortex._LockDataTupleAction"

    lock: bool = TupleField()
    userUuid: str = TupleField()
    delegateUuid: str = TupleField()
    tupleDataSelector: TupleSelector = TupleField()
    liveUpdateDataTuple: TupleDataLoaderTupleABC = TupleField()


@addTupleType
class _DataLockStatusTuple(Tuple):
    __tupleType__ = "vortex._DataLockStatusTuple"

    locked: bool = TupleField(False)
    lockedByUserUuid: Optional[str] = TupleField()
    lockAutoExpireDate: Optional[str] = TupleField()
    liveUpdateDataTuple: Optional[TupleDataLoaderTupleABC] = TupleField()
