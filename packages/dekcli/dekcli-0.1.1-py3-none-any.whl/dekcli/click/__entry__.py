from . import app
from .giteaapi import app as gitea_app

app.add_typer(gitea_app, name='gitea')


def main():
    app()
