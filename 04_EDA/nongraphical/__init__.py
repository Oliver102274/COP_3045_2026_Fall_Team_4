"""Reusable non-graphical EDA; importing the package reads and writes no files.

The table functions reuse data_preparation's column validation, so the project
root must be importable. The launcher and the tests add it to sys.path.
"""

from .analyzer import NonGraphicalAnalyzer
from .tables import build_tables, prepare_data

__all__ = ["NonGraphicalAnalyzer", "build_tables", "prepare_data"]
