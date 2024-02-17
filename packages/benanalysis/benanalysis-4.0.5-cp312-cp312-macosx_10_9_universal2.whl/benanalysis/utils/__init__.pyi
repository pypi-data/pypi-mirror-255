from __future__ import annotations
import benanalysis._benpy_core.utils
import typing
import benanalysis._benpy_core

__all__ = [
    "find_key",
    "find_peak",
    "find_peaks",
    "log",
    "log10",
    "peak_width",
    "transform"
]


def find_key(scan: benanalysis._benpy_core.Scan, lo: float, hi: float, value: float) -> float:
    """
    Find the key between lo and hi that gives a value of the specified value.
    """
def find_peak(scan: benanalysis._benpy_core.Scan) -> float:
    """
    Finds the global peak of a specified Scan scan and returns the found
    (interpolated) key.
    """
def find_peaks(scan: benanalysis._benpy_core.Scan) -> benanalysis._benpy_core.Scan:
    """
    Finds all the peaks in a specified Scan scan and returns a new Scan containing
    the found points.
    """
@typing.overload
def log(scan: benanalysis._benpy_core.Scan) -> benanalysis._benpy_core.Scan:
    """
    Compute natural logarithm of scan [Scan].

    Compute logarithm base [Scan] of scan [Scan].

    Compute logarithm base [float] of scan [Scan].

    Compute logarithm base [Scan] of x [float].
    """
@typing.overload
def log(scan: benanalysis._benpy_core.Scan, base: benanalysis._benpy_core.Scan) -> benanalysis._benpy_core.Scan:
    pass
@typing.overload
def log(scan: benanalysis._benpy_core.Scan, base: float) -> benanalysis._benpy_core.Scan:
    pass
@typing.overload
def log(x: float, base: benanalysis._benpy_core.Scan) -> benanalysis._benpy_core.Scan:
    pass
def log10(scan: benanalysis._benpy_core.Scan) -> benanalysis._benpy_core.Scan:
    """
    Compute logarithm base 10 of scan [Scan].
    """
def peak_width(scan: benanalysis._benpy_core.Scan, height: float) -> float:
    """
    Finds the width of a peak at a specified fractional height from the maximum.
    Assumes the scan contains a single peak.
    """
def transform(scan: benanalysis._benpy_core.Scan, binary_operation: typing.Callable[[float, float], float]) -> benanalysis._benpy_core.Scan:
    """
    Returns a new Scan with entries {key, op(key, value)} for each {key, value}
    in the specified Scan.
    """
