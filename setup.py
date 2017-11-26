#!/usr/bin/env python

import os
from distutils.core import setup

PROJECT = 'airbnb'
VERSION = '2.0.11'
URL = 'https://github.com/nderkach/airbnb-python'
AUTHOR = 'Nikolay Derkach'
AUTHOR_EMAIL = 'nderk@me.com'
DESC = "A wrapper for airbnb.com API"


def read_file(file_name):
    file_path = os.path.join(
        os.path.dirname(__file__),
        file_name
        )
    return open(file_path).read()

setup(
    name=PROJECT,
    version=VERSION,
    description=DESC,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    url=URL,
    license=read_file('LICENSE'),
    packages=['airbnb'],
    package_data = {'airbnb': ["files/*"]},
    classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "Operating System :: OS Independent",
        "License :: Public Domain",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Topic :: Internet :: WWW/HTTP",
        "Environment :: Console"
    ],
    install_requires=[
        'requests'
    ]
)
