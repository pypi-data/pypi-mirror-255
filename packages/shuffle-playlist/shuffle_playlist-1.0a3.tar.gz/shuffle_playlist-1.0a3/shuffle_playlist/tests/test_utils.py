from pytest import fixture, mark
from pathlib import Path
from typing import NoReturn

from ..utils import *

class TestGetFileExtension:
    PARAMS = [('pretty.ogg', 'ogg'), ('good.wav', 'wav'),
              ('good', None), ('good.', None)]

    @mark.parametrize('fn,expected', PARAMS)
    def test_get_file_extension_string(self, fn: str, expected: str | None):
        ext = get_file_extension(fn)
        assert ext == expected

    @mark.parametrize('fn,expected', PARAMS)
    def test_get_file_extension_path(self, fn: str, expected: str | None):
        pfn = Path(fn).resolve()
        ext = get_file_extension(pfn)
        assert ext == expected

def sorted_score(l: list, cmp: list) -> int:
    """Returns a score for how sorted L is compared to CMP."""
    LEN = len(l)
    score = 0
    assert LEN == len(cmp), "lists must be the same length"
    for i in range(LEN):
        if l[i] == cmp[i]:
            score += 1

    return score

def test_shuffle_list():
    l = [1, 2, 3, 4, 5]
    sl = shuffle_list(l.copy())
    assert sorted_score(sl, l) < 5

    l = ['a', 'b', 'c', 'd', 'e']
    sl = shuffle_list(l.copy())
    assert sorted_score(sl, l) < 5

def _raise_commandline_error(user_data=None) -> NoReturn:
    raise CommandlineError("commandline error", user_data=user_data)

PARAMS = [
    1,
    ('a'),
    300.054,
    (5, 6),
    {'add': '+', 'minus': '-'},
    [5, 6]
]

@mark.parametrize('user_data', PARAMS)
def test_commandline_error(user_data):
    try:
        _raise_commandline_error(user_data)
    except CommandlineError as exc:
        assert exc.user_data == user_data
