"""
 * Created by Synerty Pty Ltd
 *
 * This software is open source, the MIT license applies.
 *
 * Website : https://www.synerty.com
 * Support : support@synerty.com
"""
import abc
from abc import abstractmethod
from typing import Union, Optional

from twisted.internet.defer import Deferred

from vortex.TupleSelector import TupleSelector
from vortex.data_loader.TupleDataLoaderTupleABC import TupleDataLoaderTupleABC


class TupleDataLoaderDelegateABC(abc.ABC):
    """Tuple Data Loader Delegate ABC

    ABC for delegate classes to handle the reading and writing for each forms'
    data. Handlers must be register in
    (`Tuple`, `TupleDataLoaderDelegateABC`) pairs with the `TupleDataLoader`

    """

    def start(self):
        pass

    def shutdown(self):
        pass

    @abstractmethod
    def createData(
        self, data: TupleDataLoaderTupleABC
    ) -> Union[Deferred, TupleSelector]:
        """Load Data

        The `createData` method is called when data does not exist and needs
        to be created.

        :param data: The new object to create
        :param selector: The current tuple selector for the data.
        :return: The `TupleSelector` or a `Deferred` which eventually
            results in a `TupleSelector`. The tuple selector must select the new
            data.
        """
        pass

    @abstractmethod
    def loadData(
        self, selector: TupleSelector
    ) -> Union[Deferred, TupleDataLoaderTupleABC]:
        """Load Data

        The `loadData` method is called when data needs to be loaded from a
        storage medium. The query is represented by a `TupleSelector` value
        `selector`.

        :param selector: The `TupleSelector` for which to load data
        :return: The `Tuple` or a `Deferred` which eventually results in a `Tuple`
        """
        pass

    @abstractmethod
    def storeData(
        self, data: TupleDataLoaderTupleABC, tupleSelector: TupleSelector
    ) -> Optional[TupleSelector]:
        """Store Data

        Store the data into the storage medium. The `data` is the `Tuple` which
        needs to be written

        :param data: Tuple to write and store
        :param selector: Previous selector used to get the data
        :return: TupleSelector: An optional new tuple selector if it has changed
        """
        pass

    @abstractmethod
    def deleteData(self, selector: TupleSelector) -> Deferred:
        """Delete Data

        Delete the data referenced by the `selector`

        :param selector: `TupleSelector` for data to be deleted
        :return: Deferred
        """
        pass
