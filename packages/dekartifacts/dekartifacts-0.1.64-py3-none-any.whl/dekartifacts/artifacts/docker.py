import json
import os
import uuid
from dektools.shell import shell_wrapper, shell_with_input, shell_result, shell_exitcode, shell_output
from dektools.file import read_text, write_file, read_lines, sure_dir
from .base import ArtifactBase


class DockerArtifact(ArtifactBase):
    typed = 'docker'
    cli_list = ['docker', 'nerdctl', 'podman']

    image_tag_max_length = 128
    registry_standard = 'docker.io'

    @classmethod
    def login(cls, registry='', username='', password=''):
        print(F"Login to {registry} {username[0]}***{username[-1]}")
        ret, _, err = shell_with_input(f'{cls.cli} login {registry} -u {username} --password-stdin', password)
        if ret:
            for mark in [b'net/http: TLS handshake timeout']:
                if mark in err:
                    shell_wrapper('sleep 1')
                    print(err, flush=True)
                    cls.login(registry, username, password)
                    break
            else:
                raise ChildProcessError(err)

    @classmethod
    def pull(cls, image, ga='', la=''):
        if not cls.exist(image):
            ret, err = shell_result(f'{cls.cli} {ga} pull {la} {image}')
            if ret:
                for mark in ['net/http: TLS handshake timeout']:
                    if mark in err:
                        shell_wrapper('sleep 1')
                        return cls.pull(image)
                else:
                    raise ChildProcessError(err)
        return image

    @classmethod
    def push(cls, image, ga='', la=''):
        ret, err = shell_result(f'{cls.cli} {ga} push {la} {image}')
        if ret:
            for mark in ['net/http:', 'dial tcp:']:
                if mark in err:
                    shell_wrapper('sleep 1')
                    print(err, flush=True)
                    cls.push(image)
                    break
            else:
                raise ChildProcessError(err)

    @classmethod
    def remove(cls, image):
        shell_wrapper(f'{cls.cli} rmi {image}')

    @classmethod
    def tag(cls, image, new_image):
        shell_wrapper(f'{cls.cli} tag {image} {new_image}')

    @classmethod
    def build(cls, image, path, args=None):
        result = ''
        if args:
            for k, v in args.items():
                result += f' --build-arg {k}={v}'
        shell_wrapper(f'echo "{cls.cli} building..." && {cls.cli} build -t {image} {result} {path}')

    @classmethod
    def cp(cls, image, *args):
        name = f"tmp-cp-{uuid.uuid4().hex}"
        shell_wrapper(f"{cls.cli} create --name={name} {image}")
        for src, dest in zip(args[::2], args[1::2]):
            shell_wrapper(f"{cls.cli} cp {name}:{src} {dest}")
        shell_wrapper(f"{cls.cli} rm {name}")

    @classmethod
    def status(cls, id_or_name):
        ret, result = shell_result(f"{cls.cli} inspect {id_or_name}")
        if ret:
            return None
        return json.loads(result)[0]

    @classmethod
    def images(cls):
        images = shell_output(f"{cls.cli} images -a --format '{{{{ .Repository }}}}:{{{{ .Tag }}}}'")
        return read_lines(None, default=images)

    @classmethod
    def exports(cls, images, path):
        sure_dir(path)
        for image in images:
            path_file = os.path.join(path, f'{cls.url_to_docker_tag(image)}.tar')
            if not os.path.isfile(path_file):
                shell_wrapper(f"{cls.cli} save -o {path_file} {image}")

    @classmethod
    def imports(cls, path, skip=True):
        def load(p):
            if skip and os.path.splitext(os.path.basename(p))[0] in images:
                return
            shell_wrapper(f"{cls.cli} load -i {p}")

        if skip:
            images = {cls.url_to_docker_tag(x) for x in cls.images()}
        else:
            images = set()

        if os.path.isdir(path):
            for file in os.listdir(path):
                load(os.path.join(path, file))
        else:
            load(path)

    @classmethod
    def exist(cls, image):
        try:
            shell_wrapper(f'{cls.cli} inspect {image} > /dev/null 2>&1')
            return True
        except ChildProcessError:
            return False

    @staticmethod
    def remote_exist(image):
        return shell_exitcode(f'skopeo --override-os linux inspect docker://{image}') == 0

    @staticmethod
    def remote_tags(image):
        rc, result = shell_result(f"skopeo --override-os linux list-tags docker://{image}")
        if rc:
            return set()
        return set(json.loads(result)['Tags'])

    @staticmethod
    def format_url(url):
        sha256 = '@sha256'
        repo, tag = url.split(':', 1)
        if repo.endswith(sha256):
            repo = repo[:-len(sha256)]
        return ':'.join([repo.replace('.', '-').replace('/', '-'), tag])

    @classmethod
    def full_url(cls, full_url):
        if ':' not in full_url:
            full_url = f'{full_url}:latest'
        r = full_url.split('/')
        if len(r) <= 1 or '.' not in r[0]:
            return f'{cls.registry_standard}/{full_url}'
        return full_url

    @classmethod
    def is_in_standard(cls, url):
        return cls.full_url(url).startswith(cls.registry_standard)

    @classmethod
    def url_to_docker_tag(cls, url):
        url = cls.full_url(url)
        rr, tag = url.rsplit(':', 1)
        tag_new = rr.split('/', 1)[-1].replace('/', '-') + '-' + tag
        return cls.normalize_docker_tag(url, tag_new)

    @classmethod
    def entry(cls, url):
        image_full_url = cls.full_url(url)
        registry, repository_tag = image_full_url.split('/', 1)
        repository, tag = repository_tag.split(':')
        return dict(
            image=image_full_url,
            registry=registry,
            repository=repository,
            rr=f'{registry}/{repository}',
            tag=tag
        )

    @classmethod
    def build_fast(cls, path, step, images, args=None, push=True):
        def _do_prepare(x):
            write_file(os.path.join(path, 'Dockerfile'), s=x)

        def _do_build(target):
            shell_wrapper(f'{cls.cli} build -t {target} {build_args} {path}')

        def _do_build_build():
            for i, c in enumerate(content_build):
                _do_prepare('\n'.join([content_args, c]))
                _do_build(f'build:cache--{i}')

        def _do_build_result():
            last_image = None
            has_updated = False
            for image_name in images:
                contents = content_result[image_name]
                write_file(os.path.join(path, '.context'), ci=os.path.join(path, image_name))
                for i, c in enumerate(contents):
                    is_last = i == len(contents) - 1
                    build_from = [f'FROM build:cache--{i} AS build{i}' for i in range(len(content_build))]
                    if is_last:
                        current_image = images[image_name]
                    elif i == 0:
                        current_image = f'{step}-{image_name}--base-{result_little_version[image_name].get(i, 0)}'
                    else:
                        current_image = f'{step}-{image_name}--step-{i}-{result_little_version[image_name].get(i, 0)}'
                    self_from = ''
                    if last_image:
                        self_from = f'FROM {last_image}'
                    last_image = current_image
                    if is_last or has_updated or not cls.remote_exist(current_image):
                        _do_prepare('\n'.join([content_args, *build_from, self_from, c]))
                        _do_build(current_image)
                        if push:
                            cls.push(current_image)
                        has_updated = True

        content_args = ''
        content_result = {}
        content_build_detail = {}
        result_little_version = {}
        for file in os.listdir(path):
            pa = os.path.join(path, file)
            if not file.startswith('.') and os.path.isdir(pa):
                content_result_detail = {}
                for file2 in os.listdir(pa):
                    pa2 = os.path.join(pa, file2)
                    if not file2.startswith('.') and os.path.isfile(pa2):
                        content = read_text(pa2)
                        if file2.endswith('.Dockerfile'):
                            name = file2.rsplit('.', 1)[0]
                            content_result_detail[int(name)] = content
                content_result[file] = [content_result_detail[i] for i in sorted(content_result_detail)]
                result_little_version[file] = {
                    i: int(x) for i, x in
                    enumerate(read_lines(os.path.join(pa, 'update'), skip_empty=True, default=''))
                }
            elif file.endswith('.Dockerfile'):
                name = '.'.join(file.split('.')[1:-1])
                content = read_text(pa)
                if file.startswith('args.'):
                    content_args = content
                elif file.startswith('build.'):
                    content_build_detail[int(name)] = content
        content_build = [content_build_detail[i] for i in sorted(content_build_detail)]

        build_args = ''
        if args:
            if isinstance(args, str):
                build_args = args
            else:
                for k, v in args.items():
                    build_args += f' --build-arg {k}={v}'

        _do_build_build()
        _do_build_result()
