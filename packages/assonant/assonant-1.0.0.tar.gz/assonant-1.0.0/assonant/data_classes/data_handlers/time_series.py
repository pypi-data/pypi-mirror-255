"""Assonant TimeSeries class."""
from .data_field import DataField
from .data_handler import DataHandler


class TimeSeries(DataHandler):
    """Data class to handle any type of time series data."""

    value: DataField
    timestamps: DataField
