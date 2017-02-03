# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

version = '0.11'
name = 'knp-utils'
short_description = 'Wrapper scripts for Japanese parser `KNP`'
author = 'Kensuke Mitsuzawa'
author_email = 'kensuke.mit@gmail.com'
url = 'https://github.com/Kensuke-Mitsuzawa/knp-utils-py'
license = 'MIT'
classifiers = [
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Natural Language :: Japanese",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.5"
        ]

try:
    import pypandoc
    long_description = pypandoc.convert('README.md', 'rst')
except(IOError, ImportError):
    long_description = open('README.md').read()


install_requires = ['joblib', 'typing', 'six']
dependency_links = []

setup(
    name=name,
    version=version,
    description=short_description,
    long_description=long_description,
    author=author,
    author_email=author_email,
    install_requires=install_requires,
    dependency_links=dependency_links,
    url=url,
    license=license,
    packages=find_packages(exclude='tests'),
    classifiers=classifiers,
    test_suite='tests' #added
)