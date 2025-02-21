# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

import sys
from sunflare import __version__
from pathlib import Path

sys.path.insert(0, str(Path("..", "src").resolve()))

project = "SunFlare"
copyright = "2024, Jacopo Abramo"
author = "Jacopo Abramo"


release = __version__.split(".dev")[0]
github_user = "redsun-acquisition"
github_repo = "sunflare"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.githubpages",
    "sphinx.ext.intersphinx",
    "sphinx.ext.autosummary",
    "sphinxcontrib.mermaid",
    "sphinx_design",
    "myst_parser",
]

templates_path = ["_templates"]
exclude_patterns = ["_build"]

intersphinx_mapping = {
    "bluesky": ("https://blueskyproject.io/bluesky/main", None),
    "event_model": ("https://blueskyproject.io/event-model/main", None),
}

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "pydata_sphinx_theme"
html_static_path = ["_static"]
html_context = {
    # this doesn't really matter;
    # adding it only for completion
    "default_mode": "auto",
    "version": release,  # Sets the current version dynamically
    "versions": [
        ("latest", "/docs/latest/"),  # Development version
        ("stable", "/docs/stable/"),  # The latest stable version (0.3.5)
        ("0.3.5", "/docs/0.3.5/"),  # Explicitly tagged 0.3.5 version
    ],
}

html_theme_options = {
    "icon_links": [
        {
            "name": "GitHub",
            "url": f"https://github.com/{github_user}/{github_repo}",
            "icon": "fa-brands fa-square-github",
            "type": "fontawesome",
        }
    ],
    "switcher": {"json_url": "docs/_static/switcher.json", "version_match": release},
    "navbar_start": ["navbar-logo", "version-switcher"],
}

mermaid_version = "11.4.0"
myst_fence_as_directive = ["mermaid"]
myst_enable_extensions = ["attrs_block", "colon_fence"]

html_css_files = [
    "custom.css",
]

source_suffix = {
    ".rst": "restructuredtext",
    ".md": "markdown",
}

napoleon_numpy_docstring = True
autodoc_typehints = "description"

myst_heading_anchors = 3
