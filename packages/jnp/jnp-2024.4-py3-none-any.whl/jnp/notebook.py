#!/usr/bin/env python3
'''
Jupyter notebook functions.
'''

import logging
import pathlib
import re
import subprocess
import tempfile
from html.parser import HTMLParser
from xml.sax.saxutils import escape as xml_escape

from IPython.display import Code

from jnp.common import ENCODING
from jnp.file import copy


LOGGER = logging.getLogger(__name__)


class LinkParser(HTMLParser):
    '''
    HTML parser to check if a link's text matches its "href" attribute and
    append the "raw_link" class if it does.
    '''
    def __init__(self):
        super().__init__()
        self.attrs = {}
        self.data = None

    def handle_starttag(self, tag, attrs):
        self.attrs = dict(attrs)

    def handle_data(self, data):
        self.data = data

    def get_replacement(self):
        '''
        Return replacement text for the link if the "href" is the same as the
        link's text, else None.
        '''
        href = self.attrs.get('href', '')
        if not href or href in self.data:
            classes = self.attrs.get('class', set())
            if classes:
                classes = set(classes.split(','))
            classes.add('explicit_url')
            self.attrs['class'] = ','.join(sorted(classes))
            attrs = ' '.join(
                f'{key}="{xml_escape(value)}"'
                for (key, value) in sorted(self.attrs.items())
            )
            return f'<a {attrs}>{self.data}</a>'
        return None


def _add_link_classes(match):
    '''
    Add a custom CSS class to disable the display of the link's "href" URL after
    the link's text if the text already contains the URL. This function is
    passed to re.sub to update all of the links in the HTMl document.

    Args:
        match:
            The re.Match object.

    Returns:
        The update link element as a string.
    '''
    link = match.group(0)
    parser = LinkParser()
    parser.feed(link)
    replacement = parser.get_replacement()
    if replacement:
        return replacement
    return link


def _get_stylesheet_links(stylesheets):
    '''
    Get HTML link elements for the given stylesheet URLs.

    Args:
        stylesheets:
            An iterable of stylesheet URLs.

    Returns:
        A generator over HTML link elements.
    '''
    for stylesheet in stylesheets:
        yield f'<link rel="stylesheet" href="{xml_escape(stylesheet)}" />'


def notebook_html_cell(config):
    '''
    Get a Jupyter notebook HTML cell for including the stylesheets directly in
    the notebook.

    Args:
        config:
            The configuration object.

    Returns:
        A string with the cell contents.
    '''
    links = '\n'.join(_get_stylesheet_links(config.stylesheets))
    if links:
        return f'%%html\n{links}'
    return '# The configuration file does not specify any stylesheets.'


def nbconvert(config, path, out_dir):
    '''
    Convert a notebook to slides. This inserts some custom code into the output
    to handle sizing and aspect ratios.

    Args:
        config:
            The configuration object.

        path:
            The path to the notebook.

        out_dir:
            The output directory.

    '''

    # https://nbconvert.readthedocs.io/en/latest/config_options.html
    # https://revealjs.com/themes/
    path = pathlib.Path(path).resolve()
    out_dir = pathlib.Path(out_dir).resolve()
    # Output to a temporary directory (usually tmpfs) to avoid unnecessary disk
    # IO.
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_dir = pathlib.Path(tmp_dir)
        cmd = [
            'jupyter', 'nbconvert',
            '--log-level=WARN',
            f'--output-dir={tmp_dir}',
            '--to', 'slides',
            f'--CSSHTMLHeaderPreprocessor.style={config.pygments_style}',
            '--SlidesExporter.reveal_theme=white',
            f'--SlidesExporter.reveal_transition={config.transition}',
            '--SlidesExporter.reveal_number=h.v',
            '--TagRemovePreprocessor.remove_input_tags', 'hide_input',
            '--TagRemovePreprocessor.remove_all_outputs_tags', 'hide_output',
            str(path)
        ]
        LOGGER.info('Converting %s', path)
        LOGGER.debug('Running command: %s', cmd)
        subprocess.run(cmd, check=True)

        out_path = (out_dir / path.name).with_suffix('.slides.html')
        tmp_path = tmp_dir / out_path.name
        lines = tmp_path.read_text(encoding=ENCODING).splitlines()
        code = f'''
        const aspect_ratio = {config.aspect_ratio};
        const width = {config.width};
        Reveal.configure({{
          progress: true,
          hash: true,
          width: width,
          height: width / aspect_ratio
        }});
'''
        lines.insert(-6, code)

        for i, link in enumerate(_get_stylesheet_links(config.stylesheets)):
            lines.insert(4 + i, link)

        html = '\n'.join(lines)
        html = re.sub(r'<a .*?</a>', _add_link_classes, html)
        tmp_path.write_text(html)
        copy(tmp_path, out_path)

    return out_path


def display_command_output(cmd, language=None):
    '''
    Display command output in a Jupyter notebook cell.

    Args:
        cmd:
            The cmd, as a list. It will be run with subprocess.run.

        language:
            The language to use for syntax highlighting.

    Returns:
        The
    '''
    data = subprocess.run(cmd, check=True, stdout=subprocess.PIPE).stdout.decode()
    return Code(data=data, language=language)
