"""Define utility methods for working with the git (gitpython) module.

    $> pip install gitpython
"""
from __future__ import annotations

from pathlib import Path

import git


def is_git_repo(path: Path) -> bool:
    """Is the given path a git repo? If yes, return True. If no, return False."""
    try:
        _ = git.Repo(path).git_dir  # noqa
        return True
    except git.exc.InvalidGitRepositoryError:  # noqa
        return False
