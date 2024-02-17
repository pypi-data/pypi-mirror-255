#!/usr/bin/env python

from io import open
from setuptools import setup

"""
:authors: EvgeniBondarev
:license: OSI Approved :: Apache Software License
:copyright: (c) 2024 EvgeniBondarev
"""

version = '0.0.1'

with open('README.md', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='nn_drawer',
    version=version,

    author='nn_drawer',
    author_email='peoplesdreamer@gmail.ru',

    description=(
        u'нструмент для визуализации структуры нейронных сетей.'
        u'Этот инструмент помогает исследователям, разработчикам и обучающимся визуально представить архитектуру своих нейронных сетей, что может быть полезным для понимания внутренней организации модели.'
    ),
    long_description=long_description,
    long_description_content_type='text/markdown',

    url='https://github.com/EvgeniBondarev/Neural-Network-Drawer.git',
    download_url='https://github.com/EvgeniBondarev/Neural-Network-Drawer/archive/refs/heads/master.zip',

    license='Apache License, Version 2.0, see LICENSE file',

    packages=['nn_drawer'],
    install_requires=['matplotlib'],

    classifiers=[
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Programming Language :: Python :: Implementation :: CPython',
    ]
)

