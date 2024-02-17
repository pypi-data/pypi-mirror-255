#!/usr/bin/env python
import os
import sys
from codecs import open

from setuptools import setup, find_packages

CURRENT_PYTHON = sys.version_info[:2]
REQUIRED_PYTHON = (3, 8)

if CURRENT_PYTHON < REQUIRED_PYTHON:
    sys.stderr.write(
        """
==========================
Unsupported Python version
==========================
This version of Requests requires at least Python {}.{}, but
you're trying to install it on Python {}.{}. To resolve this,
consider upgrading to a supported Python version.
If you can't upgrade your Python version, you'll need to
pin to an older version of Requests (<2.28).
""".format(
            *(REQUIRED_PYTHON + CURRENT_PYTHON)
        )
    )
    sys.exit(1)


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name='robotcloud-client',
    version='0.0.11',
    author="Bernat Galmés Rubert",
    author_email="bernat.galmes@robotbas.com",
    description="Client to interact with robotcloud API from a python project.",
    url='https://github.com/robotmallorca/sw.module.python.robotcloud.client',
    keywords="client,robotcloud",
    packages=find_packages(include=['robotcloud', 'robotcloud.endpoints', 'robotcloud.utils', 'robotcloud.utils.datatables']),
    long_description=read('README.md'),
    python_requires=">=3.8.0",
    install_requires=[
        'requests>=2.28'
    ],
    setup_requires=['flake8']
)
