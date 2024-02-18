#!/usr/bin/env python3
'''
Presentation export manager.
'''

import logging
import os
import pathlib
import shutil
import tempfile

from jnp.common import ENCODING, NAME
from jnp.config import Config
from jnp.css import generate_sizes_css
from jnp.file import copy
from jnp.notebook import nbconvert


LOGGER = logging.getLogger(__name__)


class Manager():
    '''
    Presentation export manager.
    '''
    def __init__(self, config_path=None):
        '''
        Args:
            config_path:
                The path to the configuration file. If None, it will use an
                internal configuration file with default options.
        '''
        self.config = Config(path=config_path)

    @property
    def public_dir(self):
        '''
        The directory in which to publish the presentations and associated files.
        '''
        return self.config.public_dir

    @property
    def public_notesbooks_dir(self):
        '''
        The directory of published presentations.
        '''
        return self.public_dir / 'notebooks'

    def clean(self):
        '''
        Remove the public directory.
        '''
        pub_dir = self.public_dir
        LOGGER.info('Removing %s', pub_dir)
        try:
            shutil.rmtree(pub_dir)
        except FileNotFoundError:
            pass

    @staticmethod
    def _insert_links(line, placeholder, links):
        '''
        '''
        # Preserve indentation.
        start, end = line.split(placeholder, 1)
        link_indent = ' ' * (len(start) - len(start.lstrip()))
        end_indent = link_indent
        if start.strip():
            yield start
            link_indent += ' ' * 2
        for link in links:
            yield f'{link_indent}{link}'
        if end.strip():
            yield f'{end_indent}{end}'

    @staticmethod
    def _get_index_display_name(path):
        '''
        Get the display name of the given path for the index page.

        Args:
            path:
                An instance of pathlib.Path.

        Returns:
            The display name.
        '''
        name = path.name.split('.')
        for suffix in ('html', 'slides'):
            if name[-1] == suffix:
                name = name[:-1]
        return '.'.join(name)

    def _publish_index_page(self):
        '''
        Publish the index page with links to the published notebooks.
        '''
        config = self.config
        pub_dir = self.public_dir
        pub_notebook_dir = self.public_notesbooks_dir
        hrefs = (
            path.relative_to(pub_dir)
            for path in pub_notebook_dir.glob('*.html')
        )
        links = sorted(
            f'<li><a href="{href}">{self._get_index_display_name(href)}</a></li>'
            for href in hrefs
        )
        index_path = pub_dir / 'index.html'
        LOGGER.info('Publishing %s', index_path)
        placeholder = config.placeholder
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_dir = pathlib.Path(tmp_dir)
            tmp_path = tmp_dir / index_path.name
            with tmp_path.open('w', encoding=ENCODING) as handle:
                try:
                    index_html = config.index_template.read_text(encoding=ENCODING)
                except FileNotFoundError as err:
                    raise FileNotFoundError(f'Failed to load index template: {err}') from err
                for line in index_html.splitlines():
                    if placeholder in line:
                        for mod_line in self._insert_links(line, placeholder, links):
                            handle.write(f'{mod_line}\n')
                    else:
                        handle.write(f'{line}\n')
            copy(tmp_path, index_path)

    def _interpolate_css_variables(self, inpath, outpath):
        ''''
        Interpolate the CSS variables into the input path and save it to the
        output path.

        Args:
            inpath:
                The input path.

            outpath:
                The output path.
        '''
        variables = Config.CSS_VARIABLES.copy()
        variables.update(self.config.css_variables)
        variable_block = '\n'.join(
            f'  --{name}: {value};'
            for name, value in variables.items()
        )
        css = inpath.read_text(encoding=ENCODING).replace(
            r'/* %VARIABLES% */',
            variable_block
        )
        outpath.parent.mkdir(parents=True, exist_ok=True)
        outpath.write_text(css, encoding=ENCODING)

    def _copy_input_files(self):
        '''
        Copy input files to the ouput directory.
        '''
        # Switch to pathlib.walk when Python 3.12 becomes widespread.
        for root, dirs, fils in os.walk(self.config.input_dir):
            root = pathlib.Path(root)
            dirs[:] = [d for d in dirs if root / d != self.config.notebook_dir]
            for fil in fils:
                inpath = root / fil
                rel_path = inpath.relative_to(self.config.input_dir)
                outpath = self.config.public_dir / rel_path
                copy(inpath, outpath)

    def copy_static_files(self, dir_path):
        '''
        Copy jnp's internal static files to a directory.

        Args:
            dir_path:
                The output directory.
        '''
        css_dir = dir_path / f'css/{NAME}'
        for path in self.config.static_css_files:
            out_path = css_dir / path.name
            if path.name == 'main.css':
                self._interpolate_css_variables(path, out_path)
            else:
                copy(path, out_path)
        generate_sizes_css(css_dir / 'sizes.css')

    def publish(self):
        '''
        Publish all files to the public directory.
        '''
        config = self.config

        self.copy_static_files(self.public_dir)
        self._copy_input_files()

        pub_notebook_dir = self.public_notesbooks_dir
        empty = True
        for path in config.notebooks:
            empty = False
            nbconvert(config, path, pub_notebook_dir)
        if empty:
            LOGGER.warning('No notebooks found in %s', config.notebook_dir)

        self._publish_index_page()
