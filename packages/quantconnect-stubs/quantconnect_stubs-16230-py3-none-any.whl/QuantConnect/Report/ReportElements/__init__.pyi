from typing import overload
import abc
import typing

import QuantConnect
import QuantConnect.Packets
import QuantConnect.Report.ReportElements
import System
import System.Collections.Generic


class ReportElement(System.Object, QuantConnect.Report.ReportElements.IReportElement, metaclass=abc.ABCMeta):
    """Common interface for template elements of the report"""

    @property
    def Name(self) -> str:
        """Name of this report element"""
        ...

    @property
    def Key(self) -> str:
        """Template key code."""
        ...

    @property
    def JsonKey(self) -> str:
        """Normalizes the key into a JSON-friendly key"""
        ...

    @property
    def Result(self) -> System.Object:
        """Result of the render as an object for serialization to JSON"""
        ...

    def Render(self) -> str:
        """The generated output string to be injected"""
        ...


class EstimatedCapacityReportElement(QuantConnect.Report.ReportElements.ReportElement):
    """Capacity Estimation Report Element"""

    def __init__(self, name: str, key: str, backtest: QuantConnect.Packets.BacktestResult, live: QuantConnect.Packets.LiveResult) -> None:
        """
        Create a new capacity estimate
        
        :param name: Name of the widget
        :param key: Location of injection
        :param backtest: Backtest result object
        :param live: Live result object
        """
        ...

    def Render(self) -> str:
        """Render element"""
        ...


class SharpeRatioReportElement(QuantConnect.Report.ReportElements.ReportElement):
    """This class has no documentation."""

    @property
    def LiveResult(self) -> QuantConnect.Packets.LiveResult:
        """
        Live result object
        
        This property is protected.
        """
        ...

    @property
    def BacktestResult(self) -> QuantConnect.Packets.BacktestResult:
        """
        Backtest result object
        
        This property is protected.
        """
        ...

    @property
    def BacktestResultValue(self) -> typing.Optional[float]:
        """Sharpe Ratio from a backtest"""
        ...

    def __init__(self, name: str, key: str, backtest: QuantConnect.Packets.BacktestResult, live: QuantConnect.Packets.LiveResult, tradingDaysPerYear: int) -> None:
        """
        Estimate the sharpe ratio of the strategy.
        
        :param name: Name of the widget
        :param key: Location of injection
        :param backtest: Backtest result object
        :param live: Live result object
        :param tradingDaysPerYear: The number of trading days per year to get better result of statistics
        """
        ...

    def GetAnnualStandardDeviation(self, trailingPerformance: System.Collections.Generic.List[float], tradingDaysPerYear: float) -> float:
        """
        Get annual standard deviation
        
        :param trailingPerformance: The performance for the last period
        :param tradingDaysPerYear: The number of trading days per year to get better result of statistics
        :returns: Annual standard deviation.
        """
        ...

    def Render(self) -> str:
        """The generated output string to be injected"""
        ...


class ParametersReportElement(QuantConnect.Report.ReportElements.ReportElement):
    """This class has no documentation."""

    def __init__(self, name: str, key: str, backtestConfiguration: QuantConnect.AlgorithmConfiguration, liveConfiguration: QuantConnect.AlgorithmConfiguration, template: str) -> None:
        """
        Creates a two column table for the Algorithm's Parameters
        
        :param name: Name of the widget
        :param key: Location of injection
        :param backtestConfiguration: The configuration of the backtest algorithm
        :param liveConfiguration: The configuration of the live algorithm
        :param template: HTML template to use
        """
        ...

    def Render(self) -> str:
        """
        Generates a HTML two column table for the Algorithm's Parameters
        
        :returns: Returns a string representing a HTML two column table.
        """
        ...


