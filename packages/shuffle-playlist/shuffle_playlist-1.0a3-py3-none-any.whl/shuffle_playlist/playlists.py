"""
Playlists and playlist entries.

Do not instance any of the classes directly; instead,
use get_playlist() and get_playlist_entry().
"""

from typing import cast, Type
from abc import ABC, abstractmethod
from pathlib import Path
from .audio import get_tags
from .utils import get_file_extension
import re

## Playlist entries

class PlaylistEntry(ABC):
    """Abstract class representing an entry in a playlist."""

    __slots__ = ('channels', 'filename', 'length', 'metadata', 'samplerate')

    def __init__(self, p: Path):
        self.filename: str = str(p)
        self.length: float = 0
        self.metadata: dict = {}
        self.samplerate: float = 0
        self.channels: int = 0

    @abstractmethod
    def get_format(self) -> str:
        """Return a string detailing the file format."""
        ...

class PlaylistOggEntry(PlaylistEntry):
    """An Ogg Vorbis file playlist entry."""

    def __init__(self, p: Path):
        super().__init__(p)
        tagParser = get_tags(str(p))
        info = tagParser.get_info()
        self.filename = str(p)
        self.length = info['length']
        self.samplerate = info['samplerate']
        self.channels = info['channels']
        self.metadata = tagParser.get_tags()

    def get_format(self) -> str:
        return "Ogg Vorbis"

## Playlists

class Playlist(ABC):
    """Base class that represents a playlist."""

    def __init__(self, items: list[Path], *, title=None):
        """
        Construct a playlist from file.

        Being that it is an abstract class,
        Playlist has to be subclassed, and its
        abstract methods have to be overriden.
        """
        self.entries: list[PlaylistEntry] = []
        self.title: str | None = title
        for item in items:
            cls = get_playlist_entry(str(item))
            item = cls(item)
            self.entries.append(item)

    @abstractmethod
    def get_string(self) -> str:
        """Return the playlist file as a string."""

class MplPlaylist(Playlist):
    """Represents a Mpl playlist format."""

    def __init__(self, items: list[Path], **kw):
        """
        Construct mpl (MPlayer) playlist from ITEMS.

        Each index in ITEMS should be a Path to a file.

        **KW is captures keyword options for Playlist.
        """
        super().__init__(items, **kw)

    def get_string(self) -> str:
        msgList: list[str] = []
        for entry in self.entries:
            _file = Path(entry.filename).resolve()
            msgList.append(str(_file))

        return "\n".join(msgList)

class M3UPlaylist(Playlist):
    """Represents a M3u playlist format."""

    _artist_re: re.Pattern = re.compile(r'\s*-\s*')

    def __init__(self, items: list[Path], **kw):
        """
        Construct m3u playlist from ITEMS.

        Each index in ITEMS should be a Path to a file.

        **KW is captures keyword options for Playlist.
        """
        super().__init__(items, **kw)

    def __make_file_entry(self, entry: PlaylistEntry) -> str:
        # Artist (optional), title
        title: str = entry.metadata.get('title') or ''
        if not title:
            title = Path(entry.filename).stem

        artist: str = entry.metadata.get('artist') or ''
        if artist:
            artist = f"{artist} - "

        res = "#EXTINF:%d,%s%s\n" % \
            (round(entry.length), artist, self._artist_re.sub(': ', title))

        # Absolute path to the file
        res += entry.filename.replace(' ', '%20')

        return res + "\n"

    def get_string(self) -> str:
        msg = "#EXTM3U\n"

        if self.title:
            msg += f"#PLAYLIST:{self.title}\n"

        for entry in self.entries:
            msg += self.__make_file_entry(entry)
        return msg

PlaylistType = Type[Playlist]
PlaylistEntryType = Type[PlaylistEntry]

PLAYLIST_FACTORIES = {
    'm3u': M3UPlaylist,
    'mpl': MplPlaylist
}

PLAYLIST_ENTRY_FACTORIES = {
    'ogg': PlaylistOggEntry
}

def get_playlist(_format: str) -> PlaylistType:
    """
    Return the correct playlist type according to _FORMAT.

    The returned type can be constructed with a list
    of paths as the argument.
    """
    res = PLAYLIST_FACTORIES.get(_format)
    if res is None:
        raise ValueError(f"invalid extension '{_format}'")

    return res

def get_playlist_entry(filename: str) -> PlaylistEntryType:
    """
    Return the correct playlist entry type according to FILENAME.

    The returned type can be constructed with FILENAME as the argument.
    """
    ext = get_file_extension(filename)
    if ext is None:
        raise ValueError(f"invalid filename '{filename}': no extension")

    res = PLAYLIST_ENTRY_FACTORIES.get(ext)
    if res is None:
        raise ValueError(f"invalid extension '{ext}'", filename)

    return res
