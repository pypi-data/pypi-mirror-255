import typer
from dektools.file import read_lines
from ..artifacts.docker import DockerArtifact

app = typer.Typer(add_completion=False)


@app.command()
def exports(path, items=''):
    if items:
        images = read_lines(items, skip_empty=True)
    else:
        images = DockerArtifact.images()
    DockerArtifact.exports(images, path)


@app.command()
def imports(path, skip=True):
    DockerArtifact.imports(path, skip)


@app.command()
def migrate(path, images, registry):
    DockerArtifact.imports(path)
    for image in read_lines(images, skip_empty=True):
        image_new = f"{registry}/{image.split('/', 1)[-1]}"
        DockerArtifact.tag(image, image_new)
        DockerArtifact.push(image_new)
        DockerArtifact.remove(image)
