import os


def join_path(*args):
    return os.path.normpath(os.path.join(*(args[0], *(x.strip('\\/') for x in args[1:]))))


def normal_path(path):
    return os.path.normpath(os.path.abspath(path))
