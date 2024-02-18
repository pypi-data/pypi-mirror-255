#!/usr/bin/env python3
'''
Format text. This is only used for pretty-printing docstrings as comments in the
YAML configuration file output.
'''

import re
import textwrap


def docstring_to_comment(doc):
    '''
    Format a Python docstring as a YAML comment.

    Args:
        doc:
            The docstring.

    Returns:
        The comment string.
    '''
    # Strip superfluous whitespace.
    doc = textwrap.dedent(doc).strip()
    while '\n\n\n' in doc:
        doc = doc.replace('\n\n\n', '\n\n')

    # Split into blocks and then into subblocks based on indentation level.
    blocks = doc.split('\n\n')
    indent_re = re.compile(r'^(\s*)(.*)$')
    for i, block in enumerate(blocks):
        subblocks = []
        for line in block.splitlines():
            match = indent_re.match(line)
            indent = match.group(1)
            content = match.group(2)
            if not subblocks or subblocks[-1]['indent'] != indent:
                subblocks.append({'indent': indent, 'lines': [content]})
            else:
                subblocks[-1]['lines'].append(content)

        for j, subblock in enumerate(subblocks):
            indent = subblock['indent']
            text = '\n'.join(subblock['lines'])
            lines = textwrap.wrap(
                text,
                break_long_words=False,
                initial_indent=indent,
                subsequent_indent=indent
            )
            subblocks[j] = '\n'.join(f'# {line}' for line in lines)

        blocks[i] = '\n'.join(subblocks)

    return '\n#\n'.join(blocks)
