"""Define utility methods that make use of the os module.
"""
from __future__ import annotations

import ast
import logging
import os
import shutil
from pathlib import Path

from decorators.timing import timing

logger = logging.getLogger(__name__)

IN_PATH_IGNORE = ["venv", ".git", ".idea", "pycache", "log", ".txt", "DS_Store", ".md"]


class FStringFinder(ast.NodeVisitor):
    def __init__(self, filepath: Path):
        self.filepath = filepath
        self.flagged = []

    def visit_JoinedStr(self, node: ast.JoinedStr) -> None:
        """Check if the f-string has any FormattedValue (actual formatting). If yes, return a
        notification string. If not, do nothing.
        """
        if not any(isinstance(value, ast.FormattedValue) for value in node.values):
            self.flagged.append(
                f"{self.filepath}:{node.lineno}. Line: {node.values[0].value}"  # noqa
            )


@timing
def backup_python_files(root_dir: Path):
    """Creates a backup (with .py.bak) extension for all python files in the given root_dir and
    all subdirectories. Non-python files are ignored."""
    p_count = 0
    f_count = 0

    for path, _, filenames in os.walk(root_dir):
        if any([i in path for i in IN_PATH_IGNORE]):
            continue
        p_count += 1

        for filename in filenames:
            if filename.endswith(".py"):
                filepath = Path(os.path.join(path, filename))
                backup_path = Path(os.path.join(path, filename + ".bak"))
                shutil.copy(filepath, backup_path)

                f_count += 1
                logger.info(f"{filepath.name}... {backup_path.name}.")

    logger.info(f"Directories scanned: {p_count}.")
    logger.info(f"Python files backed up: {f_count}.")


@timing
def find_fstrings_without_formatting(filepath: Path):
    """Locates all fstrings that lack any formatting (dynamic content)."""
    flagged = []

    for path, _, filenames in os.walk(filepath):
        if "__pycache__" in path:
            continue

        print(f"Searching {path} for f-strings without formatting.")

        if any([i in str(path) for i in IN_PATH_IGNORE]):
            continue

        for filename in filenames:
            if ".bak" in filename:
                continue

            print(f"\tFilename: {filename}.")
            filename = str(filename)
            if any([i in filename for i in IN_PATH_IGNORE]):
                continue
            if filename.endswith(".py"):
                filepath = Path(os.path.join(path, filename))
                with open(filepath, "r", encoding="utf-8") as f:
                    source = f.read()
                    tree = ast.parse(source, filename=str(filepath))
                    finder = FStringFinder(filepath)
                    finder.visit(tree)
                    flagged += finder.flagged

    if flagged:
        f_strings = "f_strings"
        if len(flagged) == 1:
            f_strings = f_strings[:-1]

        result_msg = (
            f"Identified {len(flagged)} {f_strings} without formatting. Listing follows "
            f"in this message.\n"
        )
        for i, flag in enumerate(flagged, 1):
            result_msg += f"\n\t\t\t{i}: {flag}"

        logger.info(result_msg)
    else:
        result_msg = "Did not find any f-strings without formatting.\n"

    print(result_msg)
