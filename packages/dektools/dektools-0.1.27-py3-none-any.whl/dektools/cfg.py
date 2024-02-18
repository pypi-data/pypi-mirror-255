import os
import json
from .file import write_file, read_text, remove_path
from .dict import assign


class ObjectCfg:
    def __init__(self, name):
        self.name = name

    @property
    def path(self):
        return os.path.join(os.path.expanduser('~'), f'.{self.name}.json')

    def set(self, data=None):
        if not data:
            remove_path(self.path)
        else:
            write_file(self.path, json.dumps(data))

    def get(self):
        return json.loads(read_text(self.path, default='{}'))

    def update(self, data):
        data = assign(self.get(), data)
        self.set(data)
        return data
