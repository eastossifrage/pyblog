# -*- coding:utf-8 -*-
__author__ = '东方鹗'


import misaka as m
from pygments import highlight
from pygments.formatters.html import HtmlFormatter
from pygments.lexers import get_lexer_by_name


class CustomRenderer(m.HtmlRenderer):
	def blockcode(self, text, lang):
		if not lang:
			return u'\n<pre><code>{}</code></pre>\n'.format(text.strip())
		lexer = get_lexer_by_name(lang, stripall=True)
		formatter = HtmlFormatter(linenos='inline')

		return highlight(code=text, lexer=lexer, formatter=formatter)

	def table(self, content):

		return u'\n<table class="table table-bordered table-hover">{}</table>\n'.format(content.strip())

