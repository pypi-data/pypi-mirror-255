#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [ 'pyyaml>=5.1.2' ]

setup(
    author="dem4ply",
    author_email='dem4ply@gmail.com',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: Public Domain',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.8',
    ],
    description="small lib to proccess the keys of the dict like attributes",
    install_requires=requirements,
    license="WTFPL",
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='chibi_atlas',
    name='chibi_atlas',
    packages=find_packages(include=['chibi_atlas', 'chibi_atlas.*']),
    url='https://github.com/dem4ply/chibi_atlas',
    version='1.0.2',
    zip_safe=False,
)
