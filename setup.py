#!/usr/bin/env python3

from setuptools import setup, Command
import lychee  # for metadata


setup(
    name = lychee.__metadata__['name'],
    version = lychee.__metadata__['version'],
    packages = ['lychee'],

    # metadata for upload to PyPI
    author = lychee.__metadata__['author'],
    author_email = lychee.__metadata__['author_email'],
    description = lychee.__metadata__['description'],
    license = lychee.__metadata__['license'],
    url = lychee.__metadata__['url'],
    # TODO: keywords, long_description, download_url, classifiers, etc.
)
