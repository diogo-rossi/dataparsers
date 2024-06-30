# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# %% -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import shutil
import sys

# Add source to path
sys.path.insert(0, os.path.abspath("."))

# process the module file and readme file
from process_module import process_module
from process_readme import process_readme

process_module()
process_readme()

import dataparsers
from dataparsers import arg, parse

# %% -- Project information -----------------------------------------------------

project = "dataparsers"
copyright = "2024, Diogo Rossi"
author = "Diogo Rossi"


# %% -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "myst_parser",
    "sphinx_copybutton",
    "sphinx.ext.doctest",
    "sphinx.ext.intersphinx",
    "sphinx.ext.extlinks",
    "sphinxnotes.comboroles",
]

maximum_signature_line_length = 70

# Napoleon settings
napoleon_google_docstring = True
napoleon_numpy_docstring = False

# Copy button settings
copybutton_exclude = ".linenos, .gp, .go"
copybutton_prompt_text = ">>> "

# Inter-sphinx settings
intersphinx_mapping = {"python": ("https://docs.python.org/3", None)}

# Ext-links settings
extlinks = {
    "original": ("https://docs.python.org/3/library/argparse.html#%s", "%s"),
    "argument": ("2_available_functions.html#%s", "%s"),
}

# Combo-roles settings
comboroles_roles = {
    "original_link": ["literal", "original"],
    "argument_link": ["literal", "argument"],
}

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = []


# %% -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "furo" # sphinx_rtd_theme
html_title = '<p style="text-align: center"><b>dataparsers</b></p>'

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]
html_logo = "logo.png"

html_theme_options = {
    # 'logo_only': True,
    'display_version': True,
    # "sidebar_hide_name": True,
}

html_css_files = ["css/custom.css"]

default_role = "code"
