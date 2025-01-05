"""
RenderCV is a Typst-based Python package with a command-line interface (CLI) that allows
you to version-control your CV/resume as source code.
"""

__version__ = "2.0"

from .api import generate_a_typst_file

__all__ = ["generate_a_typst_file"]
