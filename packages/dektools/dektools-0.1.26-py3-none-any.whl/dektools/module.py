import types
from importlib import import_module


def obj2mq(x):
    return x.__module__, x.__qualname__.split('.')


def mq2obj(mq):
    m, q = mq
    cursor = import_module(m)
    for x in q:
        cursor = getattr(cursor, x)
    return cursor


def mq2str(mq):
    return '.'.join([mq[0], *mq[1]])


def get_module_attr(s):
    module, attrs = s, []
    while True:
        try:
            cursor = import_module(module)
            for attr in attrs:
                cursor = getattr(cursor, attr)
            return cursor
        except ModuleNotFoundError as e:
            if not module.startswith(e.name):
                raise e
            rs = module.rsplit('.', 1)
            if not module:
                raise e
            else:
                module = rs[0]
                attrs.insert(0, rs[1])


class ModuleProxy:
    def __init__(self, module=None):
        self.module = module

    def __getattr__(self, item):
        if hasattr(self.module, item):
            x = getattr(self.module, item)
            if isinstance(x, types.ModuleType):
                return self.__class__(x)
            else:
                return x
        else:
            return self.__class__(import_module(f'{self.module.__name__}.{item}' if self.module else item))
