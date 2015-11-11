# Lychee

*Lychee* is an MEI document manager.

## License

*Lychee* is copyrighted according to the terms of the GNU GPLv3+. A copy of the license is held in
the file called "LICENSE."

## Install for Development

For the nCoda prototype, with a targeted launch in September 2016, we're using the PyPy 4.0 series.
This is a Python 2 interpreter. Download it from http://pypy.org/download.html. We do recommend
writing Python 3 compatible code whenever possible, for which reason you may also want to maintain
a test environment with a CPython 3 interpreter.

1. Set up a virtualenv and activate it.
1. Update the default ``pip`` and ``setuptools``, which may not be able to successfully install
   the dependencies: ``pip install -U pip setuptools``.
1. Comment out the repository-based dependencies (Abjad and Lychee) in "pip_freeze_pypy40".
1. Run ``pip install -r pip_freeze_pypy40`` to install the dependencies.
1. Install Abjad.
   1. Check https://pypi.python.org/pypi/Abjad to see if Abjad 2.17 has been released. If so, run
      ``pip install Abjad`` to install it.
   1. Otherwise clone the Abjad repository from https://github.com/Abjad/abjad, checkout commit
      7e3af7f66, then install it by running ``pip install -e .`` in the abjad directory.
1. Then install Lychee by running ``pip install -e .`` in the Lychee directory.
1. And finally... run ``py.test`` in the Lychee directory to run the automated test suite, and make
   sure that nothing is broken *before* you even start developing!

## Install for Deployment

Don't. It's not ready yet!
