# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

version = '0.1'
name = 'knp-utils'
short_description = ''
author = 'Kensuke Mitsuzawa'
author_email = 'kensuke.mit@gmail.com'
url = ''
license = 'MIT'


with open('README.md') as f:
    readme = f.read()


install_requires = ['joblib', 'typing', 'six']
dependency_links = []

setup(
    name=name,
    version=version,
    description='',
    long_description=readme,
    author=author,
    author_email=author_email,
    install_requires=install_requires,
    dependency_links=dependency_links,
    url=url,
    license=license,
    packages=find_packages(exclude='tests'),
    test_suite='tests' #added
)