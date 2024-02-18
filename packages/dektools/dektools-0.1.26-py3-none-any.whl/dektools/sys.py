import os
import sys
import subprocess
from sysconfig import get_paths
from importlib import metadata, import_module


def path_sys_exe():  # Used by system python Scripts bin
    return subprocess.getoutput('python -c "import sys;print(sys.executable)"')


def sys_paths_relative(path, raw=False):  # sys_paths_relative('./.venv')
    if not raw:
        path = os.path.normpath(os.path.abspath(path))
    result = {}
    paths = get_paths()
    for k, p in paths.items():
        if p.startswith(sys.prefix):
            result[k] = path + p[len(sys.prefix):]
        else:
            result[k] = p
    return result


def sure_command(cmd):
    ret = os.system(cmd)
    if ret:
        raise ChildProcessError((ret, cmd))


def get_console_scripts_exe(name, cmd=None):
    eps = metadata.entry_points(group='console_scripts')
    try:
        ep = eps[name]
    except KeyError:
        return None
    try:
        filepath = import_module(ep.module.split('.')[0]).__file__
        path_pkg = os.path.dirname(filepath)
        if os.path.splitext(os.path.basename(filepath))[0] == '__init__':
            path_pkg = os.path.dirname(path_pkg)
    except (ImportError, ModuleNotFoundError):
        return None
    cmd = cmd or name
    for file in ep.dist.files:
        fp = os.path.abspath(os.path.join(path_pkg, os.path.sep.join(file.parts)))
        if os.path.isfile(fp) and os.path.splitext(os.path.basename(fp))[0].lower() == cmd.lower():
            return fp
    return None
