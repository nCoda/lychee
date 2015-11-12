#!/usr/bin/env python3

from setuptools import setup, Command
import lychee  # for __version__


setup(
    name = 'Lychee',
    version = lychee.__version__,
    packages = ['lychee'],

    install_requires = [
        'Abjad>2.17',
        'signalslot>0.1,<0.2',
    ],

    # metadata for upload to PyPI
    author = 'Christopher Antila',
    author_email = 'christopher@antila.ca',
    description = 'The tastiest fruit around!',
    license = 'GPLv3+',
    url = 'http://ncodamusic.org/lychee',
    # TODO: keywords, long_description, download_url, classifiers, etc.
)
