#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# ==========================================
# Copyright 2023 Yang 
# ararpy - setup
# ==========================================
#
#
#

import setuptools
import pathlib

here = pathlib.Path(__file__).parent.resolve()
long_description = (here / 'README.md').read_text(encoding='utf-8')

options = {
    "name": 'pdf-maker',  #
    "version": '0.0.3',  # version
    "author": 'Yang Wu',
    "author_email": 'wuycug@hotmail.com',
    "description": 'A module for creating PDF files',  # short description
    "long_description": long_description,  # detailed description in README.md
    "long_description_content_type": 'text/markdown',
    "url": 'https://github.com/wuyangchn/pdf-maker.git',  # github url
    "packages": setuptools.find_packages(),
    "package_data": {'pdf_maker': ['resources/*']},
    "install_requires": [
      "numpy",
    ],
    "classifiers": [
      'Development Status :: 3 - Alpha',
      'Programming Language :: Python :: 3',
      'License :: OSI Approved :: MIT License',
      'Operating System :: OS Independent',
    ],
    "python_requires": '>=3.5',
}

setuptools.setup(**options)
