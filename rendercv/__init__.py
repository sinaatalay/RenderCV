"""
RenderCV is a Typst-based Python package with a command-line interface (CLI) that allows
you to version-control your CV/resume as source code.
"""

__version__ = "2.1"

from .api import create_contents_of_a_typst_file

__all__ = ["create_contents_of_a_typst_file"]

_parial_install_error_message = (
    "It seems you have a partial installation of RenderCV, so this feature is"
    " unavailable. To enable full functionality, run:\n\npip install"
    ' "rendercv[full]"`'
)
