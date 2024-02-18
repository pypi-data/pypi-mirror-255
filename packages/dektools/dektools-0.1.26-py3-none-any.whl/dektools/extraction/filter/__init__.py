import json
import jmespath
from functools import partial, reduce
from ..value import ProxyValue
from .utils import Method, AttrProxy
from ...module import ModuleProxy
from ...hash import hash_file
from ...re import re2format


class FilterSet:
    custom_filters = {}

    def __init__(self):
        self.context = default_filters | self.custom_filters

    def register(self, key, func):
        if isinstance(func, str):
            func = eval(func, self.context)
        self.context[key] = func
        return func

    def update(self, context):
        for k, v in context.items():
            self.register(k, v)

    def eval(self, context, value, expressions):
        cursor = value
        if cursor is ProxyValue.NOT_EXIST:
            return cursor
        if context:
            context = self.context | context
        else:
            context = self.context
        for expression in expressions:
            func = eval(expression, context)
            cursor = func(cursor)
            if cursor is ProxyValue.NOT_EXIST:
                return cursor
        return cursor

    @staticmethod
    def in_set(d):
        return AttrObject(d)


class AttrObject:
    def __init__(self, attrs):
        self.attrs = attrs

    def __getattr__(self, item):
        return self.attrs[item]


def __list_at(default, index):
    def wrapper(x):
        if x:
            return x[index]
        else:
            return default

    return wrapper


def __last(default=None):
    return __list_at(default, -1)


def __first(default=None):
    return __list_at(default, 0)


def __printf(trans=None):
    def inner(value):
        val = value
        if trans:
            val = trans(value)
        print(val)
        return value

    return inner


def __split(s, sep=" ", strip=True, none=False):
    result = []
    for x in s.split(sep):
        if strip:
            x = x.strip()
        if none or x:
            result.append(x)
    return result


def __bytes(x):
    if isinstance(x, str):
        return x.encode('utf-8')
    elif isinstance(x, bytes):
        return x
    else:
        return __bytes(json.dumps(x, sort_keys=True))


default_filters = {
    'c': lambda x: x(),
    'me': lambda x: x,
    'mp': ModuleProxy(),
    'print': lambda x: print(x) or x,
    'prints': lambda x: lambda value: print(value, x) or value,
    'printf': __printf,
    'p': partial,
    'h': hash_file,
    'bs': __bytes,
    'reduce': reduce,
    'first': __first,
    'last': __last,
    'none': lambda x: x or None,
    'orv': lambda x=None: lambda value: value or x,
    'split': lambda sep=" ", strip=True, none=False: lambda value: __split(value, sep, strip, none),
    's': lambda x: str(x),
    'm': Method(),
    'a': AttrProxy(),
    're': lambda pattern: (lambda string: re2format(pattern, string)[1]),
    'at': lambda index: (lambda array: array[index]),
    'sl': lambda begin=None, end=None, step=None: (lambda array: array[slice(begin, end, step)]),
    'sumd': lambda x: reduce(lambda y, z: y | z, x, {}),
    'jp': lambda x: (lambda y: jmespath.compile(x).search(y))
}
