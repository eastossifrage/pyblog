# -*- coding:utf-8 -*-
__author__ = '东方鹗'
__blog__ = 'http://www.os373.cn'


import mistune
from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import html
import re

'''
此处的数学公式的功能借鉴了 FMBlog 项目的代码，项目地址：
https://github.com/vc12345679/FMBlog

博客文章：《mistune的KaTeX数学公式扩展开发》——
https://blog.chensiwei.space/blog/mistune_extension_katex.html
'''
class KaTeXRenderer(mistune.Renderer):
    def __init__(self, *args, **kwargs):
        super(KaTeXRenderer, self).__init__(*args, **kwargs)

    def inlinekatex(self, text):
        return '<tex class="tex-inline">%s</tex>' % text

    def blockkatex(self, text):
        return '<tex class="tex-block">%s</tex>' % text


class KaTeXInlineLexer(mistune.InlineLexer):
    def __init__(self, *args, **kwargs):
        super(KaTeXInlineLexer, self).__init__(*args, **kwargs)
        self.enable_katexinline()

    def enable_katexinline(self):
        self.rules.inlinekatex = re.compile(r'^\${2}([\s\S]*?)\${2}(?!\$)')  # $$tex$$
        self.default_rules.insert(3, 'inlinekatex')
        self.rules.text = re.compile(r'^[\s\S]+?(?=[\\<!\[_*`~\$]|https?://| {2,}\n|$)')

    def output_inlinekatex(self, m):
        return self.renderer.inlinekatex(m.group(1))

'''# 为更适应 editor.md 的科学公式块的显示模式，除非有必要，此处不再设置块形式代码。
class KaTeXBlockLexer(mistune.BlockLexer):
    def __init__(self, *args, **kwargs):
        super(KaTeXBlockLexer, self).__init__(*args, **kwargs)
        self.enable_katexblock()

    def enable_katexblock(self):
        self.rules.blockkatex = re.compile(r'^\\\\\[(.*?)\\\\\]', re.DOTALL)  # \\[ ... \\]
        self.default_rules.insert(0, 'blockkatex')

    def parse_blockkatex(self, m):
        self.tokens.append({
            'type': 'blockkatex',
            'text': m.group(1)
        })

'''


class MyMarkdown(mistune.Markdown):
    def output_blockkatex(self):
        return self.renderer.blockkatex(self.token['text'])


'''
以下内容为加载一些扩展功能，如
    代码高亮，
    TOC功能，
    表格的 bootstrap 样式，
    图片居中
'''

class MyRenderer(KaTeXRenderer):
    def block_code(self, txt, lang, inlinestyles=False, linenos=False):
        """增加代码高亮功能"""
        if not lang:
            text = txt.strip()
            return u'<pre><code>%s</code></pre>\n' % mistune.escape(text)
        if lang not in ['katex', 'latex', 'math']:
            try:
                lexer = get_lexer_by_name(lang, stripall=True)
                formatter = html.HtmlFormatter(
                    noclasses=inlinestyles, linenos=linenos
                )
                code = highlight(txt, lexer, formatter)
                if linenos:
                    return '<div class="table-responsive">%s</div>\n' % code
                return code
            except:
                return '<pre class="%s"><code>%s</code></pre>\n' % (
                    lang, mistune.escape(txt)
                )
        else:
            return '<tex class="tex-block">%s</tex>' % mistune.escape(txt)

    def reset_toc(self):
        """增加 TOC 功能"""
        self.toc_tree = []
        self.toc_count = 0

    def header(self, text, level, raw=None):
        """增加 TOC 功能"""
        rv = '<h%d id="toc-%d">%s</h%d>\n' % (
            level, self.toc_count, text, level
        )
        self.toc_tree.append((self.toc_count, text, level, raw))
        self.toc_count += 1
        return rv

    def render_toc(self, level=3):
        """增加 TOC 功能"""
        """Render TOC to HTML.
        :param level: render toc to the given level
        """
        return ''.join(self._iter_toc(level))

    def _iter_toc(self, level):
        """增加 TOC 功能"""
        first_level = None
        last_level = None

        yield '<ul class="nav nav-pills flex-column">\n'

        for toc in self.toc_tree:
            index, text, l, raw = toc

            if l > level:
                # ignore this level
                continue

            if first_level is None:
                # based on first level
                first_level = l
                last_level = l
                yield '<li class="nav-item"><a class="nav-link" href="#toc-%d">%s</a>' % (index, text)
            elif last_level == l:
                yield '</li>\n<li class="nav-item"><a class="nav-link" href="#toc-%d">%s</a>' \
                      % (index, text)
            elif last_level == l - 1:
                last_level = l
                yield '<ul>\n<li class="nav-item"><a class="nav-link" href="#toc-%d">%s</a>' \
                      % (index, text)
            elif last_level > l:
                # close indention
                yield '</li>'
                while last_level > l:
                    yield '</ul>\n</li>\n'
                    last_level -= 1
                yield '<li class="nav-item"><a class="nav-link" href="#toc-%d">%s</a>' % (index, text)

        if last_level or first_level is not None:
            # close tags
            yield '</li>\n'
            while last_level > first_level:
                yield '</ul>\n</li class="nav-item">\n'
                last_level -= 1

        yield '</ul>\n'

    # 以下功能借鉴了该文章，网址为：
    # http://depado.markdownblog.com/2015-09-29-mistune-parser-syntax-
    # highlighter-mathjax-support-and-centered-images
    def table(self, header, body):
        return "<table class='table table-bordered table-hover'>" + header + body + "</table>"

    def image(self, src, title, text):
        if src.startswith('javascript:'):
            src = ''
        text = mistune.escape(text, quote=True)
        if title:
            title = mistune.escape(title, quote=True)
            html = '<img class="img-responsive center-block" src="%s" alt="%s" title="%s"' % \
                   (src, text, title)
        else:
            html = '<img class="img-responsive img-fluid center-block" src="%s" alt="%s"' % (src, text)
        if self.options.get('use_xhtml'):
            return '%s />' % html
        return '%s>' % html

