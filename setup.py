#!/usr/bin/env python3

from setuptools import setup

setup(
  name = 'bottle-authenticate',
  version = '0.2',
  description = 'Authentication for Bottle',
  author = 'Leon Merten Lohse',
  author_email = 'leon@green-side.de',
  url = 'https://www.github.com/llohse/bottle-authenticate',
  license = 'MIT',
  platforms = 'any',
  py_modules = [ 'bottle_authenticate', ],
  install_requires = ['bottle>=0.9',],
  classifiers = [
      'Environment :: Web Environment',
      'Intended Audience :: Developers',
      'License :: OSI Approved :: MIT License',
      'Operating System :: OS Independent',
      'Programming Language :: Python',
      'Programming Language :: Python :: 3',
      'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
      'Topic :: Software Development :: Libraries :: Python Modules'
      ]
  )
