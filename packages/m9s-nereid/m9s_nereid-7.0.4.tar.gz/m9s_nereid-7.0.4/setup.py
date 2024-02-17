#!/usr/bin/env python3
# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.

import io
import os
import re

from setuptools import find_packages, setup

MODULE2PREFIX = {
    'nereid_base', 'm9s',
    'nereid_test', 'm9s',
    }

def read(fname):
    return io.open(
        os.path.join(os.path.dirname(__file__), fname),
        'r', encoding='utf-8').read()


def get_version():
    init = read(os.path.join('nereid', '__init__.py'))
    return re.search('__version__ = "([0-9.]*)"', init).group(1)


def get_require_version(name):
    require = '%s >= %s.%s, < %s.%s'
    require %= (name, major_version, minor_version,
        major_version, minor_version + 1)
    return require


version = get_version()
major_version, minor_version, _ = version.split('.', 2)
major_version = int(major_version)
minor_version = int(minor_version)
name = 'm9s_nereid'
download_url = 'https://gitlab.com/m9s/nereid.git'
requires = [
    get_require_version('m9s-nereid-base'),
    #get_require_version('m9s-trytond'),
    'cachelib',
    'secure-cookie',
    'pytz',
    'flask',
    'flask-wtf',
    'blinker',
    'speaklater',
    'Flask-Babel',
    'Flask-Login',
    'email_validator',
    ]

tests_require = [
    'pycountry>=16.11.08',
    get_require_version('m9s-nereid-base'),
    get_require_version('m9s-nereid-test'),
    ]

setup(name=name,
    version=version,
    description='Tryton Nereid Module',
    long_description=read('README.md'),
    long_description_content_type='text/markdown',
    author='MBSolutions',
    author_email='info@m9s.biz',
    url='https://www.m9s.biz/',
    download_url=download_url,
    project_urls={
        "Bug Tracker": 'https://support.m9s.biz/',
        "Source Code": 'https://gitlab.com/m9s/nereid.git',
        },
    keywords='',
    packages=[
        'nereid',
        'nereid.contrib',
        'nereid.tests',
        'trytond.modules.nereid_test',
        ],
    package_dir={
        'nereid': 'nereid',
        'nereid.contrib': 'nereid/contrib',
        'nereid.tests': 'tests',
        'trytond.modules.nereid_test': 'nereid_test_module',
        },
    package_data={
        'trytond.modules.nereid_test': (['*.xml']
            + ['tryton.cfg', 'locale/*.po', 'tests/*.rst',
                'templates/*.*', 'templates/tests/*.*']),
        },
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Plugins',
        'Framework :: Tryton',
        'Intended Audience :: Developers',
        'Intended Audience :: Financial and Insurance Industry',
        'Intended Audience :: Legal Industry',
        'License :: OSI Approved :: '
        'GNU General Public License v3 or later (GPLv3+)',
        'Natural Language :: Bulgarian',
        'Natural Language :: Catalan',
        'Natural Language :: Chinese (Simplified)',
        'Natural Language :: Czech',
        'Natural Language :: Dutch',
        'Natural Language :: English',
        'Natural Language :: Finnish',
        'Natural Language :: French',
        'Natural Language :: German',
        'Natural Language :: Hungarian',
        'Natural Language :: Indonesian',
        'Natural Language :: Italian',
        'Natural Language :: Persian',
        'Natural Language :: Polish',
        'Natural Language :: Portuguese (Brazilian)',
        'Natural Language :: Romanian',
        'Natural Language :: Russian',
        'Natural Language :: Slovenian',
        'Natural Language :: Spanish',
        'Natural Language :: Turkish',
        'Natural Language :: Ukrainian',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: Implementation :: CPython',
        'Topic :: Office/Business',
        ],
    license='GPL-3',
    python_requires='>=3.8',
    install_requires=requires,
    extras_require={
        'test': tests_require,
        },
    zip_safe=False,
    )
