"""
This module defines the parsing interface and the different parsers for BAGUETTE to handle different types of input reports.
"""

from importlib import import_module
from pathlib import Path
from .abc import AbstractParser
modules = {f"lib.{p.stem}" for p in (Path(__file__).parent / "lib").glob("*.py") if p.name != "__init__.py"}

parsers : list[type[AbstractParser]] = []

for m in modules:
    import_module(__package__ + "." + m)
    del m

__all__ = ["parsers"]

del modules, import_module, Path