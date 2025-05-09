"""Python library for performing I/O (currently read-only) operations on MATLAB MAT-files."""

from .matio_base import load_from_mat

__all__ = ["load_from_mat"]
