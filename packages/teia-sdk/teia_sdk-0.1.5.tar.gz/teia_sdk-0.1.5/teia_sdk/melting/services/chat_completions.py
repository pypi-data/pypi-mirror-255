import json
import os
from typing import Any, Iterator, Optional

import httpx
import requests
from melting_schemas.historian.chat_completions import (
    ChatCompletionCreationResponse,
    ChatCompletionRequest,
    HybridChatCompletionRequest,
    RawChatCompletionRequest,
    StreamedChatCompletionCreationResponse,
)

from ...exceptions import TeiaSdkError
from ...utils import handle_erros
from .. import MELT_API_URL, TEIA_API_KEY
from ..schemas import ChatCompletionResponse


class CompletionClient:
    relative_path = "/text-generation/chat-completions"
    timeout = 60

    @classmethod
    def get_headers(cls) -> dict[str, str]:
        obj = {
            "Authorization": f"Bearer {TEIA_API_KEY}",
        }
        return obj

    @classmethod
    def create_one(
        cls,
        body: ChatCompletionRequest
        | RawChatCompletionRequest
        | HybridChatCompletionRequest,
        user_email: Optional[str] = None,
    ) -> ChatCompletionCreationResponse:
        if not isinstance(body, dict):
            body = body.dict(exclude_none=True)

        headers = cls.get_headers()
        if user_email:
            headers["X-User-Email"] = user_email

        res = httpx.post(
            f"{MELT_API_URL}{cls.relative_path}/create",
            timeout=cls.timeout,
            headers=headers,
            json=body,
        )

        return res.json()

    @classmethod
    def read_one(cls, identifier: str) -> ChatCompletionResponse:
        res = httpx.get(
            f"{MELT_API_URL}{cls.relative_path}/{identifier}",
            headers=cls.get_headers(),
        )
        handle_erros(res)
        return res.json()

    @classmethod
    def stream_one(
        cls,
        body: ChatCompletionRequest
        | RawChatCompletionRequest
        | HybridChatCompletionRequest,
        count_tokens: bool = False,
        user_email: Optional[str] = None,
    ) -> tuple[str, Iterator[StreamedChatCompletionCreationResponse]]:
        if not isinstance(body, dict):
            body = body.dict(exclude_none=True)

        headers = cls.get_headers()
        if count_tokens:
            headers["X-Count-Tokens"] = "true"
        if user_email:
            headers["X-User-Email"] = user_email
        # TODO: use httpx stream instead of requests
        res = requests.post(
            f"{MELT_API_URL}{cls.relative_path}/stream",
            headers=headers,
            json=body,
            stream=True,
        )
        try:
            res.raise_for_status()
        except requests.HTTPError as e:
            raise TeiaSdkError(res.json()) from e
        identifier = res.headers["Content-Location"].split("/")[-1]
        return identifier, map(json.loads, res.iter_lines())
