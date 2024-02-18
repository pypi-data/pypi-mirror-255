from collections import OrderedDict
from urllib.parse import urlparse, urlunparse, parse_qsl, urlencode


class Url:
    @classmethod
    def from_str(cls, url):
        pt = urlparse(url)
        kwargs = dict(
            scheme=pt.scheme,
            netloc=pt.netloc,
            path=pt.path,
            query=dict(parse_qsl(pt.query, True)),
            fragment=pt.fragment
        )
        return cls(**kwargs)

    @classmethod
    def is_abs_url(cls, url):
        return bool(cls.from_str(url).scheme)

    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def __getattr__(self, item):
        return self.kwargs[item]

    def format(self, **kwargs):
        kwargs = self.kwargs | kwargs
        return urlunparse((
            kwargs.get('scheme'),
            kwargs.get('netloc'),
            kwargs.get('path') or '',
            '',
            urlencode(kwargs.get('query') or {}),
            kwargs.get('fragment')
        ))

    def sort_query(self):
        query = self.kwargs.get('query')
        if query is not None:
            self.kwargs['query'] = OrderedDict((k, query[k]) for k in sorted(query))
        return self

    @property
    def value(self):
        return self.format()

    @property
    def home(self):
        return self.format(
            path=None,
            query=None,
            fragment=None
        )


def get_auth_url(url, username, password=None):
    a, b = url.split('//', 1)
    pw = ''
    if password:
        pw = f":{password}"
    return f"{a}//{username}{pw}@{b}"
