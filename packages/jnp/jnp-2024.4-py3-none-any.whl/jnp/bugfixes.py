#!/usr/bin/env python3
'''
Fix for syntax highlighting with Code in Jupyter Lab:
https://github.com/ipython/ipython/issues/11747
'''
from IPython.display import Code
from pygments import highlight
from pygments.formatters import HtmlFormatter


def _jupyterlab_repr_html_(self):
    fmt = HtmlFormatter()
    style = (
        f'<style>{fmt.get_style_defs(".output_html")}\n'
        f'{fmt.get_style_defs(".jp-RenderedHTML")}</style>'
    )
    return style + highlight(self.data, self._get_lexer(), fmt)


Code._repr_html_ = _jupyterlab_repr_html_
