import json
import os
import httpx

from .schemas import SearchRequest, SearchResponse

try:
    TEIA_API_KEY = os.environ["TEIA_API_KEY"]
    SEARCH_API_URL = os.getenv("SEARCH_API_URL", "https://plugins.athena.teialabs.com.br")
except KeyError:
    m = "[red]MissingEnvironmentVariables[/red]: "
    m += "[yellow]'TEIA_API_KEY'[/yellow] cannot be empty."
    print(m)
    exit(1)


class SearchClient:
    relativepath = "/search/"  # TODO remove slash

    @classmethod
    def get_headers(cls) -> dict[str, str]:
        obj = {
            "Authorization": f"Bearer {TEIA_API_KEY}",
        }
        return obj

    @classmethod
    def search(cls, body: SearchRequest) -> SearchResponse:
        response = httpx.post(
            url=f"{SEARCH_API_URL}{cls.relativepath}",
            headers=cls.get_headers(),
            json=body,
        )
        return response.json()
