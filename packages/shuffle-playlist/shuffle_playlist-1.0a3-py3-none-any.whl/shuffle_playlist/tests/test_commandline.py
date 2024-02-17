from ..__main__ import *
from ..utils import CommandlineError
from typing import Iterable
from pathlib import Path

import pytest

def test_parse_commandline():
    def join(*args: str) -> str:
        return " ".join(args)

    def stringify(container: Iterable) -> list[str]:
        return [str(x) for x in container]

    def format_cmdline(*args) -> str:
        return "failed commandline:" + join(*args)

    files = ['file1.ogg', 'file2.wav']

    # assert that exceptions are correctly raised
    cmd = ['-', *files]
    with pytest.raises(CommandlineError):
        parse_commandline(*cmd)

    # explicit format, print to output
    cmd = ['-f', 'm3u', '-', *files]
    params = parse_commandline(*cmd)
    assert params.output == '-'
    assert len(params.files) >= 1

    # print to file, format inferred from filename
    cmd = ['playlist.m3u', *files]
    params = parse_commandline(*cmd)
     # output: assert is path
    assert isinstance(params.output, Path), format_cmdline(*cmd)
     # output: assert basename == 'playlist.m3u'
    assert str(params.output.name) == 'playlist.m3u', format_cmdline(*cmd)
     # format: assert == m3u; ensures that extension is correctly parsed
    assert params.format_ == 'm3u', format_cmdline(*cmd)
     # files: assert has same contents as original list
    assert join(*stringify(params.files)) == join(*files), format_cmdline(*cmd)

    for fmt in ('m3u', 'mpl'):
        cmd = ['-f', fmt, 'playlist.m3u', *files]
        params = parse_commandline(*cmd)
        # format: assert == fmt
        assert params.format_ == fmt, format_cmdline(*cmd)
