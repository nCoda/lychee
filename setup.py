#!/usr/bin/env python3

from setuptools import setup, find_packages
from metadata import LYCHEE_METADATA
import versioneer


setup(
    name=LYCHEE_METADATA['name'],
    version=versioneer.get_version(),
    packages=find_packages(exclude=['*.tests']),
    install_requires=(
        'Abjad==2.17',
        'grako>=3.14,<3.15',
        'lithoxyl==0.4',
        'lxml>3,<4',
        'signalslot',
    ),
    extras_require={
        'devel': (
            'mock',
            'pytest>3,<4',
            'python-coveralls',
            'pytest-cov',
            'sphinx',
            'versioneer',
        ),
    },

    # metadata for upload to PyPI
    author=LYCHEE_METADATA['author'],
    author_email=LYCHEE_METADATA['author_email'],
    description=LYCHEE_METADATA['description'],
    license=LYCHEE_METADATA['license'],
    url=LYCHEE_METADATA['url'],
    cmdclass=versioneer.get_cmdclass(),
    # TODO: keywords, long_description, download_url, classifiers, etc.
)
