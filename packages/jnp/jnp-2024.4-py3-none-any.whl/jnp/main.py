#!/usr/bin/env python3
'''
Package entry points.
'''

import argparse
import logging
import pathlib
import sys


from jnp.common import ENCODING
from jnp.file import copy
from jnp.manager import Manager
from jnp.notebook import notebook_html_cell


LOGGER = logging.getLogger(__name__)


def _copy(arg_in, arg_out):
    '''
    Convenience function for copying input data to either a file path or STDOUT.

    Args:
        arg_in:
            Either a string or a Path object.

        arg_out:
            Either "-" or a file path.
    '''
    if isinstance(arg_in, pathlib.Path):
        if arg_out == '-':
            print(arg_in.read_text(encoding=ENCODING))
        else:
            copy(arg_in, arg_out)

    else:
        if arg_out == '-':
            print(arg_in)
        else:
            path = pathlib.Path(arg_out).resolve()
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(arg_in, encoding=ENCODING)


def main(args=None):
    '''
    Export Jupyter notebook presentations to a directory.
    '''
    logging.basicConfig(
        style='{',
        format='[{asctime}] {levelname} {message}',
        level=logging.INFO
    )
    parser = argparse.ArgumentParser(description=main.__doc__)
    parser.add_argument(
        '-c', '--config',
        type=pathlib.Path,
        help=('''
            The path to the YAML configuration file.
            If not given, default paths will be used.
        ''')
    )
    parser.add_argument(
        '--create-config',
        metavar='PATH',
        help=('''
            Create a default confuration file at the given path.
            If the path is "-" then print to STDOUT.
        ''')
    )
    parser.add_argument(
        '--copy-static',
        type=pathlib.Path,
        metavar='PATH',
        help=('''
            Copy internal static files to the given path.
            Use this to create modified copies of the internal files.
        ''')
    )
    parser.add_argument(
        '--copy-index-template',
        metavar='PATH',
        help=('''
            Copy the internal index template.
            The template can be used as a starting point for creating a custom
            index page.
            If the path is "-" then print to STDOUT.
        ''')
    )
    parser.add_argument(
        '--html-cell',
        action='store_true',
        help=('''
            Print a Jupyter notebook HTML cell that can be used to display CSS
            styles while editing the notebook. Copy and poste the content to a
            separate "code" cell and execute it.

            Copy the static files to the input directory with --copy-static so
            that Jupyter Lab can find them.
        ''')
    )
    pargs = parser.parse_args(args=args)

    if pargs.create_config:
        _copy(Manager().config.example, pargs.create_config)
        return

    if pargs.copy_index_template:
        _copy(Manager().config.index_template, pargs.copy_index_template)
        return

    manager = Manager(config_path=pargs.config)

    if pargs.html_cell:
        print(notebook_html_cell(manager.config))
        return

    if pargs.copy_static:
        manager.copy_static_files(pargs.copy_static)
        return

    manager.publish()


def run_main(args=None):
    '''
    Wrapper around main() to handle exceptions.

    Args:
        args:
            Passed through to main().
    '''
    try:
        main(args=args)
    except KeyboardInterrupt:
        pass
    except FileNotFoundError as err:
        sys.exit(str(err))
