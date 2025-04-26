"""Conversion utilities for matio"""

from .matmap import mat_to_containermap, mat_to_dictionary
from .matstring import mat_to_string
from .mattables import mat_to_categorical, mat_to_table, mat_to_timetable
from .mattimes import mat_to_calendarduration, mat_to_datetime, mat_to_duration

__all__ = [
    "mat_to_containermap",
    "mat_to_dictionary",
    "mat_to_string",
    "mat_to_categorical",
    "mat_to_table",
    "mat_to_timetable",
    "mat_to_calendarduration",
    "mat_to_datetime",
    "mat_to_duration",
]
