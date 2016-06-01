#!/usr/bin/env python

from setuptools import setup

setup(name='tonicidentifier_makam',
      version='1.3.1',
      description='An Automatic Tonic Identification Method for Turkish '
                  'Makam Music Recordings',
      author='Hasan Sercan Atli',
      url='https://github.com/hsercanatli/tonic_identifier',
      packages=['tonicidentifier'],
      install_requires=[
          "numpy",
          "matplotlib",
      ],
      )
