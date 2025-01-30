# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path('..', 'src').resolve()))
sys.path.insert(0, os.path.abspath('_extension'))

project = 'SunFlare'
copyright = '2024, Jacopo Abramo'
author = 'Jacopo Abramo'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    "sphinx.ext.githubpages",
    'sphinx.ext.intersphinx',
    'myst_parser'
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

intersphinx_mapping = {
    # TODO: figure out how this works
    # 'bluesky': ('https://blueskyproject.io/bluesky/', None),
}

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'pydata_sphinx_theme'
html_static_path = ['_static']
html_context = {
   # this doesn't really matter;
   # adding it only for completion
   "default_mode": "auto"
}

html_css_files = [
    'custom.css',
]

html_js_files = [
    'custom.js',
]

source_suffix = {
    '.rst': 'restructuredtext',
    '.md': 'markdown',
}

# Enable figure numbering
numfig = True

napoleon_numpy_docstring = True
autodoc_typehints = 'description'
