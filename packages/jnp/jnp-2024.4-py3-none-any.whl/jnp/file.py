#!/usr/bin/env python3
'''
File functions.
'''

import errno
import filecmp
import logging
import os
import pathlib
import shutil


LOGGER = logging.getLogger(__name__)


def symlink(path, target):
    '''
    Create a symlink.

    Args:
        path:
            The symlink path.

        target:
            The symlink target.
    '''
    path = pathlib.Path(path).resolve()
    target = str(target)
    if path == pathlib.Path(target).resolve():
        LOGGER.error('Cannot symlink a path to itself: %s', path)
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        cur_target = path.readlink()
    except FileNotFoundError:
        pass
    except OSError as err:
        # Not a symlink. Remove it.
        if err.errno == errno.EINVAL:
            if path.is_dir():
                LOGGER.info('Removing directory to create symlink: %s', path)
                shutil.rmtree(path)
            else:
                LOGGER.info('Removing file to create symlink: %s', path)
                path.unlink()
    else:
        if cur_target == target:
            return
        LOGGER.info('Removing old symlink: %s', path)
        path.unlink()
    path.symlink_to(target)


def _copy_dir(src, dst):
    '''
    Copy a directory. Destination files without corresponding source files are
    removed and then each file in the source is copied as necessary to the
    destination.

    Args:
        src:
            The source directory path.

        dst:
            The destination directory path.
    '''
    for root, dirs, fils in os.walk(dst):
        root = pathlib.Path(root)
        rel_root = root.relative_to(dst)
        src_root = src / rel_root

        # Filter and remove directories with no corresponding source.
        missing_dirs = [
            dname for dname in dirs
            if (src_root / dname).is_dir()
        ]
        for dname in missing_dirs:
            shutil.rmtree(root / dname)
        dirs[:] = [d for d in dirs if d not in missing_dirs]

        # Remove files with no corresponding source.
        for fname in fils:
            if not (src_root / fname).is_file():
                (root / fname).unlink()

    for root, _dirs, fils in os.walk(src):
        root = pathlib.Path(root)
        rel_root = root.relative_to(src)
        dst_root = dst / rel_root

        if fils:
            dst_root.mkdir(parents=True, exist_ok=True)

        for fname in fils:
            src_path = root / fname
            dst_path = dst_root / fname
            try:
                if filecmp.cmp(src_path, dst_path, shallow=False):
                    continue
                dst_path.unlink()
            except FileNotFoundError:
                pass
            shutil.copy2(src_path, dst_path)


def copy(src, dst):
    '''
    Copy the source to the destination. This compares existing files to avoid
    redundant copies.

    Args:
        src:
            The source path (either a file or directory).

        dst:
            The destination path.
    '''
    src = pathlib.Path(src).resolve()
    dst = pathlib.Path(dst).resolve()
    if not src.exists():
        LOGGER.warning('%s does not exist.', src)
        return
    if src == dst:
        LOGGER.warning('Cannot copy a path to itself: %s')
        return
    dst.parent.mkdir(parents=True, exist_ok=True)
    if dst.is_symlink():
        dst.unlink()

    if src.is_dir():
        if dst.is_dir():
            _copy_dir(src, dst)
            return
        try:
            dst.unlink()
        except FileNotFoundError:
            pass
        shutil.copytree(src, dst)
    else:
        try:
            if dst.is_dir():
                shutil.rmtree(dst)
            elif filecmp.cmp(src, dst, shallow=False):
                return
            else:
                dst.unlink()
        except FileNotFoundError:
            pass
        shutil.copy2(src, dst)
