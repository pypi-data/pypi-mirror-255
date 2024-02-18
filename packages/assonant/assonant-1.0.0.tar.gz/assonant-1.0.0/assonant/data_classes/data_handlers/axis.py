"""Assonant Axis data handler."""
from typing import Union

from ..types import TransformationType
from .data_field import DataField
from .data_handler import DataHandler
from .time_series import TimeSeries


class Axis(DataHandler):
    """Data class to handle data related to an axis position.

    When axis position is static the 'value' field must contain a single value and when it varies over time, it
    should be an array or TimeSeries.
    """

    name: str
    transformation_type: TransformationType
    value: Union[DataField, TimeSeries]
