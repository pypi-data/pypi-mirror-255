import logging

from twisted.internet import defer
from twisted.internet.defer import Deferred

from vortex.PerformTestActionTuple import PerformTestActionTuple
from vortex.TupleAction import TupleActionABC, TupleGenericAction
from vortex.handler.TupleActionProcessor import (
    TupleActionProcessor,
    TupleActionProcessorDelegateABC,
)

logger = logging.getLogger(__name__)


class TestProcessor(TupleActionProcessorDelegateABC):
    def processTupleAction(self, tupleAction: TupleActionABC) -> Deferred:
        assert isinstance(
            tupleAction, TupleGenericAction
        ), "tupleAction is not TupleGenericAction"
        if "FAIL PLEASE" == tupleAction.data:
            raise Exception("Processing failed scenario, exception raised")
        return defer.succeed(True)


actionProcessor = TupleActionProcessor("vortexTestActions")
actionProcessor.setDelegate(PerformTestActionTuple.tupleName(), TestProcessor())
