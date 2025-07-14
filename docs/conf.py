"""
Configuration file for the Sphinx documentation builder.
"""

import os
import sys

# Add apilinker to the path
sys.path.insert(0, os.path.abspath('..'))

# Project information
project = 'ApiLinker'
copyright = '2025, ApiLinker Team'
author = 'ApiLinker Team'

# The full version, including alpha/beta/rc tags
from apilinker import __version__
release = __version__

# General configuration
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.viewcode',
    'sphinx.ext.napoleon',
    'sphinx.ext.intersphinx',
    'sphinx.ext.autosectionlabel',
    'sphinx_rtd_theme',
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# Options for HTML output
html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']

# Napoleon settings
napoleon_google_docstring = True
napoleon_numpy_docstring = False
napoleon_include_init_with_doc = True
napoleon_include_private_with_doc = False

# Intersphinx mapping
intersphinx_mapping = {
    'python': ('https://docs.python.org/3', None),
    'httpx': ('https://www.python-httpx.org', None),
}

# AutoAPI settings
autoapi_type = 'python'
autoapi_dirs = ['../apilinker']
autoapi_template_dir = '_templates/autoapi'
autoapi_add_toctree_entry = True

# Generate configuration for autosectionlabel
autosectionlabel_prefix_document = True
