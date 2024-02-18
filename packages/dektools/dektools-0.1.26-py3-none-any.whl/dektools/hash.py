import hashlib
from .file import sure_read


def hash_file(algorithm, path, block_size=4096):  # algorithm: hashlib.__always_supported
    def update(f):
        for chunk in iter(lambda: f.read(block_size), b""):
            hs.update(chunk)

    hs = getattr(hashlib, algorithm)()
    file = sure_read(path)
    if hasattr(file, 'read'):
        update(file)
    else:
        with open(file, "rb") as file:
            update(file)
    return hs.hexdigest()
