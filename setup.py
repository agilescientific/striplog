# -*- coding: utf 8 -*-
"""
Python installation file.
"""
from setuptools import setup

REQUIREMENTS = ['numpy',
                'pillow',
                'matplotlib'
                ]

CLASSIFIERS = ['Development Status :: 4 - Beta',
               'Intended Audience :: Science/Research',
               'Natural Language :: English',
               'License :: OSI Approved :: Apache Software License',
               'Operating System :: OS Independent',
               'Programming Language :: Python',
               ]

setup(name='striplog',
      version='0.4.2',
      description='Tools for making and managing well data.',
      url='http://github.com/agile-geoscience/striplog',
      author='Agile Geoscience',
      author_email='hello@agilegeoscience.com',
      license='Apache 2',
      packages=['striplog'],
      download_url='https://github.com/agile-geoscience/tarball/0.4.2',
      install_requires=REQUIREMENTS,
      classifiers=CLASSIFIERS,
      zip_safe=False,
)
