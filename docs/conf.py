# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
# import os
# import sys
# sys.path.insert(0, os.path.abspath('.'))


# -- Project information -----------------------------------------------------
import gitflow_linter

project = 'gitflow_linter'
copyright = '2021, Poul Fighter'
author = 'Poul Fighter'

# The full version, including alpha/beta/rc tags
release = '0.0.3'

# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = ['sphinx.ext.autodoc', 'sphinx.ext.autosectionlabel']

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'nature'

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

command = 'gitflow-linter'
url = 'https://github.com/fighterpoul/gitflow_linter.git'

rst_epilog = """
.. |version| replace:: {versionnum}
.. |project| replace:: {project}
.. |command| replace:: {command}
.. |url| replace:: {url}
.. |doc_url| replace:: {doc_url}
.. |settings_file| replace:: {settings_file}
""".format(
    versionnum=release,
    project=project,
    command=command,
    url=url,
    doc_url='https://fighterpoul.github.io/gitflow_linter/',
    settings_file=gitflow_linter.DEFAULT_LINTER_OPTIONS,
)
