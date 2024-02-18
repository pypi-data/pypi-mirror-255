from pathlib import Path
from typing import Annotated, Optional
import json

import typer
from rich import print
from typer import Option

from .client import PluginClient
from ..utils import ppjson

app = typer.Typer()


@app.command()
def available():
    response = PluginClient.available_plugins()
    ppjson(response)


@app.command()
def select():
    pass


@app.command()
def run():
    pass


@app.command()
def select_and_run():
    pass
