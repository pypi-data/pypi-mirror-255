"""Assonant Data Classes.

Assonant data classes defines standard data schemas for acquiring sending,
manipulating and storing data over Assonant modules.

All classes inherits from AssonantDataClass and can be split in 3 types:

1. Instrument: Data classes responsible for grouping data related to instrumental data
2. Non-Instrument: Data classes responsible for grouping data related to non-instrumental data
3. Data Handler: Data classes responsible for standardizing how data is handled inside other
Assonant data classes.

To import and uses data classes from each type, refer to its specific submodule as shown below:

from .assonant_data_class.<sub_module_name> import <data_class_name>, ...
"""

from .assonant_data_class import AssonantDataClass

__all__ = ["AssonantDataClass"]
