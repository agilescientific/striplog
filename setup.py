# -*- coding: utf-8 -*-
"""
Python installation file.

:copyright: 2016 Agile Geoscience
:license: Apache 2.0
"""
from setuptools import setup
import re

verstr = 'unknown'
VERSIONFILE = "striplog/_version.py"
with open(VERSIONFILE, "r")as f:
    verstrline = f.read().strip()
    pattern = re.compile(r"__version__ = ['\"](.*)['\"]")
    mo = pattern.search(verstrline)
if mo:
    verstr = mo.group(1)
else:
    raise RuntimeError("Unable to find version string in %s." % (VERSIONFILE,))

REQUIREMENTS = ['numpy',
                'matplotlib',
                'scipy'
                ]

TEST_REQUIREMENTS = ['pytest',
                     'coveralls',
                     'pytest-cov',
                     'pytest-mpl'
                     ]

CLASSIFIERS = ['Development Status :: 4 - Beta',
               'Intended Audience :: Science/Research',
               'Natural Language :: English',
               'License :: OSI Approved :: Apache Software License',
               'Operating System :: OS Independent',
               'Programming Language :: Python',
               'Programming Language :: Python :: 3.4',
               'Programming Language :: Python :: 3.5',
               'Programming Language :: Python :: 3.6',
               'Programming Language :: Python :: 3.7',
               ]

setup(name='striplog',
      version=verstr,
      description='Tools for making and managing 1D subsurface data.',
      url='http://github.com/agile-geoscience/striplog',
      author='Agile Scientific',
      author_email='hello@agilescientific.com',
      license='Apache 2',
      packages=['striplog'],
      tests_require=TEST_REQUIREMENTS,
      test_suite='run_tests',
      install_requires=REQUIREMENTS,
      classifiers=CLASSIFIERS,
      zip_safe=False,
      )
