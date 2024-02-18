from pathlib import Path
from typing import Annotated, Optional
import json

import typer
from rich import print
from typer import Option

from .client import MFClient
from ..utils import ppjson

app = typer.Typer()


@app.command()
def put(
    name: Annotated[str, Option("-n", "--name")],
    file: Annotated[
        Path,
        Option(
            "-f", "--file", exists=True, file_okay=True, readable=True, allow_dash=True
        ),
    ],
):
    print("put", repr(name), repr(file))


@app.command()
def read_one(
    identifier: Annotated[Optional[str], Option("--id", metavar="ID")] = None,
    name: Annotated[Optional[str], Option("-n", "--name")] = None,
):
    if identifier is None and name is None:
        typer.echo("Must provide either 'identifier' or 'name'.")
        raise typer.Abort()
    ppjson(MFClient.chat_prompts.read_one(identifier=identifier, name=name))


@app.command()
def read_many(
    name: Annotated[Optional[str], Option("-n", "--name")] = None,
    model: Annotated[Optional[str], Option("-m", "--model")] = None,
    limit: Annotated[int, Option("-l", "--limit")] = 10,
    skip: Annotated[int, Option("-s", "--skip")] = 0,
):
    ppjson(
        MFClient.chat_prompts.read_many(name=name, model=model, limit=limit, skip=skip)
    )


@app.command()
def post(
    file: Annotated[
        Path,
        Option(
            "-f", "--file", exists=True, file_okay=True, readable=True, allow_dash=True
        ),
    ],
):
    ppjson(MFClient.chat_prompts.post(json.load(file.open())))


@app.command()
def delete(
    name: Annotated[str, Option("-n", "--name")],
):
    if name is None:
        typer.echo("Must provide 'name'.")
        raise typer.Abort()
    else:
        ppjson(MFClient.chat_prompts.delete(name))
