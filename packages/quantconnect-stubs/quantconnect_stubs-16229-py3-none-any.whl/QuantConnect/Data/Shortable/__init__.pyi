from typing import overload
import datetime
import typing

import QuantConnect
import QuantConnect.Data.Shortable
import QuantConnect.Interfaces
import System


class LocalDiskShortableProvider(System.Object, QuantConnect.Interfaces.IShortableProvider):
    """Sources short availability data from the local disk for the given brokerage"""

    DataProvider: QuantConnect.Interfaces.IDataProvider = ...
    """
    The data provider instance to use
    
    This field is protected.
    """

    @property
    def Brokerage(self) -> str:
        """
        The short availability provider
        
        This property is protected.
        """
        ...

    def __init__(self, brokerage: str) -> None:
        """
        Creates an instance of the class. Establishes the directory to read from.
        
        :param brokerage: Brokerage to read the short availability data
        """
        ...

    def ShortableQuantity(self, symbol: typing.Union[QuantConnect.Symbol, str], localTime: typing.Union[datetime.datetime, datetime.date]) -> typing.Optional[int]:
        """
        Gets the quantity shortable for the Symbol at the given date.
        
        :param symbol: Symbol to lookup shortable quantity
        :param localTime: Time of the algorithm
        :returns: Quantity shortable. Null if the data for the brokerage/date does not exist.
        """
        ...


class ShortableProviderPythonWrapper(System.Object, QuantConnect.Interfaces.IShortableProvider):
    """Python wrapper for custom shortable providers"""

    def __init__(self, shortableProvider: typing.Any) -> None:
        """
        Creates a new instance
        
        :param shortableProvider: The python custom shortable provider
        """
        ...

    def ShortableQuantity(self, symbol: typing.Union[QuantConnect.Symbol, str], localTime: typing.Union[datetime.datetime, datetime.date]) -> typing.Optional[int]:
        """
        Gets the quantity shortable for a Symbol, from python custom shortable provider
        
        :param symbol: Symbol to check shortable quantity
        :param localTime: Local time of the algorithm
        :returns: The quantity shortable for the given Symbol as a positive number. Null if the Symbol is shortable without restrictions.
        """
        ...


class NullShortableProvider(System.Object, QuantConnect.Interfaces.IShortableProvider):
    """
    Defines the default shortable provider in the case that no local data exists.
    This will allow for all assets to be infinitely shortable, with no restrictions.
    """

    Instance: QuantConnect.Data.Shortable.NullShortableProvider
    """The null shortable provider instance"""

    def ShortableQuantity(self, symbol: typing.Union[QuantConnect.Symbol, str], localTime: typing.Union[datetime.datetime, datetime.date]) -> typing.Optional[int]:
        """
        Gets the quantity shortable for the Symbol at the given time.
        
        :param symbol: Symbol to check
        :param localTime: Local time of the algorithm
        :returns: null, indicating that it is infinitely shortable.
        """
        ...


class InteractiveBrokersShortableProvider(QuantConnect.Data.Shortable.LocalDiskShortableProvider):
    """Sources the InteractiveBrokers short availability data from the local disk for the given brokerage"""

    def __init__(self) -> None:
        """Creates a new instance"""
        ...


