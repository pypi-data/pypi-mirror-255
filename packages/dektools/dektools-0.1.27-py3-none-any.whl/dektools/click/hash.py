import os
import typer
from ..hash import hash_file

app = typer.Typer(add_completion=False)


@app.callback(invoke_without_command=True)
def get_hash(path: str = '.', deep: bool = False):
    path = os.path.normpath(os.path.abspath(path))
    if os.path.isdir(path):
        for fn in os.listdir(path):
            pfn = os.path.join(path, fn)
            if deep or os.path.isfile(pfn):
                get_hash(pfn)
    else:
        print(os.path.basename(path) + ' :')
        print(f'   sha256: {hash_file("sha256", path)}')
        print(f'   md5: {hash_file("md5", path)}')
        print()
