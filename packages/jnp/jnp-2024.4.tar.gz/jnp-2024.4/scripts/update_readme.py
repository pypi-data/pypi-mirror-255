#!/usr/bin/env python3
'''
Update command output in the README file.

Dependencies;
* [tree](https://gitlab.com/OldManProgrammer/unix-tree)
* [vimdiff](https://www.vim.org/)
'''

import filecmp
import logging
import pathlib
import re
import shutil
import subprocess
import tempfile


ENCODING = 'utf-8'
LOGGER = logging.getLogger(__name__)
JNP_DIR = pathlib.Path(__file__).resolve().parent.parent


def update_command_output(match):
    '''
    Update the command output for the given regex match.

    Args:
        match:
            The Match object.

    Returns:
        The update output block.
    '''
    indent = match['indent']
    label = match['label'].strip()
    lang = match['lang'].strip()
    tree_cmd = ('tree', '--prune', '--noreport', '-n')
    cmds = {
        'input_dir': [*tree_cmd, 'presentations'],
        'public_dir': [*tree_cmd, 'public'],
        'config_file': ['jnp', '--create-config', '-'],
        'help': ['jnp', '--help'],
        'html_cell': ['jnp', '--html-cell'],
        'index_page': ['jnp', '--copy-index-template', '-']
    }
    try:
        cmd = cmds[label]
    except KeyError:
        LOGGER.error('Unrecognized label in README: %s', label)
        return match.group(0)

    cwd = str(JNP_DIR)
    output = subprocess.run(
        cmd,
        check=True,
        stdout=subprocess.PIPE,
        cwd=cwd,
    ).stdout.decode(ENCODING).strip()
    output = '\n'.join(f'{indent}{line}' for line in output.split('\n'))
    return f'{indent}[output: {label}]: #\n{indent}~~~{lang}\n{output}\n{indent}~~~\n'


def main():
    '''
    Update command output in the README file.
    '''
    # Remove and recreate the public directory to ensure that only the intended
    # files will appear in the "tree" output.
    public_dir = JNP_DIR / 'public'
    LOGGER.info('Removing %s', public_dir)
    try:
        shutil.rmtree(public_dir)
    except FileNotFoundError:
        pass
    LOGGER.info('Running jnp')
    subprocess.run(['jnp'], check=True, cwd=JNP_DIR)

    readme_path = JNP_DIR / 'README.md'
    text = readme_path.read_text(encoding=ENCODING)
    regex = re.compile(
        r'^(?P<indent>\s*)\[output: (?P<label>.+?)\]: #\n'
        r'(?P=indent)~~~(?P<lang>.*?)\n'
        r'.*?^(?P=indent)~~~\n',
        re.MULTILINE | re.DOTALL
    )
    text = regex.sub(update_command_output, text)
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_dir = pathlib.Path(tmp_dir)
        tmp_path = tmp_dir / readme_path.name
        tmp_path.write_text(text, encoding=ENCODING)
        if not filecmp.cmp(tmp_path, readme_path):
            subprocess.run(['vimdiff', str(tmp_path), str(readme_path)], check=True)


if __name__ == '__main__':
    logging.basicConfig(
        style='{',
        format='[{asctime}] {levelname} {message}',
        datefmt='%y-%m-%d %H:%M:%s',
        level=logging.INFO
    )
    try:
        main()
    except KeyboardInterrupt:
        pass
