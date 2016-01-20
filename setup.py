#!/usr/bin/env python

from setuptools import setup

setup(name='makamtonicidentifier',
      version='1.0',
      description='An Automatic Tonic Identification Method for Turkish Makam Music Recordings',
      author='Hasan Sercan Atli',
      url='https://github.com/hsercanatli/tonic_identifier',
      packages=['tonicidentifier'], requires=['numpy', 'pypeaks']
      )
