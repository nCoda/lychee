# Lychee

*Lychee* is an engine for MEI document management and conversion.

[![CircleCI](https://circleci.com/gh/nCoda/lychee.svg?style=svg)](https://circleci.com/gh/nCoda/lychee)

## License

*Lychee* is copyrighted according to the terms of the GNU GPLv3+. A copy of the license is held in
the file called "LICENSE."

The *Lychee* logo is modified from a file on the
[Wikimedia Commons](https://commons.wikimedia.org/wiki/File:Litchi_chinensis_fruits.JPG), borrowed
for use under the terms of the [CC-BY-SA 3](https://creativecommons.org/licenses/by-sa/3.0/deed.en)
licence.

## Python 2 and 3; CPython and PyPy

For the nCoda prototype, with a targeted launch in September 2016, we're targeting the PyPy 4.0
series as our runtime environment. This is a Python 2 environment. We will not hold ourselves to
compatibility with CPython or Python 3, but we should attempt to write portable code when possible.

You can download Pypy from http://pypy.org/download.html.

Lychee will primarily target Python 3 for the first nCoda milestone after a Python 3.3 compatible
PyPy interpreter becomes available.

## Install for Development

These instructions will produce a virtualenv for use with Lychee only. If you plan to use Lychee
with the *Fujian* PyPy server and *Julius*, you must also follow the instructions below in the
"Install with Fujian" section. You can install *Fujian* at any time; it simply adds packages to the
virtualenv.

1. Set up a virtualenv and activate it.
    1. ``virtualenv -p /path/to/pypy /path/to/virtualenv``
    1. ``source /path/to/virtualenv/bin/activate``
1. Change into the Lychee root directory.
1. Update the default ``pip`` and ``setuptools``, which otherwise may not be capable of installing
   the dependencies: ``pip install -U pip setuptools``.
1. Clone the ssh://vcs@goldman.ncodamusic.org/diffusion/10/mercurial-hug.git repository to a sibling
   directory of the "lychee" directory.
1. Run ``pip install -e .`` from the "mercurial-hug" directory.
1. Run ``pip install -r pip_freeze_pypy40`` in the "lychee" directory to install the dependencies.
1. Then install Lychee by running ``pip install -e .`` in the Lychee directory.
1. Finally, run ``py.test`` in the Lychee directory to run the automated test suite, and make
   sure that nothing is broken *before* you even start developing!

## Install with Fujian

These instructions will produce a virtualenv for use with Lychee and *Fujian* together, which may
be used as a back-end for the *Julius* nCoda user interface.

1. Set up a Lychee virtualenv by following the steps in the "Install for Development" section.
1. Clone *Fujian* (*not* into the Lychee directory) from git@jameson.adjectivenoun.ca:ncoda/fujian.git
   The top-level Lychee directory and the Fujian directory should probably be siblings (that is,
   they should be contained in the same directory).
1. From the "fujian" directory, checkout the "ncoda" branch: ``git checkout ncoda``. This branch
   has a minor change that allows Lychee to run, which should not be pushed to GitHub. (If we do
   accidentally push it to GitHub, it's not a problem, just useless to everyone not using
   *Fujian* with nCoda).
1. Run ``pip install "tornado<5"`` (with the double quote marks) to install *Tornado*.
1. Run ``pip install -e .`` in the ``fujian`` directory to install *Fujian*.

## Run with Fujian

Start the Lychee/*Fujian* monstrosity by activating the virtualenv and running ``python -m fujian``
from any directory.

## Install for Deployment

Don't. It's not ready yet!

## Troubleshooting

If you get a segfault, delete the `__pycache__` directories and try again.
