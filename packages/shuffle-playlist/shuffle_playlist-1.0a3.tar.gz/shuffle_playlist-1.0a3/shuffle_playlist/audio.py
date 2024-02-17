"""Audio functions and classes."""

# Ogg Vorbis
from mutagen.oggvorbis import OggVorbis, OggVorbisInfo
from mutagen._vorbis import VCommentDict
from soundfile import SoundFile
from typing import TypedDict, Protocol, cast
import re

class TagDict(TypedDict):
    length: float
    channels: int
    samplerate: int
    bitrate: int

class ExSoundFile(SoundFile):
    @property
    def seconds(self) -> float:
        """Length in seconds."""
        return float(self.frames * self.channels) / float(self.samplerate)

class TagParser(Protocol):
    """A protocol for defining tag objects."""

    def get_tags(self) -> dict[str, str]:
        """
        Returns a dictionary with some metadata on the file.

        Possible keys are:
            * title (str)
            * album (str)
            * artist (str)
        """
        ...

    def get_info(self) -> TagDict:
        """
        Returns a dictionary with information about the file.

        Possible keys are:
            * length (float) - length in seconds
            * channels (int) - number of audio channels
            * samplerate (int) - samplerate in hertz
            * bitrate (int) - audio bitrate
        """
        ...

class OggTagParser:
    def __init__(self, filename: str):
        self.__ogg = OggVorbis(filename)

    def get_tags(self) -> dict[str, str]:
        tags: VCommentDict = cast(VCommentDict, self.__ogg.tags)
        res = {k:v for (k,v) in tags}
        return res

    def get_info(self) -> TagDict:
        info: OggVorbisInfo = cast(OggVorbisInfo, self.__ogg.info)
        res = {
            'length': info.length,
            'channels': info.channels,
            'samplerate': info.sample_rate,
            'bitrate': info.bitrate
        }
        return TagDict(**res)

AUDIO_TAG_FACTORIES = {
    'ogg': OggTagParser
}

_ext_re = re.compile(r'(?i)\.([a-z0-9]+)')

def get_file_dict(filename: str) -> dict:
    """
    Return a dictionary with information about FILENAME.

    The returned dictionary contains the following:
        * length (float) - the length of the song in seconds
        * filename (str) - the name of the file with the leading path removed
        * samplerate (float) - the samplerate of the file
        * channels (int) - the number of channels
    """
    res = {}

    with ExSoundFile(filename) as snf:
        res['length'] = snf.seconds
        res['filename'] = snf.name
        res['samplerate'] = snf.samplerate
        res['channels'] = snf.channels

    return res

def get_tags(filename: str) -> TagParser:
    """
    Return the metadata tags for FILENAME.

    FILENAME can be a str or bytes.

    The returned object is a working implementation
    that fits the structure of `TagParser`.

    Raises:
        ValueError
            - if the file has no extension
            - if the extension is not supported
    """
    m = _ext_re.search(filename)
    if m is None:
        raise ValueError(f"invalid filename '{filename}': missing extension")
    ext = m[1]

    cls = AUDIO_TAG_FACTORIES.get(ext)
    if cls is None:
        raise ValueError(f"invalid extension '{ext}'", filename)
    res: TagParser = cls(filename)

    return res

__all__ = [
    # Classes
    'TagParser',

    # Functions
    'get_tags',
    'get_file_dict'
]
