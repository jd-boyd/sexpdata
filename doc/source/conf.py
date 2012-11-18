# -*- coding: utf-8 -*-

import sys
import os

sys.path.insert(0, os.path.abspath('../..'))

# -- General configuration ----------------------------------------------------

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.intersphinx',
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# The suffix of source filenames.
source_suffix = '.rst'

# The master toctree document.
master_doc = 'index'

# General information about the project.
project = u'sexpdata'
copyright = u'2012, Takafumi Arakaki'

# The short X.Y version.
version = '0.0.2'
# The full version, including alpha/beta/rc tags.
release = '0.0.2.dev0'

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
exclude_patterns = []

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = 'sphinx'


# -- Options for HTML output --------------------------------------------------

html_theme = 'default'

#html_theme_options = {}

html_static_path = []  # default: ['_static']

# Output file base name for HTML help builder.
htmlhelp_basename = 'sexpdatadoc'


# -- Options for LaTeX output -------------------------------------------------

latex_elements = {
# The paper size ('letterpaper' or 'a4paper').
#'papersize': 'letterpaper',

# The font size ('10pt', '11pt' or '12pt').
#'pointsize': '10pt',

# Additional stuff for the LaTeX preamble.
#'preamble': '',
}

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title,
#  author, documentclass [howto/manual]).
latex_documents = [
  ('index', 'sexpdata.tex', u'sexpdata Documentation',
   u'Takafumi Arakaki', 'manual'),
]


# -- Options for manual page output -------------------------------------------

# One entry per manual page. List of tuples
# (source start file, name, description, authors, manual section).
man_pages = [
    ('index', 'sexpdata', u'sexpdata Documentation',
     [u'Takafumi Arakaki'], 1)
]


# -- Options for Texinfo output -----------------------------------------------

# Grouping the document tree into Texinfo files. List of tuples
# (source start file, target name, title, author,
#  dir menu entry, description, category)
texinfo_documents = [
  ('index', 'sexpdata', u'sexpdata Documentation',
   u'Takafumi Arakaki', 'sexpdata', 'One line description of project.',
   'Miscellaneous'),
]


# Example configuration for intersphinx: refer to the Python standard library.
intersphinx_mapping = {'http://docs.python.org/': None}
