from .dict import is_list


def obj_path_value(obj, path, ignore=True, mode='ia'):
    keys = [x for x in (path or '').split(".")]
    cursor = obj
    for key in keys:
        if 'i' in mode:
            try:
                if is_list(cursor):
                    key = int(key)
                cursor = cursor[key]
                continue
            except (IndexError, KeyError, TypeError, ValueError):
                pass
        if 'a' in mode:
            try:
                cursor = getattr(cursor, key)
                continue
            except AttributeError:
                pass
        if not ignore:
            raise ValueError(f'Cant get value of {obj} , {path} , {mode} , {key}')
    return cursor


class AttrsKwargs:
    def __init__(self, **kwargs):
        self._kwargs = kwargs

    def __getattr__(self, item):
        return self[item]

    def __getitem__(self, item):
        return self._kwargs[item]


class AttrsKwargsAny(AttrsKwargs):
    _any = None

    def __getitem__(self, item):
        return self._kwargs.get(item, self._any)


class AttrsDict:
    def __init__(self, kwargs, final=None):
        self._kwargs = kwargs
        self._final = final

    def __getattr__(self, item):
        return self[item]

    def __getitem__(self, item):
        value = self._get_item_raw(item)
        return self._final(value) if self._final else value

    def _get_item_raw(self, item):
        return self._kwargs[item]


class AttrsDictAny(AttrsDict):
    _any = None

    def _get_item_raw(self, item):
        return self._kwargs.get(item, self._any)


class DictObj(object):
    pass


def dict_to_obj(data, cls=DictObj):
    def walk(node):
        if isinstance(node, dict):
            obj = cls()
            for k, v in node.items():
                setattr(obj, k, walk(v))
            return obj
        else:
            return node

    return walk(data)
