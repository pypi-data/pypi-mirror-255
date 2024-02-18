import json

import httpx
import requests
from http_error_schemas.factory import get_error_class
from rich import print

from .exceptions import TeiaSdkError


def pjson(obj):
    """Prettify JSON."""
    return json.dumps(obj, indent=4, sort_keys=True)


def ppjson(obj):
    """Pretty print JSON."""
    print(pjson(obj))


def handle_erros(response: requests.Response | httpx.Response):
    try:
        response.raise_for_status()
    except (requests.HTTPError, httpx.HTTPStatusError) as e:
        exc = get_error_class(response.status_code)
        obj = response.json()
        ppjson(exc(**obj))
        raise TeiaSdkError(obj, e.request, e.response) from e
    except (requests.RequestException, httpx.RequestError) as e:
        print(e.request)
        raise TeiaSdkError(response.json()) from e
