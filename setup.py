#!/usr/bin/env python

from setuptools import setup
from pkgutil import walk_packages


def get_packages():
    return [name
            for _, name, ispkg in walk_packages(".")
            if ispkg]


setup(
    name="pysesame2",
    version='1.0.0',
    author="Candyhouse Inc",
    author_email="cerberus@candyhouse.co",
    description="",
    license="MIT",
    platforms=['Linux', 'Mac OSX', 'Windows'],
    url="https://docs.candyhouse.co/",
    classifiers=[
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: POSIX',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    packages=get_packages(),
    entry_points={
        "console_scripts": [
            "sesame2=pysesame2.cli:main",
        ]
    },
    install_requires=['requests']
)
