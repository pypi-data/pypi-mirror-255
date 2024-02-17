from __future__ import annotations
import benanalysis._benpy_core.physics
import typing

__all__ = [
    "planks_law_sr"
]


def planks_law_sr(temperature_kelvin: float, wavelength_meters: float) -> float:
    """
    Spectral radiance as a function of temperature and wavelength, in units of
    W/(sr m^2)/m
    """
