#!/usr/bin/env python3
'''
Configuration.
'''

import logging
import pathlib

import yaml

from jnp.common import NAME
from jnp.text import docstring_to_comment


LOGGER = logging.getLogger(__name__)


def _parse_variables(variables, defaults=None):
    '''
    Parse the CSS variables from the configurationf file and return a generator
    over key-value pairs. This is used to enable nesting of related variables in
    dicts. For example, instead of specifying each background property by it's
    full name (background-color, background-image, etc.), the properties can be
    nested under a common "background" field (background: color, image, etc.).

    Args:
        variables:
            The dict of CSS variables with possibly nested dicts.

        defaults:
            Default values for the dict to fill in missing values, including
            those from nested dicts.

    Returns:
        A generator over key-value pairs with the expanded variable names.
    '''
    all_keys = set((*variables.keys(), *defaults.keys()))
    for key in sorted(all_keys):
        value = variables.get(key, defaults.get(key))
        if isinstance(value, dict):
            subdefaults = defaults.get(key, {})
            for subkey, value in _parse_variables(value, defaults=subdefaults):
                yield f'{key}-{subkey}', value
        yield key, value


class Config():
    '''
    Configuration file reader.
    '''
    CSS_VARIABLES = {
        'jnp-main-color': '#1488ca',
        'jnp-h1-color': '#ffcd1c',
        'jnp-background': {
            'attachment': 'fixed',
            'color': '#ffffff',
            'image': 'none',
            'position': 'center',
            'repeat': 'no-repeat',
            'size': '100% 100%',
        },
        'jnp-radius': '10pt',
    }

    def __init__(self, path=None):
        '''
        Args:
            path:
                The path to the configuration file. If None, defaults values
                will be used for all settings relative to the current working
                directory.
        '''
        if path:
            path = pathlib.Path(path).resolve()
        else:
            path = None
            LOGGER.info('No configuration file given, using defaults.')
        self.path = path
        self._config = None
        self._cwd = pathlib.Path.cwd()

    @property
    def _root_dir(self):
        '''
        The root directory relative to which paths should be interpretted.
        '''
        if self.path:
            return self.path.parent
        return self._cwd

    @property
    def config(self):
        '''
        The configuration file object, or None if no path was given.
        '''
        if self.path and not self._config:
            LOGGER.info('Loading configuration file %s', self.path)
            with self.path.open('rb') as handle:
                self._config = yaml.safe_load(handle)
        return self._config

    def _get(self, key, default=None):
        '''
        Try to get a key from the configuration file.

        Args:
            key:
                The key to get.

            default:
                The default value to use when the key is not found.

        Returns:
            The value, or the default if the key was not found.
        '''
        try:
            value = self.config[key]
        except (TypeError, KeyError):
            value = None
        if value is None:
            value = default
        return value

    def _get_example_entry(self, name, *default):
        '''
        Get an entry for the example file.

        Args:
            name:
                The field/attribute name.

            default:
                If given, it will be used in place of the class's default value
                for this attribute.

        Returns:
            A YAML stub.
        '''
        doc = getattr(self.__class__, name).__doc__
        doc = docstring_to_comment(doc)
        if default:
            default = default[0]
        else:
            default = getattr(self, name)
            if isinstance(default, pathlib.Path):
                if default.is_relative_to(self._root_dir):
                    default = default.relative_to(self._root_dir)
                default = str(default)
        line = yaml.dump({name: default})
        return f'{doc}\n{line}'

    @property
    def example(self):
        '''
        An example configuration file.
        '''
        return f'''# jnp configuration file

{self._get_example_entry('transition')}
{self._get_example_entry('aspect_ratio')}
{self._get_example_entry('width')}
{self._get_example_entry('public_dir')}
{self._get_example_entry('input_dir')}
{self._get_example_entry('stylesheets')}
{self._get_example_entry('css_variables', self.CSS_VARIABLES)}
{self._get_example_entry('pygments_style')}
{self._get_example_entry('index_template', None)}
{self._get_example_entry('placeholder')}
'''.strip()

    @property
    def transition(self):
        '''
        The reveal.js slide transition effect. This is passed through to
        nbconvert's SlidesExporter.reveal_transition option. For the list of
        supported values, see

            https://nbconvert.readthedocs.io/en/latest/config_options.html
        '''
        return self._get('transition', default='slide')

    @property
    def aspect_ratio(self):
        '''
        The presentation's aspect ratio.
        '''
        return self._get('aspect_ratio', default=1.6)

    @property
    def width(self):
        '''
        The presentation's width. The presentation will scale to the screen so
        this basically just adjusts the size of text and other elements.
        '''
        return self._get('width', default=1100)

    @property
    def public_dir(self):
        '''
        The directory in which to publish the presentations.
        '''
        return self._root_dir / self._get('public_dir', default='public')

    @property
    def stylesheets(self):
        '''
        CSS stylesheets to include in the exported HTML slides. These will be
        interpretted relative to the public directory.

        The default list includes the custom stylesheets provided by jnp. These
        can be supplemented, modified or replaced with the users own
        stylesheets. The default files will be created automatically when jnp
        exports the slides.

        For example, "../css/custom.css" will load "<public_dir>/css/custom.css"
        from a notebook located in "<public_dir>/notebooks".
        '''
        subpath = f'../css/{NAME}/'
        names = ('main.css', 'sizes.css', 'reveal.css')
        return self._get('stylesheets', default=[f'{subpath}{name}' for name in names])

    @property
    def css_variables(self):
        '''
        The default main.css stylesheet supports limited configuration via the
        following variables:

            jnp-main-color:
                The main color of the presentation's theme (H1 header
                backgrounds, H2 header text, links, etc.)

            jnp-h1-color:
                The text color of H1 headers displayed on jnp_main_color
                backgrounds.

            jnp-background:
                The CSS background properties (color, image, position, etc.):

                For details, see https://www.w3schools.com/cssref/css3_pr_background.php

            jnp-radius:
                Border radius of H1 header backgrounds, code blocks, images, etc.
        '''
        variables = self._get('css_variables', default=self.CSS_VARIABLES)
        return dict(_parse_variables(variables, defaults=self.CSS_VARIABLES))

    @property
    def pygments_style(self):
        '''
        The Pygments syntax highlighting style to use. The list of available
        styles can be displayed with the command "pygmentize -L styles". An
        online preview of the built-in styles is available here:

            https://pygments.org/styles/
        '''
        return self._get('pygments_style', default='default')

    @property
    def _resource_dir(self):
        '''
        An iterable of this package's resource file paths.
        '''
        #  m_path = importlib.resources.files('jnp.resources')
        #  return pathlib.Path(m_path.joinpath(''))
        return pathlib.Path(__file__).resolve().parent / 'resources'

    @property
    def static_css_files(self):
        '''
        An iterable of the static CSS filepaths.
        '''
        for path in self._resource_dir.glob('*.css'):
            yield path

    @property
    def input_dir(self):
        '''
        The directory containing the Jupyter notebooks and associated files for
        the presentation. This directory should contain a subdirectory named
        "notebooks" with the Jupyter notebook files (.ipynb file extension). The
        rest of the files in the directory will be symlinked to the output
        directory when jnp is run.
        '''
        return self._root_dir / self._get('input_dir', default='presentations')

    @property
    def notebook_dir(self):
        '''
        The directory containing the Jupyter notebook files.
        '''
        return self.input_dir / 'notebooks'

    @property
    def notebooks(self):
        '''
        An iterable over Jupyter notebook files to convert to presentations.
        '''
        yield from self.notebook_dir.glob('*.ipynb')

    @property
    def index_template(self):
        '''
        The index page template file path.
        '''
        path = self._get('index_template')
        if path:
            return self.path.parent / path
        return self._resource_dir / 'index.html'

    @property
    def placeholder(self):
        '''
        The placeholder variable for the list of links in the index template.
        '''
        return self._get('placeholder', default='%NOTEBOOK_LINKS%')
