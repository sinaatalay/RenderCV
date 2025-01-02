"""
The `rendercv.themes` package contains all the built-in templates and the design data
models for the themes.
"""

from .classic import ClassicThemeOptions
from .sb2nov import Sb2novThemeOptions

__all__ = [
    "ClassicThemeOptions",
    "Sb2novThemeOptions",
]
