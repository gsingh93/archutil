#!/usr/bin/env python

from distutils.core import setup

import shutil

shutil.copyfile('archutil.py', 'archutil')

setup(name='archutil',
      version='0.1',
      description='A tool for listing and backing up explicitly installed packages and for managing config files',
      author='Gulshan Singh',
      author_email='gsingh2011@gmail.com',
      url='https://github.com/gsingh93/archutil',
      scripts=['archutil'],
     )
