# Configuration file for the Sphinx documentation builder.
"""
Sphinx configuration for HireSense documentation.

This configuration enables:
- Shibuya theme (modern, clean documentation theme)
- MyST parser for Markdown support
- Napoleon for Google-style docstrings
- Autodoc for automatic API documentation
- Autosummary for generating module summaries
"""

import os
import sys

# Add project root to path for autodoc
sys.path.insert(0, os.path.abspath('..'))

# -- Project information -----------------------------------------------------

project = 'HireSense'
copyright = '2026, HireSense Team'
author = 'HireSense Team'
release = '1.0.0'
version = '1.0'

# -- General configuration ---------------------------------------------------

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.viewcode',
    'sphinx.ext.napoleon',
    'sphinx.ext.autosummary',
    'sphinx.ext.intersphinx',
    'myst_parser',
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store', '_archive']

# Source file suffixes
source_suffix = {
    '.rst': 'restructuredtext',
    '.md': 'markdown',
}

# -- Autodoc configuration ---------------------------------------------------

autodoc_default_options = {
    'members': True,
    'member-order': 'bysource',
    'special-members': '__init__',
    'undoc-members': True,
    'exclude-members': '__weakref__',
    'show-inheritance': True,
}

autodoc_typehints = 'description'
autodoc_typehints_format = 'short'

# -- Autosummary configuration -----------------------------------------------

autosummary_generate = True
autosummary_imported_members = False

# -- Napoleon configuration (Google-style docstrings) ------------------------

napoleon_google_docstring = True
napoleon_numpy_docstring = True
napoleon_include_init_with_doc = True
napoleon_include_private_with_doc = False
napoleon_include_special_with_doc = True
napoleon_use_admonition_for_examples = True
napoleon_use_admonition_for_notes = True
napoleon_use_admonition_for_references = True
napoleon_use_ivar = True
napoleon_use_param = True
napoleon_use_rtype = True
napoleon_type_aliases = None

# -- MyST parser configuration -----------------------------------------------

myst_enable_extensions = [
    'deflist',
    'colon_fence',
    'html_admonition',
    'smartquotes',
    'replacements',
    'linkify',
    'strikethrough',
    'tasklist',
]

myst_heading_anchors = 3

# -- Intersphinx configuration -----------------------------------------------

intersphinx_mapping = {
    'python': ('https://docs.python.org/3', None),
    'flask': ('https://flask.palletsprojects.com/en/latest/', None),
    'sqlalchemy': ('https://docs.sqlalchemy.org/en/20/', None),
}

# -- Options for HTML output -------------------------------------------------

# Try to use Shibuya theme, fallback to RTD theme, then alabaster
try:
    import shibuya
    html_theme = 'shibuya'
    html_theme_options = {
        'accent_color': 'green',
        'globaltoc_collapse': True,
        'globaltoc_maxdepth': 3,
    }
except ImportError:
    try:
        import sphinx_rtd_theme
        html_theme = 'sphinx_rtd_theme'
        html_theme_options = {
            'navigation_depth': 4,
            'collapse_navigation': False,
            'sticky_navigation': True,
        }
    except ImportError:
        html_theme = 'alabaster'

html_static_path = ['_static']
html_title = 'HireSense Documentation'
html_short_title = 'HireSense'
html_favicon = None
html_logo = None

# -- Options for other outputs -----------------------------------------------

# LaTeX output
latex_elements = {
    'papersize': 'letterpaper',
    'pointsize': '10pt',
}

# Manual pages
man_pages = [
    ('index', 'hiresense', 'HireSense Documentation', [author], 1)
]