#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import setup, find_packages


with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
    'requests>=2.19.1', 'python-magic>=0.4.15', 'dateutils>=0.6.6',
    'xmltodict>=0.12.0', 'pyyaml>=5.1.2', 'chibi-donkey>=1.0.1',
    'Pillow>=10.1.0', 'chibi-atlas>=1.0.2' ]

setup(
    name='chibi',
    keywords='chibi',
    version='0.12.0',
    description='',
    long_description=readme + '\n\n' + history,
    license="WTFPL",
    author='dem4ply',
    author_email='',
    packages=find_packages(include=['chibi', 'chibi.*']),
    install_requires=requirements,
    dependency_links = [],
    url='https://github.com/dem4ply/chibi',
    zip_safe=False,
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: Public Domain',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ] )
