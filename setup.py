#!/usr/bin/env python3

from setuptools import setup, find_packages
import lychee  # for metadata


setup(
    name = lychee.__metadata__['name'],
    version = lychee.__metadata__['version'],
    packages = find_packages(exclude=['*.tests']),
    install_requires = (
        'Abjad==2.17',
        'grako>=3.14,<3.15',
        'lxml>3,<4',
        'mercurial<3.5',
        'mercurial-hug>0.4',
        'signalslot',
    ),
    extras_require = {
        'devel': (
            'mock',
            'pytest>3,<4',
            'python-coveralls',
            'pytest-cov',
            'sphinx',
        ),
    },

    # metadata for upload to PyPI
    author = lychee.__metadata__['author'],
    author_email = lychee.__metadata__['author_email'],
    description = lychee.__metadata__['description'],
    license = lychee.__metadata__['license'],
    url = lychee.__metadata__['url'],
    # TODO: keywords, long_description, download_url, classifiers, etc.
)
