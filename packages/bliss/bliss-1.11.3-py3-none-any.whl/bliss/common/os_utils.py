# -*- coding: utf-8 -*-
#
# This file is part of the bliss project
#
# Copyright (c) 2015-2023 Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.

import os
import pathlib
from numbers import Number
from typing import Optional
from bliss.common.query_pool import NonCooperativeQueryPool
from bliss import current_session


def find_existing(path):
    """Returns `path` or one of its parent directories.

    :param str path:
    :returns str or None:
    """
    path = os.path.normpath(path)
    while not os.path.exists(path):
        previous = path
        path = os.path.dirname(path)
        if path == previous:
            break
    if not os.path.exists(path):
        return
    return path


def has_required_disk_space(
    path: str,
    required_disk_space: Number,
    query_pool: Optional[NonCooperativeQueryPool] = None,
) -> bool:
    """
    :param path: may not exist yet
    :param required_disk_space: is MB
    :param query_pool:
    :returns: also returns `True` when no path was found or
              the call did not finish within the query pool's
              timeout.
    """
    if required_disk_space <= 0:
        return True
    path = find_existing(path)
    if not path:
        return True
    stat = statvfs(path, query_pool=query_pool)
    if stat is None:
        return True
    free_space = stat.f_frsize * stat.f_bavail / 1024**2
    return free_space >= required_disk_space


def statvfs(path, query_pool: Optional[NonCooperativeQueryPool] = None):
    """os.statvfs could take several seconds on NFS"""
    if query_pool is None:
        return os.statvfs(path)
    assert isinstance(query_pool, NonCooperativeQueryPool)
    return query_pool.execute(os.statvfs, args=(path,), default=None)


def has_write_permissions(path):
    """
    :param str path: may not exist yet
    :returns bool:
    """
    if os.path.exists(path):
        return os.access(path, os.W_OK)
    else:
        # Check whether we can create the path
        path = os.path.dirname(os.path.normpath(path))
        path = find_existing(path)
        if path and os.path.isdir(path):
            return os.access(path, os.W_OK)
        else:
            return False


def makedirs(path: str, exist_ok: bool = True, **kwargs) -> None:
    """When possible use the Bliss session's writer object to
    create the directory. Otherwise use `os.makedirs` but beware
    the current process user will be the owner.
    """
    if current_session and exist_ok and not kwargs:
        if current_session.scan_saving.create_path(path):
            return
        # We are here because the writer is the null writer
        # or the writer has no access to the directory we
        # are trying to create.
    os.makedirs(path, exist_ok=exist_ok, **kwargs)


def is_subdir(child, parent, strict: bool = False) -> bool:
    parent = pathlib.Path(parent).resolve()
    child = pathlib.Path(child).resolve()
    if strict:
        return parent in child.parents
    return child == parent or parent in child.parents
