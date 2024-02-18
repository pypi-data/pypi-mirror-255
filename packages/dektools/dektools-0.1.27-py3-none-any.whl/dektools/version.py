import string


def version_to_tuple(version, sep='.'):
    array = []
    for x in version.split(sep):
        try:
            x = int(x)
        except ValueError:
            pass
        array.append(x)
    return tuple(array)


def version_digits(version):
    includes = string.digits + '.'
    result = ''
    for x in version:
        if x in includes:
            result += x
    return result


def version_is_pure(version):
    return '-' not in version


def version_sorted(versions, reverse=False):
    keys = {x: version_to_tuple(x) for x in versions}
    return sorted(keys, key=lambda x: keys[x], reverse=reverse)
