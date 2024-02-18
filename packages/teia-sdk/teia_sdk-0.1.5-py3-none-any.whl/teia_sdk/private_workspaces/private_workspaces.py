import typer

from .client import PrivateWorkspaceClient
from ..utils import ppjson

app = typer.Typer()


# TODO
@app.command()
def get_private_workspaces():
    response = PrivateWorkspaceClient.get_private_workspaces()
    ppjson(response)
