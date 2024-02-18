import os
import re
import shutil
from igittigitt import IgnoreParser
from .path import normal_path
from .operation import read_lines


class FileHitChecker:
    def __init__(self, src_dir, ignore_file=None, rules=None):
        self.src_dir = normal_path(src_dir)
        self.parser = IgnoreParser()
        if ignore_file:
            self.parser.parse_rule_files(src_dir, ignore_file)
        if rules:
            for rule in rules:
                self.parser.add_rule(rule, src_dir)

    @property
    def shutil_ignore(self):
        return self.parser.shutil_ignore

    def is_hit(self, path):
        if not os.path.isabs(path):
            path = os.path.join(self.src_dir, path)
        return self.parser.match(path)

    def walk(self, func):
        def wrapper(path):
            for fn in os.listdir(path):
                fp = os.path.join(path, fn)
                func(fp, self.is_hit(fp), fp[len(self.src_dir) + 1:])
                if os.path.isdir(fp):
                    wrapper(fp)

        if os.path.exists(self.src_dir):
            wrapper(self.src_dir)

    def merge_dir(self, dest, ignores=None):
        def shutil_ignore(base_dir, file_names):
            result = set()
            for ignore in ignores:
                if base_dir.endswith(ignore):
                    result |= set(file_names)
                elif ignore in file_names:
                    result |= {ignore}
            return result | self.parser.shutil_ignore(base_dir, file_names)

        ignores = ignores or []
        if os.path.isdir(dest):
            shutil.rmtree(dest)
        shutil.copytree(self.src_dir, dest, ignore=shutil_ignore)


class ReHitChecker:
    @classmethod
    def form_file(cls, *filepaths):
        lines = []
        for filepath in filepaths:
            for x in read_lines(filepath, skip_empty=True):
                if not x.startswith('#'):
                    lines.append(x)
        return cls(lines)

    def __init__(self, lines):
        self.lines = lines

    def test(self, test):
        for item in self.lines:
            r = re.search(item, test)
            if r:
                return item
        return None

    def includes(self, array):
        for item in array:
            if self.test(item) is not None:
                yield item

    def excludes(self, array):
        for item in array:
            if self.test(item) is None:
                yield item
