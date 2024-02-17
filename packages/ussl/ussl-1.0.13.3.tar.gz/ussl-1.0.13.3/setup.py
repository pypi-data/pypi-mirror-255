#! /usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup

with open('README.md', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='ussl',
    author='ussc soc dev team',
    author_email='iushangaraev@ussc.ru, pbikkuzhina@ussc.ru',
    description='Пакет разработчиков USSC-SOC для упрощения взаимодействия с АРМ, серверами и сетевыми устройствами',
    long_description=long_description,
    long_description_content_type='text/markdown',
    version='1.0.13.3',
    packages=[
        'ussl',
        'ussl.model',
        'ussl.postprocessing',
        'ussl.protocol',
        'ussl.transport',
        'ussl.exceptions',
        'ussl.utils',
    ],
    install_requires=[
        'pywinrm==0.4.1',
        'paramiko==2.7.2',
        'marshmallow==3.20.2',
        'python-ldap==3.4.0', # адаптер https://www.lfd.uci.edu/~gohlke/pythonlibs/#python-ldap есть только для этой версии библиотеки
    ],
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.8'
    ]
)

# python setup.py sdist
# twine upload dist/*
