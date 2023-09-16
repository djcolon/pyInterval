# pyInterval

**Daniel Colon - 16/09/2023**

## Summary

Software to compile an mp3 file by splicing different mp3 files together at
certain durations to allow the creation of a music track used for interval
training.

There are no unit tests as I knocked this out on a Saturday morning as a little
private utility. I thought I'd share it should anyone find it useful.

## Installation

pyinterval was built and tested using wsl.

pyInterval uses [poetry](https://python-poetry.org), which will need to be
[installed first](https://python-poetry.org/docs/#installation).

After poetry is installed, install pyInterval's dependencies:
```sh
poetry install
```

The program uses pydub which relies on ffmpeg, install it using your
distribution's package manager:

```sh
# Debian/Ubuntu
sudo apt-get install ffmpeg
```

## Debugging

Using visual studio code (launched from wsl if running in wsl!) you can use a
standard debug gonfig (just press F5), but make sure the correct interpreter is
selected. After installing with poetry, run `poetry env info` and copy the
Virtualenv `Executable` path, and set it as your interpreter by clicking in the
bottom right of vscode when working in cli.py
([see also...](https://code.visualstudio.com/docs/python/environments)).

## Attribution

The program relies heavily on [pydub](https://github.com/jiaaro/pydub).

All mp3 files used in the samples come from
[incompetech](https://incompetech.com/).

Excepting three_beeps which is by [Joseph Sardin](https://bigsoundbank.com/sound-2645-dial-tone-call-ends.html)

Example c25k timings taken from [Tom Benninger](https://www.reddit.com/r/C25K/comments/kr5va/visual_c25k/)

## Usage

```sh
poetry run pyInterval
```

Which will generate an mp3 files from the example.
If the combined source files are too short to cover the defined intervals they
will be looped.
