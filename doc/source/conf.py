import sphinx_rtd_theme

import rsync_watch

html_theme = 'sphinx_rtd_theme'
html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]

extensions = []
extensions += ['sphinx.ext.autodoc']
extensions += ['sphinx.ext.intersphinx']
extensions += ['sphinx.ext.viewcode']
extensions += ['sphinxarg.ext']

templates_path = ['_templates']
source_suffix = '.rst'

master_doc = 'index'

project = u'rsync_watch'
copyright = u'2019, Josef Friedrich'
author = u'Josef Friedrich'
version = rsync_watch.__version__
release = rsync_watch.__version__
language = None
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']
pygments_style = 'sphinx'
todo_include_todos = False
html_static_path = []
htmlhelp_basename = 'rsync_watchdoc'
autodoc_default_options = {
    'members': True,
    'undoc-members': True,
    'private-members': True,
    'show-inheritance': True,
}
intersphinx_mapping = {'python': ('https://docs.python.org/3', None)}
