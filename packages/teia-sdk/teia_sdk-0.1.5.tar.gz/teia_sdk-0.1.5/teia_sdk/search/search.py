from pathlib import Path
from typing import Annotated, Optional
import json

import typer
from rich import print
from typer import Option

from .client import SearchClient
from ..utils import ppjson

app = typer.Typer()


@app.command()
def find(
    query: Annotated[str, Option("-q", "--query")],
    model_name: Annotated[str, Option("-m", "--model_name")],
    model_type: Annotated[str, Option("-t", "--model_type")],
    kb_name: Annotated[str, Option("-kb", "--kb_name")],
    threshold: Annotated[float, Option("-th", "--threshold")] = 0.5,
    top_k: Annotated[int, Option("-tk", "--top_k")] = 10,
):
    """Find similar documents in a knowledge base."""
    body = {
        "query": query,
        "model_name": model_name,
        "model_type": model_type,
        "search_settings": [
            {
                "kb_name": kb_name,
                "threshold": threshold,
                "top_k": top_k,
            }
        ],
    }
    response = SearchClient.search(body=body)
    print(ppjson(response))
