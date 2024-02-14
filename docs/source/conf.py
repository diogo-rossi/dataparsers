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
import sys
import shutil

MODULE_FILE = "dataparsers.py"
EXTERNAL_LINKS = {
    "`parse_args()`": "https://docs.python.org/3/library/argparse.html#the-parse-args-method",
    "`add_argument()`": "https://docs.python.org/3/library/argparse.html#the-add-argument-method",
    "`add_argument_group()`": "https://docs.python.org/3/library/argparse.html#argparse.ArgumentParser.add_argument_group",
    "`add_mutually_exclusive_group()`": "https://docs.python.org/3/library/argparse.html#argparse.ArgumentParser.add_mutually_exclusive_group",
    "`ArgumentParser`": "https://docs.python.org/3/library/argparse.html#argumentparser-objects",
    "`argparse`": "https://docs.python.org/3/library/argparse.html#module-argparse",
    "`dataclasses`": "https://docs.python.org/3/library/dataclasses.html#module-dataclasses",
    "`dataclass`": "https://docs.python.org/3/library/dataclasses.html#dataclasses.dataclass",
}
INTERNAL_LINKS = ["`dest`"]

# Copy stub file to `source` file
shutil.copy(os.path.abspath(f"../../src/{MODULE_FILE}i"), os.path.abspath(f"./{MODULE_FILE}"))

# Add source to path
sys.path.insert(0, os.path.abspath("."))

from process_text import initial_docstring, remove_overloads, put_links_on_file
from replace_snippets import process_file

docstring = initial_docstring(MODULE_FILE).replace(
    "# dataparsers\n\nA wrapper", "# User manual\n\n`dataparsers` is a simple module that wrappers"
)

# remove overloads from the original stub file
remove_overloads(MODULE_FILE)

put_links_on_file(MODULE_FILE, EXTERNAL_LINKS, INTERNAL_LINKS)

# Put links for markdown version
for link in EXTERNAL_LINKS:
    docstring = docstring.replace(link, f"[{link}]({EXTERNAL_LINKS[link]})")

with open("1_user_manual.md", "w") as file:
    file.write(docstring)

process_file("1_user_manual.md", replace_notes=True, replace_snippets=True)

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
extlinks = {"original": ("https://docs.python.org/3/library/argparse.html#%s", "%s")}

# Combo-roles settings
comboroles_roles = {"literal_issue": ["literal", "original"]}

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
html_theme = "sphinx_rtd_theme"

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]

# html_css_files = ["css/custom.css"]

default_role = "code"
