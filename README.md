# Lychee

*Lychee* is an engine for MEI document management and conversion.

[![CircleCI](https://circleci.com/gh/nCoda/lychee.svg?style=svg)](https://circleci.com/gh/nCoda/lychee)

We recommend you use the [nCoda Setup Program](https://goldman.ncodamusic.org/diffusion/NC/) to
install *Lychee*. The instructions below describe part of what that program does.


## License

*Lychee* is copyrighted according to the terms of the GNU GPLv3+. A copy of the license is held in
the file called "LICENSE."

The *Lychee* logo is modified from a file on the
[Wikimedia Commons](https://commons.wikimedia.org/wiki/File:Litchi_chinensis_fruits.JPG), borrowed
for use under the terms of the [CC-BY-SA 3](https://creativecommons.org/licenses/by-sa/3.0/deed.en)
licence.


## Python 2 and 3; CPython and PyPy

Currently *Lychee* runs in Python 2 only, but should run in both CPython and PyPy. You can follow
our progress on Python 3 support with [T116](https://goldman.ncodamusic.org/T116) on the nCoda
Phabricator installation.

Why only Python 2? Mercurial is integrated in *Lychee* (via the `mercurial-hug` library) and
Mercurial only runs in Python 2. They have serious and legitimate problems with Python 3, so we are
working on alternative solutions.


## Install for Development

These instructions produce a virtualenv with *Lychee* only. If you plan to use *Lychee* with the
*Fujian* server, follow the instructions below in the "Install with Fujian" section. You can
install *Fujian* at any time; if you're unsure, don't install it now.

1. Set up a virtualenv and activate it.
    1. ``virtualenv /path/to/virtualenv``
    1. ``source /path/to/virtualenv/bin/activate``
1. Change into the Lychee root directory.
1. Update the default ``pip`` and ``setuptools``, which otherwise may not be capable of installing
   the dependencies: ``pip install -U pip setuptools``.
1. Clone the ssh://vcs@goldman.ncodamusic.org/diffusion/HUG/mercurial-hug.git repository to a
   sibling directory of the "lychee" directory.
1. Run ``pip install -e .`` from the "mercurial-hug" directory.
1. Run ``pip install -e ".[devel]"`` in the "lychee" directory to install the dependencies.
1. Then install Lychee by running ``pip install -e .`` in the Lychee directory.
1. Finally, run ``py.test`` in the Lychee directory to run the automated test suite, and make
   sure that nothing is broken *before* you even start developing!


## Install with Fujian

These instructions will produce a virtualenv for use with Lychee and *Fujian* together, which may
be used as a back-end for the *Julius* nCoda user interface.

1. Set up a *Lychee* virtualenv by following the steps in the "Install for Development" section.
1. Clone *Fujian* (not into the *Lychee* directory) from
   ssh://vcs@goldman.ncodamusic.org/diffusion/FJ/fujian.git. The top-level *Lychee* directory and
   the *Fujian* directory should be siblings (that is, they should be in the same directory).
1. Run ``pip install -e .`` in the ``fujian`` directory to install *Fujian*.


## Run with Fujian

Start the monstrosity by activating the virtualenv and running ``python -m fujian`` from any directory.


## Install for Deployment

Don't.


## Troubleshooting

If you get a segfault, delete the `__pycache__` directories and try again.
