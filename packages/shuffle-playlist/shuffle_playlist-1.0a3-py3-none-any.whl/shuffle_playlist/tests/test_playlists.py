from ..playlists import get_playlist, get_playlist_entry
from pytest import mark
from typing import no_type_check, cast
from pathlib import Path
import os, dotenv

env = dotenv.find_dotenv()
if env:
    dotenv.load_dotenv(env)
del env

@mark.parametrize('_format', ['m3u'])
def test_get_playlist(_format: str):
    cls = get_playlist(_format)

@mark.parametrize('filename', ['file.ogg'])
def test_get_playlist_entries(filename: str):
    get_playlist_entry(filename)
