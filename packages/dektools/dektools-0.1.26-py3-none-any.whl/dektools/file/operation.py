import os
import tempfile
import shutil
import codecs
import filecmp
from io import BytesIO

DEFAULT_VALUE = type('default_value', (), {})


def write_file(
        filepath,
        s=None, b=None, sb=None,
        m=None, mi=None,
        c=None, ci=None,
        ma=None, mo=None,
        t=False,
        encoding='utf-8'):
    if filepath and not t and mi is None and ci is None:
        if os.path.exists(filepath):
            remove_path(filepath)
        sure_dir(os.path.dirname(filepath))
    if t:
        pt = tempfile.mkdtemp()
        if s is not None or b is not None or sb is not None:
            fp = os.path.join(pt, filepath or '__tempfile__')
            write_file(fp, s=s, b=b, sb=sb)
        else:
            fp = os.path.join(pt, filepath or os.path.basename(m or mi or c or ci or ma or mo))
            write_file(fp, m=m, mi=mi, c=c, ci=ci, ma=ma, mo=mo)
        return fp
    elif s is not None:
        write_text(filepath, s, encoding)
    elif b is not None:
        with open(filepath, 'wb') as f:
            f.write(b)
    elif sb is not None:
        if isinstance(sb, str):
            write_file(filepath, s=sb)
        else:
            write_file(filepath, b=sb)
    elif c is not None:
        filepath_temp = str(filepath) + '.__tempfile__'
        if os.path.exists(filepath_temp):
            os.remove(filepath_temp)
        if os.path.isdir(c):
            shutil.copytree(c, filepath_temp)
        else:
            shutil.copyfile(c, filepath_temp)
        shutil.move(filepath_temp, filepath)
    elif ci is not None:
        if os.path.exists(ci):
            write_file(filepath, c=ci)
    elif m is not None:
        shutil.move(m, filepath)
    elif mi is not None:
        if os.path.exists(mi):
            write_file(filepath, m=mi)
    elif ma is not None:
        sure_dir(filepath)
        merge_assign(ma, filepath)
    elif mo is not None:
        sure_dir(filepath)
        merge_overwrite(mo, filepath)
    else:
        raise TypeError('s, b, c, ci, m, mi is all empty')


def read_file(filepath, default=DEFAULT_VALUE):
    if os.path.isfile(filepath):
        with open(filepath, 'rb') as f:
            return f.read()
    else:
        if default is not DEFAULT_VALUE:
            return default
        else:
            raise FileNotFoundError(filepath)


def read_text(filepath, default=DEFAULT_VALUE, encoding='utf-8'):
    if filepath and os.path.isfile(filepath):
        with codecs.open(filepath, encoding=encoding) as f:
            return f.read()
    else:
        if default is not DEFAULT_VALUE:
            return default
        else:
            raise FileNotFoundError(filepath)


def write_text(filepath, content, encoding='utf-8'):
    with codecs.open(filepath, 'w', encoding=encoding) as f:
        return f.write(content)


def read_lines(filepath, skip_empty=False, encoding='utf-8', default=DEFAULT_VALUE):
    for line in read_text(filepath, encoding=encoding, default=default).splitlines():
        line = line.strip()
        if skip_empty and not line:
            continue
        yield line


def remove_path(path, ignore=False):
    try:
        if os.path.isdir(path):
            shutil.rmtree(path)
        elif os.path.isfile(path):
            os.remove(path)
        return True
    except PermissionError as e:
        if not ignore:
            raise e from e
        return False


def clear_dir(path, ignore=False):
    for file in os.listdir(path):
        remove_path(os.path.join(path, file), ignore)


def merge_dir(dest, src):
    for fn in os.listdir(src):
        write_file(os.path.join(dest, fn), ci=os.path.join(src, fn))


def copy_path(src, dest):
    remove_path(dest)
    if os.path.isdir(src):
        shutil.copytree(src, dest)
    elif os.path.isfile(src):
        shutil.copyfile(src, dest)


def copy_file_stable(src, dest, block_size=4096):
    with open(src, 'rb') as f:
        sure_dir(os.path.dirname(dest))
        with open(dest, 'wb') as f2:
            for chunk in iter(lambda: f.read(block_size), b""):
                f2.write(chunk)


def sure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)


def sure_read(path_or_content):
    if isinstance(path_or_content, bytes):
        return BytesIO(path_or_content)
    else:
        return path_or_content


def content_cmp(a, b):
    return filecmp.cmp(a, b, False)


def temp_path(path):
    path_out = os.path.join(tempfile.mkdtemp(prefix='temp_path'), 'temp')
    write_file(path_out, ci=path)
    return path_out


def list_relative_path(src):
    def walk(p):
        for fn in os.listdir(p):
            fp = os.path.join(p, fn)
            if os.path.isfile(fp):
                result[fp[len(str(src)) + 1:]] = fp
            elif os.path.isdir(fp):
                walk(fp)

    result = {}
    if os.path.isdir(src):
        walk(src)
    return result


def list_dir(path):
    if os.path.isdir(path):
        for item in os.listdir(path):
            yield os.path.join(path, item)


def merge_assign(dest, src):
    src_info = list_relative_path(src)
    for rp, fp in src_info.items():
        copy_file_stable(fp, os.path.join(dest, rp))


def merge_overwrite(dest, src):
    src_info = list_relative_path(src)
    for rp, fp in src_info.items():
        copy_file_stable(fp, os.path.join(dest, rp))
    dest_info = list_relative_path(dest)
    for rp, fp in dest_info.items():
        if rp not in src_info:
            remove_path(fp)
