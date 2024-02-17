#!/usr/bin/env python3

from argparse import ArgumentParser
from pathlib import Path
from typing import Any, Optional, Sequence
from dataclasses import dataclass
from .utils import *
from .playlists import get_playlist as pl_get_playlist

__all__ = ['Parameters', 'parse_commandline', 'main']

@dataclass
class Parameters:
    files: list[Path]
    output: Path | str
    format_: str
    title: Optional[str]

def parse_commandline(_argv: Optional[Sequence[str]]=None):
    parser = ArgumentParser(prog='shuffle_playlist', description="A tool for creating shuffled playlists")
    parser.add_argument('-t', '--title', help='set the title of the playlist')
    parser.add_argument('-f', '--format', help='playlist format')
    parser.add_argument('OUTPUT', help='file to write playlist to (or - for stdout)')
    parser.add_argument('FILE', nargs='+', type=Path,
                        help='files to add to playlist')

    if _argv:
        args = parser.parse_args(_argv)
    else:
        args = parser.parse_args()

    files: list[Path] = args.FILE
    output: Path | str = args.OUTPUT

    # If output is '-', then --format is required
    ext: Any = None
    if output == '-':
        ext = args.format
        if ext is None:
            raise CommandlineError("missing '--format' option: required when OUTPUT is '-'",
                                   user_data=parser)
    else:
        output = Path(output).resolve()
        ext = args.format or get_file_extension(output)

    args.extension = ext

    return Parameters(
        files=recurse_subdirs(*files),
        output=output,
        format_=ext,
        title=args.title
    )

def main():
    # Main function.
    params = parse_commandline()

    fmt = params.format_
    files = params.files
    output = params.output

    PlaylistClass = pl_get_playlist(fmt)
    playlist = PlaylistClass(shuffle_list(files), title=params.title)

    if output == '-':
        print(playlist.get_string())
        return

    # Write to file
    with open(output, 'wt') as fd:
        fd.write(playlist.get_string())

if __name__ == "__main__":
    main()
