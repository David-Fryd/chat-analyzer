# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'Chat Analyzer'
copyright = '2022, David Fryd'
author = 'David Fryd'
release = '1.0.1b1'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = ['sphinx.ext.autodoc', 'sphinxcontrib.programoutput']

templates_path = ['_templates']
exclude_patterns = []



# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

# html_theme = 'alabaster'
html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']


# # Autodoc config
import os
import sys
sys.path.insert(0, os.path.abspath('../../chat_analyzer'))

# apidocs genned thru: 'sphinx-apidoc -o ./source/apidoc ../chat_analyzer' while in the docs directory
# in order to regen docs, navigate to docs directory and run: 'make clean ; make html'