"""
Some fonts for RenderCV.
"""

import pathlib

__version__ = "0.5.1"

package_folder_path = pathlib.Path(__file__).parent

# Make a list of all the folders (except __pycache__) in the package folder:
available_font_families = [
    folder.name
    for folder in package_folder_path.iterdir()
    if folder.is_dir() and folder.name != "__pycache__"
]
path_of = {
    font_famiy: package_folder_path / font_famiy
    for font_famiy in available_font_families
}
paths_to_font_folders = list(path_of.values())
paths_to_font_files = [
    font_file
    for font_folder in paths_to_font_folders
    for font_file in font_folder.rglob("*")
    if font_file.is_file() and font_file.suffix not in {"", ".txt"}
]
links_to_font_files = [
    f"https://raw.githubusercontent.com/rendercv/rendercv-fonts/main/rendercv_fonts/{font_path.relative_to(package_folder_path)}"
    for font_path in paths_to_font_files
]
