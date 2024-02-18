from . import app
from .image import app as image_app

app.add_typer(image_app, name='image')


def main():
    app()
