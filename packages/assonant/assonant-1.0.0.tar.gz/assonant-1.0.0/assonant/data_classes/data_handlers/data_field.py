"""Assonant DataField class."""
from typing import Dict, List, Optional, Type, Union

import numpy as np

from .data_handler import DataHandler


class DataField(DataHandler):
    """Data class to handle any type of base data, such as integers, floats, numpy arrays and lists."""

    value: Union[int, float, str, List, Type[np.ndarray]]
    unit: Optional[str] = None
    extra_metadata: Optional[Dict[str, Union[int, float, str, List, Type[np.ndarray]]]] = {}
