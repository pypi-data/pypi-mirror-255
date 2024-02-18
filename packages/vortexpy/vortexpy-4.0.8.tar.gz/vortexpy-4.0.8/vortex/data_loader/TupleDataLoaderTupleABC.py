import logging
from abc import ABCMeta

from vortex.Tuple import Tuple

logger = logging.getLogger(__name__)


class TupleDataLoaderTupleABC(Tuple, metaclass=ABCMeta):
    pass
