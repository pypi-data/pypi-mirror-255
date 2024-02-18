import string
import codecs
from collections.abc import Mapping


class FormatDict(Mapping):
    empty = type('empty', (), {})

    def __init__(self, kwargs, missing=None):
        self.kwargs = kwargs
        self.missing = missing

    @staticmethod
    def __missing(key):
        return f'{{{key}}}'

    def __getitem__(self, item):
        value = self.kwargs.get(item, self.empty)
        if value is self.empty:
            return (self.missing or self.__missing)(item)
        else:
            return value

    def __iter__(self):
        return iter(self.kwargs)

    def __len__(self):
        return len(self.kwargs)


formatter = string.Formatter()


def str_format_partial(s, kwargs, missing=None):
    return formatter.vformat(s, (), FormatDict(kwargs, missing))


def str_escaped(s):
    return codecs.getdecoder("unicode_escape")(s.encode('utf-8'))[0]


def str_custom_escaped_split(s, delim, escaped='\\'):
    ret = []
    current = []
    itr = iter(s)
    for ch in itr:
        if ch == escaped:
            try:
                # skip the next character; it has been escaped!
                current.append(escaped)
                current.append(next(itr))
            except StopIteration:
                pass
        elif ch == delim:
            # split! (add current to the list and reset it)
            ret.append(''.join(current))
            current = []
        else:
            current.append(ch)
    ret.append(''.join(current))
    return ret


def str_custom_escaped(s, mapping=None, escaped='\\'):
    mapping = {} if mapping is None else mapping
    r = ""
    cursor = 0
    length = len(s)
    while cursor < length:
        c = s[cursor]
        if c == escaped:
            cursor += 1
            c = s[cursor]
            r += mapping.get(c, c)
        else:
            r += c
        cursor += 1
    return r


def str_align_number(index, total):
    lt = len(str(total))
    li = len(str(index))
    return max(0, lt - li) * '0' + str(index)


_var_marker_ld = set(string.ascii_lowercase + string.digits)
_var_marker_u = set(string.ascii_uppercase)
_var_marker_d = set(string.digits)


def to_var_format(*str_list):
    r = []
    for x in str_list:
        s = ""
        for i in range(len(x)):
            if x[i] in _var_marker_ld:
                s += x[i]
            else:
                if s:
                    r.append(s)
                    s = ""
                if x[i] in _var_marker_u:
                    s += x[i].lower()
        if s:
            r.append(s)
    if r and r[0][0] in _var_marker_d:
        r[0] = '_' + r[0]
    return r


def to_var_format_camel(r):
    return ''.join(x if i == 0 else x.capitalize() for i, x in enumerate(r))


def to_var_format_pascal(r):
    return ''.join(x.capitalize() for x in r)


def to_var_format_hungarian(r):
    return '_'.join(r)


def to_var_format_py(r):
    return ''.join(r)


def str_special_escape(s, escape='\\'):
    r = ""
    escaping = False
    for x in s:
        if not escaping and x == escape:
            escaping = True
        else:
            r += x
            escaping = False
    return r


def str_format_var(s, begin='{', end='}', escape='\\'):
    fmt = ['']
    args = []
    arg = None
    escaping = False
    for x in s:
        if not escaping and x == escape:
            escaping = True
        else:
            if escaping:
                if arg is None:
                    fmt[-1] += x
                else:
                    arg += x
            else:
                if x == begin:
                    if arg is None:
                        arg = ""
                    else:
                        arg += x
                else:
                    if x == end:
                        if arg is None:
                            fmt[-1] += x
                        else:
                            args.append(arg)
                            arg = None
                            fmt.append('')
                    else:
                        if arg is None:
                            fmt[-1] += x
                        else:
                            arg += x
            escaping = False
    return lambda xx, ma=None, mi=None: _str_format_var_final(fmt, xx, ma, mi), args


def _str_format_var_final(fmt, args, mapping=None, missing=None):
    s = ""
    cursor = 0
    while True:
        s += fmt[cursor]
        if cursor == len(fmt) - 1:
            break
        arg = args[cursor]
        if mapping and arg in mapping:
            arg = mapping[arg]
        elif missing:
            arg = missing(arg)
        s += str(arg)
        cursor += 1
    return s


def decimal_to_short_str(num, sequence):
    lst = []
    sequence_length = len(sequence)
    num = num - 1
    if num > sequence_length - 1:
        while True:
            d = int(num / sequence_length)
            remainder = num % sequence_length
            if d <= sequence_length - 1:
                lst.insert(0, sequence[remainder])
                lst.insert(0, sequence[d - 1])
                break
            else:
                lst.insert(0, sequence[remainder])
                num = d - 1
    else:
        lst.append(sequence[num])
    return "".join(lst)


if __name__ == '__main__':
    fx, a = str_format_var('aaa{bbb}ccc{ddd}')
    print(fx([x.upper() for x in a]))

    import hashlib
    print(decimal_to_short_str(int(hashlib.md5('test'.encode("ascii")).hexdigest(), 16), string.digits + string.ascii_letters + '_'))
