"""
notsetuptools
=============

This package attempts to correct the namespace hacks provided
by setuptools so that they're actually useable.

>>> from notsetuptools import setup
>>> setup(
>>>     namespace_packages=['package'],
>>>     # ...
>>> )
"""

from setuptools import setup

setup(
    name='notsetuptools',
    version='0.1',
    description='A hack to fix setuptools namespace packages hack.',
    long_description=__doc__,
    author='David Cramer',
    author_email='dcramer@gmail.com',
    packages=['notsetuptools'],
    zip_safe=False,
)
