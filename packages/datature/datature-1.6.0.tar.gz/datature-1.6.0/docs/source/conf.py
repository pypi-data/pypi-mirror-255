#!/usr/bin/env python
# -*-coding:utf-8 -*-
'''
  ████
██    ██   Datature
  ██  ██   Powering Breakthrough AI
    ██

@File    :   conf.py
@Author  :   Raighne.Weng
@Version :   1.6.0
@Contact :   developers@datature.io
@License :   Apache License 2.0
@Desc    :   Datature Python Doc
'''

import os
import sys

# pylint: disable=C0103,W0622
project = 'Datature Python SDK Documentation'
copyright = '2023, Datature'
author = 'Datature'
release = '0.6.4'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration
extensions = [
    'sphinx.ext.duration', 'sphinx.ext.doctest', 'sphinx.ext.autodoc',
    'sphinx.ext.autosummary', 'sphinx.ext.intersphinx',
    'sphinx_markdown_builder', 'sphinx.ext.napoleon'
]

templates_path = ['_templates']
exclude_patterns = []

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']
html_show_sourcelink = False
autodoc_member_order = 'bysource'

sys.path.insert(0, os.path.abspath('../../'))
