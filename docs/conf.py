#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
@author:    george wang
@datetime:  2019-06-30
@file:      tasks.py
@contact:   georgewang1994@163.com
@desc:      文档配置
"""

import os
import sys
sys.path.insert(0, os.path.abspath('../..'))

ablog_builder = 'dirhtml'
ablog_website = '_website'

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.doctest',
    'sphinx.ext.intersphinx',
    'sphinx.ext.todo',
    'sphinx.ext.ifconfig',
    'sphinx.ext.extlinks',
    #'IPython.sphinxext.ipython_directive',
    #'IPython.sphinxext.ipython_console_highlighting',
    'alabaster',
]

#language = 'de'
#language = 'tr'
# PROJECT

version = release = "0.0.17"
project = u'Ammonia'
copyright = u'2014-2015, Ammonia'
master_doc = 'index'
source_suffix = '.rst'
exclude_patterns = ['_build']


# HTML OUTPUT

html_title = "Ammonia"
html_static_path = ['_static']
html_use_index = True
html_domain_indices = False
html_show_sourcelink = True
html_favicon = '_static/icon.ico'

# SPHINX

intersphinx_mapping = {
    'python': ('http://docs.python.org/', None),
    'sphinx': ('http://sphinx-doc.org/', None)
}
extlinks = {
    'wiki': ('http://en.wikipedia.org/wiki/%s', ''),
    'issue': ('https://github.com/GeorgeWang1994/Ammonia/issues/%s', 'issue '),
    'pull': ('https://github.com/GeorgeWang1994/Ammonia/pulls/%s', 'pull request '),
}

rst_epilog = '''
.. _Sphinx: http://sphinx-doc.org/
.. _Python: http://python.org
.. _Disqus: http://disqus.com/
.. _GitHub: https://github.com/GeorgeWang1994/Ammonia
.. _PyPI: https://pypi.org/project/Ammonia
.. _Read The Docs: https://readthedocs.org/
.. _Alabaster: https://github.com/bitprophet/alabaster
'''

import re
from sphinx import addnodes


event_sig_re = re.compile(r'([a-zA-Z-]+)\s*\((.*)\)')

def parse_event(env, sig, signode):
    m = event_sig_re.match(sig)
    if not m:
        signode += addnodes.desc_name(sig, sig)
        return sig
    name, args = m.groups()
    signode += addnodes.desc_name(name, name)
    plist = addnodes.desc_parameterlist()
    for arg in args.split(','):
        arg = arg.strip()
        plist += addnodes.desc_parameter(arg, arg)
    signode += plist
    return name


def setup(app):
    from sphinx.ext.autodoc import cut_lines
    from sphinx.util.docfields import GroupedField
    app.connect('autodoc-process-docstring', cut_lines(4, what=['module']))
    app.add_object_type('confval', 'confval',
                        objname='configuration value',
                        indextemplate='pair: %s; configuration value')
    fdesc = GroupedField('parameter', label='Parameters',
                         names=['param'], can_collapse=True)
    app.add_object_type('event', 'event', 'pair: %s; event', parse_event,
                        doc_field_types=[fdesc])
