# -*- coding: utf-8 -*-
import sys
import os
sys.path.insert(0, os.path.abspath('..'))

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.viewcode',
    'sphinx.ext.napoleon',
]

templates_path = ['_templates']
source_suffix = '.rst'
master_doc = 'index'

project = u'reFrameD'
copyright = u'2024, James Tuck, Kevin Volkel'
author = u'James Tuck, Kevin Volkel'
version = '1.1'
release = '1.1.1'

pygments_style = 'sphinx'
html_theme = 'default'
html_static_path = ['_static']
exclude_patterns = ['_build']
