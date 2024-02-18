import os
import json
import functools
from pathlib import Path
from dektools.version import version_is_pure, version_sorted, version_digits
from dektools.shell import shell_output
from dektools.file import write_file
from dektools.download import download_http_exist
from dekartifacts.artifacts.staticfiles import StaticfilesArtifact

path_resources = Path(__file__).resolve().parent.parent.parent.parent / 'resources'


class PackageBase:
    artifact_cls = StaticfilesArtifact

    def __init__(self, meta, *args):
        self.meta = meta
        self.args = args
        self.artifact = self.artifact_cls()

    def pull(self, version):
        if self.is_remote:
            path_out = self.artifact.pull(self.location(version))
            return write_file(self.filename, t=True, m=path_out)
        else:
            return write_file(self.filename, t=True, c=self.location(version))

    def exist(self, version):
        return download_http_exist(self.location(version))

    @property
    def name(self):
        return self.meta['name']

    @property
    def ext(self):
        ext = self.meta.get('ext')
        if ext is None:
            return os.path.splitext(self.meta['release'])[-1]
        return ext

    @property
    def filename(self):
        return self.name + self.ext

    @property
    def is_remote(self):
        return not self.meta['release'].startswith('/')

    def location(self, version):
        result = self.meta['release'].format(version=version)
        if not self.is_remote:
            return str(path_resources) + result
        return result

    @property
    @functools.lru_cache(None)
    def versions(self):
        return version_sorted((version_digits(x) for x in self.versions_all if version_is_pure(x)), reverse=True)

    @property
    @functools.lru_cache(None)
    def versions_all(self):
        for key, value in (self.meta.get('versions') or {}).items():
            if key == 'github':
                content = shell_output(f"curl -sL https://api.github.com/repos/{value}/tags")
                return [x['name'] for x in json.loads(content)]
            elif key == 'value':
                return value
        return []


all_package = {}


def register_package(name):
    def wrapper(cls):
        all_package[name] = cls

    return wrapper
