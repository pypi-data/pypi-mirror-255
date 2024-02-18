#!/usr/bin/env python3
'''
Generate CSS files.
'''

import logging
import pathlib

from jnp.common import ENCODING


LOGGER = logging.getLogger(__name__)


def generate_sizes_css(path):
    '''
    Generate a CSS file with a series of incremental classes.
    '''
    path = pathlib.Path(path).resolve()
    LOGGER.debug('Creating %s', path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', encoding=ENCODING) as handle:
        # Jupyter notebook strips out inline styles such as flex-basis that can
        # change the page layout so we create custom classes with 5% increments
        # as a work-around.
        for pct in range(5, 100, 5):
            handle.write(f'''.fb{pct} {{
  flex-basis: {pct}%;
}}
''')
        # reveal.js code height classes.
        for height in range(5, 40, 1):
            handle.write(f'''.reveal .ch{height} pre {{
  max-height: calc({height} * var(--jp-code-font-size)) !important;
  overflow: auto !important;
}}
.reveal .ch{height} pre * {{
  overflow: visible !important;
}}
''')
