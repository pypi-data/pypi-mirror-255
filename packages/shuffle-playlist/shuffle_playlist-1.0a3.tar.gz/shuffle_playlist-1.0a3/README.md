# shuffle_playlist

Creates a shuffled m3u playlist from the files provided.

# Installation

Either install it from PyPi or clone this repository and install from its directory.

```sh
pip install shuffle-playlist
```

```sh
git clone https://github.com/JohnDevlopment/shuffle_playlist.git
cd shuffle_playlist
pip install .
```

# Usage

At its most basic, the commandline will look like this:

```sh
shuffle_playlist OUTPUT FILE [FILE ...]
```

For example:

```sh
shuffle-playlist playlist.m3u file1.ogg file2.ogg file3.ogg
```

You can either write the playlist to a file or specify `-` to print to stdout.
Playlists are in M3U format by default; however, you can also write to an mpl file (MPlayer playlist) by writing the output file to have a `.mpl` extension, or by using the `-f` option:

```sh
shuffle-playlist playlist.mpl file1.ogg file2.ogg file3.ogg
shuffle-playlist -f mpl - file1.ogg file2.ogg file3.ogg
```

For more information, pass `-h` to `shuffle-playlist`.
