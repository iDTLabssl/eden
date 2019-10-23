#!/usr/bin/env python
# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014, 2015 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/eden/license

from setuptools import setup, find_packages

try:  # for pip >= 10
    from pip._internal.req import parse_requirements
    from pip._internal.download import PipSession
except ImportError:  # for pip <= 9.0.3
    from pip.req import parse_requirements
    from pip.download import PipSession

# LONG_DESCRIPTION = open('README.rst').read()
REQUIREMENTS = [str(ir.req) for ir in parse_requirements('requirements.txt', session=PipSession())
                if not (getattr(ir, 'link', False) or getattr(ir, 'url', False))]

setup(
    name='Eden',
    version='0.0.9',
    description='Eden Core library',
    long_description='Eden Core library',
    author='Salton Massally',
    author_email='salton.massally@gmail.com',
    url='https://github.com/idtlabssl/eden',
    license='GPLv3',
    platforms=['any'],
    packages=find_packages(exclude=['tests']),
    test_suite='nose.collector',
    tests_require=['nose', 'httmock', 'mock'],
    install_requires=REQUIREMENTS,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ]
)
