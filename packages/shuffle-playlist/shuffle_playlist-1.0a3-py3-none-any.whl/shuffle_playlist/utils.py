"""
Utility functions and classes.

Functions:
    * get_file_extension()
    * shuffle_playlist()
"""

from typing import Protocol, Optional, cast
from pathlib import Path
import random, re

class CommandlineError(RuntimeError):
    """
    An error for wrong commandline arguments.

    USER_DATA can be used to provide user data, which
    the user can.
    """

    def __init__(self, *args, user_data=None, **kw):
        self.user_data = user_data
        super().__init__(*args, **kw)

class StringInputError(RuntimeError):
    """An error for invalid string input."""

class FileDescriptor(Protocol):
    """Describes a file descriptor."""

    def write(self, data: str | bytes):
        """Write DATA to file."""

class Pathlike(Protocol):
    def __fspath__(self) -> str:
        ...

_ext_re = re.compile(r'\.(\w+)')

def get_file_extension(_file: Path | str) -> Optional[str]:
    """
    Get the extension of _FILE.

    Returns a string unless _FILE is a string and there is
    not extension, in which case it returns None.
    """
    if isinstance(_file, Path):
        pfile = cast(Path, _file)
        res = str(pfile.suffix)
        return res[1:] or None
    elif (_file, str):
        sfile = cast(str, _file)
        m = _ext_re.search(sfile)
        return m[1] if m else None

def _recurse_subdirs(subdir: Path):
    if subdir.is_dir():
        res: list[Path] = []
        for fp in subdir.iterdir():
            if fp.is_dir():
                temp = _recurse_subdirs(fp)
                assert isinstance(temp, list)
                res.extend(temp)
            else:
                res.append(fp)
        return res

    # Not a directory
    return subdir

def recurse_subdirs(*subdirs: str | Pathlike) -> list[Path]:
    """
    Recurse through *SUBDIRS.

    Return a list of files from recursing through each
    directory in *SUBDIRS, and each subdirectory of
    that directory. If an element of *SUBDIRS is a
    file, then it is added to the resulting list
    unchanged.
    """
    files = []
    for subdir in subdirs:
        temp = _recurse_subdirs(Path(subdir).resolve())
        if isinstance(temp, list):
            files.extend(temp)
        else:
            files.append(temp)

    files.sort()
    return files

def shuffle_list(values: list) -> list:
    """Shuffles the items in a list."""
    random.shuffle(values)
    return values

__all__ = [
    # Classes
    'CommandlineError',
    'FileDescriptor',
    'StringInputError',

    # Functions
    'get_file_extension',
    'recurse_subdirs',
    'shuffle_list'
]
