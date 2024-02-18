"""
Path operations for heist
"""
import os
import sys
from pathlib import Path
from pathlib import PurePosixPath
from pathlib import PureWindowsPath


def path_convert(hub, target_system, entry_path, ext_path):
    """
    Convert local path to target (remote) path.

    Due to pathlib.Path docstring indicating that a PureWindowsPath and
    PosixPath can not be created on their counterpart's system, we must
    make our own conversion.
    :param target_system:
    :param entry_path:
    :param list options:
    :return:
    """
    path_obj = None
    if "win" in target_system:
        path_obj = PureWindowsPath(entry_path)
        for option in ext_path:
            path_obj = path_obj.joinpath(option)
    elif "linux" in target_system or "darwin" in target_system:
        path_obj = PurePosixPath(entry_path)
        for option in ext_path:
            path_obj = path_obj.joinpath(option)
    hub.log.debug(f"Converted path for {target_system} for {entry_path}")
    return path_obj


def _realpath_darwin(path):
    base = ""
    for part in path.parts[1:]:
        if base != "":
            if os.path.islink(os.path.sep.join([base, part])):
                base = os.readlink(os.path.sep.join([base, part]))
            else:
                base = os.path.abspath(os.path.sep.join([base, part]))
        else:
            base = os.path.abspath(os.path.sep.join([base, part]))
    return base


def _realpath_windows(path):
    base = ""
    if not isinstance(path, Path):
        path = Path(path)
    for part in path.parts:
        if base != "":
            try:
                part = os.readlink(os.path.sep.join([base, part]))
                base = os.path.abspath(part)
            except OSError:
                base = os.path.abspath(os.path.sep.join([base, part]))
        else:
            base = part
    return base


def _realpath(path):
    """
    Cross platform realpath method. On Windows when python 3, this method
    uses the os.readlink method to resolve any filesystem links.
    All other platforms and version use ``os.path.realpath``.
    """
    if sys.platform == "darwin":
        return _realpath_darwin(path)
    elif sys.platform == "win32":
        return _realpath_windows(path)
    return os.path.realpath(path)


def clean_path(hub, root, path, subdir=False):
    """
    Return a clean path that has been validated.
    Using os.path here instead of pathlib, because
    the api's functionalities are not entirely the
    same yet.
    """
    real_root = _realpath(root)
    path = os.path.expandvars(path)
    if not os.path.isabs(real_root):
        return ""
    if not os.path.isabs(path):
        path = os.path.join(root, path)
    path = os.path.normpath(path)
    real_path = _realpath(path)
    if path.startswith(real_root):
        return os.path.join(root, path)
    if subdir:
        if real_path.startswith(real_root):
            return real_path
    else:
        if os.path.dirname(real_path) == os.path.normpath(real_root):
            return real_path
    return ""
