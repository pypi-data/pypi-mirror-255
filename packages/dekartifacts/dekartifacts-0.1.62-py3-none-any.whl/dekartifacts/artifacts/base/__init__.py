import os
import functools
import shutil
import json
import hashlib
import string
from dektools.common import classproperty
from dektools.file import read_text, write_file
from dektools.str import decimal_to_short_str

docker_image_tag_max_length = 128


class ArtifactBase:
    typed = ''
    marker_registry = 'registry'

    cli_list = []

    def __init__(self, environ=None):
        self.environ = environ or os.environ

    def prepare(self):
        pass

    @classproperty
    @functools.lru_cache(None)
    def path_work(self):
        return os.path.join(os.path.expanduser('~'), f'.dekartifacts', self.typed)

    @classproperty
    @functools.lru_cache(None)
    def cli(self):
        for cli in self.cli_list:
            if shutil.which(cli):
                return cli

    @staticmethod
    def normalize_docker_tag(url, tag):
        if len(tag) > docker_image_tag_max_length:
            sha = decimal_to_short_str(
                int(hashlib.sha256(url.encode('utf-8')).hexdigest(), 16),
                string.digits + string.ascii_letters
            )
            sep = '-'
            tag = tag[len(tag) - docker_image_tag_max_length + len(sha) + len(sep):] + sep + sha
        return tag

    @classmethod
    def url_to_docker_tag(cls, url):
        return None

    def query_env_map(self, marker, is_end):
        result = {}
        for key in self.environ.keys():
            if is_end:
                if key.endswith(marker):
                    result[key[:-len(marker)]] = self.environ[key]
            else:
                if key.startswith(marker):
                    result[key[len(marker):]] = self.environ[key]
        return result

    def list_env_registries(self):
        return sorted(self.query_env_map(f"__{self.typed}_{self.marker_registry}", True))

    def login_all_env(self):
        for registry in self.list_env_registries():
            self.login_env(registry)

    def login_env(self, registry=None):
        registry = registry or self.environ.get(f"{self.typed}_default_login_registry", "")
        kwargs = self.query_env_map(f"{registry}__{self.typed}_", False)
        self.login(**kwargs)

    def login(self, **kwargs):
        raise NotImplementedError

    @property
    @functools.lru_cache(None)
    def path_objects(self):
        return os.path.join(self.path_work, 'objects')

    def path_keep_dir(self, path, path_object):
        return os.path.join(path, path_object[len(self.path_objects) + 1:])

    @property
    @functools.lru_cache(None)
    def path_auth(self):
        return os.path.join(self.path_work, 'auth.json')

    def get_auth(self, registry):
        if os.path.exists(self.path_auth):
            auth = json.loads(read_text(self.path_auth))
            return auth.get(registry)

    def login_auth(self, registry='', **kwargs):
        auth = {}
        if os.path.exists(self.path_auth):
            auth = json.loads(read_text(self.path_auth))
        auth[registry] = kwargs
        write_file(self.path_auth, s=json.dumps(auth))
