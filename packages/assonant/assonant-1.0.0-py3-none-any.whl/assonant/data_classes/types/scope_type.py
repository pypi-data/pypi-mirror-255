"""Scope type definitions."""
from enum import Enum


class ScopeType(Enum):
    """Scope types."""

    CALIBRATION = "calibration"
    PRE_EXPOSURE = "pre_exposure"
    DURING_EXPOSURE = "during_exposure"
    POST_EXPOSURE = "post_exposure"
