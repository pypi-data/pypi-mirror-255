import json


class ToStrJSONEncoder(json.JSONEncoder):
    def default(self, o):
        return repr(o)


def obj2str(obj):
    return json.dumps(obj, indent=4, ensure_ascii=False, sort_keys=True, cls=ToStrJSONEncoder)


def pprint(obj, *args, **kwargs):
    print(obj2str(obj), *args, **kwargs)
