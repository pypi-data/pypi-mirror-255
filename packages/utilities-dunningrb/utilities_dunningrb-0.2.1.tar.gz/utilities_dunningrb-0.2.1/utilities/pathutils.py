"""Define utility methods for working with Path objects.
"""
from __future__ import annotations

import logging
import os
import shutil
import sys
from pathlib import Path

from utilities.genutils import convert_to_type

logger = logging.getLogger(__name__)


def add_extension(filepath: Path, ext: str) -> Path:
    """Add an extension to the Path object if it does not already have one."""
    if not filepath.suffix:
        return Path(str(filepath) + ext)
    else:
        return filepath


def copy_all_files(*, sourcepath: Path, targetpath: Path):
    """Copy all files in the source directory to the target directory."""

    def _get_pairs(target_path):
        pairs = [
            (item, target_path / item.name)
            for item in sourcepath.glob("*")
            if item.is_file()
        ]

        pyversion = int(sys.version_info[0]) + int(sys.version_info[1]) / 10

        if pyversion <= 3.7:
            pairs = [(str(p[0]), str(p[1])) for p in pairs]
        elif pyversion < 3.0:
            err_msg = "Python version must be 3+."
            raise ValueError(err_msg)

        return pairs

    for pair in _get_pairs(targetpath):
        shutil.copy(*pair)


def count_files(path: Path):
    """Return the integer number of files in the given directory and all subdirectories."""
    return sum(1 for _, _, files in os.walk(path) for _ in files)


def confirm_filetype(filepath: str | Path, expected_extensions: str | list) -> bool:
    """Return boolean True if the given filepath has an extension that matches any of the given
    expected extensions."""
    filepath = convert_to_type(filepath, Path)
    expected_extensions = convert_to_type(expected_extensions, list)
    print(f"filepath: {filepath}")
    print(f"expected extensions: {expected_extensions}")
    suffix = filepath.suffix
    return any(suffix.lower() == expect.lower() for expect in expected_extensions)


def convert_to_path(path: str | Path) -> Path:
    """Convert the given path to type Path (in place) if it is type str. Otherwise, do nothing."""
    return Path(path) if path is isinstance(path, str) else path


def set_full_filepath(
    *,
    target_path: str | None,
    root_path: str,
    default_path: str,
    filename: str,
    parents: bool = True,
    exist_ok: bool = True,
):
    """Set the full filepath for the given filename. If path is None, use
    default_path.
    """
    if target_path is None:
        filepath = Path(root_path, default_path, filename)
    else:
        Path(root_path, target_path).mkdir(parents=parents, exist_ok=exist_ok)
        filepath = Path(root_path, target_path, filename)

    return filepath


def add_suffix_to_path(*, path: Path, suffix: str) -> Path:
    """Add a suffix to a Path object.

    Example:

        Given pathutils: "../../output/data.csv", as a Path object.
        Given suffix: "-01", as a stringutils.

        Return: "../../output/data-01.csv", as a Path object.
    """
    parent = str(path.parent)
    pathname, extension = str(path.name).split(".")
    pathname = "\\" + f"{pathname}-{suffix}.{extension}"

    return Path(parent + pathname)
