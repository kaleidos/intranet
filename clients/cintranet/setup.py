#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from setuptools import setup, find_packages

setup(
    name = 'cintranet',
    version = ":versiontools:cintranet:",
    description = "Kaleidos intranet command line client",
    long_description = "",
    keywords = 'cmd',
    author = 'Yamila Moreno',
    author_email = 'yamila.moreno@kaleidos.net',
    url = 'https://github.com/kaleidos/intranet',
    license = 'BSD',
    include_package_data = True,
    packages = find_packages(),
    package_data={},
    install_requires=[
        'termcolor',
        'requests',
    ],
    # other arguments here...
    entry_points = {
        'console_scripts': [
            'cintranet = cintranet.cintranet:main_loop',
        ],
    },

    setup_requires = [
        'versiontools >= 1.8',
    ],
    test_suite = 'nose.collector',
    tests_require = ['nose >= 1.2.1'],
    classifiers = [
        "Programming Language :: Python",
        'Development Status :: 4 - Beta',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP',
    ]
)
