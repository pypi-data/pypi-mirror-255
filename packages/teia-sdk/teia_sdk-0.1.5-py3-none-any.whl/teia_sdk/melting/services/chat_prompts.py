from typing import Any, Optional

import httpx
from melting_schemas.templating import ChatPromptTemplate
from melting_schemas.templating.prompt import ChatPrompt, GeneratedFields

from ...utils import handle_erros
from .. import MELT_API_URL, TEIA_API_KEY


class TemplatingClient:
    relative_path = "/templating/chat-prompts"

    @classmethod
    def get_headers(cls) -> dict[str, str]:
        obj = {
            "Authorization": f"Bearer {TEIA_API_KEY}",
        }
        return obj

    @classmethod
    def read_one(
        cls, identifier: Optional[str] = None, name: Optional[str] = None
    ) -> ChatPrompt:
        if identifier is not None:
            res = httpx.get(
                f"{MELT_API_URL}{cls.relative_path}/{identifier}",
                headers=cls.get_headers(),
            )
        elif name is not None:
            res = httpx.get(
                f"{MELT_API_URL}{cls.relative_path}",
                headers=cls.get_headers(),
                params={"name": name},
            )
        else:
            raise ValueError("Must provide either 'identifier' or 'name'.")
        handle_erros(res)
        return res.json()

    @classmethod
    def read_many(
        cls,
        limit: int,
        skip: int,
        name: Optional[str] = None,
        model: Optional[str] = None,
    ) -> list[ChatPrompt]:
        params = {"name": name, "settings.model": model, "$limit": limit, "$skip": skip}
        params = {k: v for k, v in params.items() if v is not None}
        res = httpx.get(
            f"{MELT_API_URL}{cls.relative_path}",
            headers=cls.get_headers(),
            params=params,
        )
        handle_erros(res)
        return res.json()

    @classmethod
    def post(cls, body: ChatPromptTemplate) -> GeneratedFields:
        res = httpx.post(
            f"{MELT_API_URL}{cls.relative_path}",
            headers=cls.get_headers(),
            json=body,
        )
        handle_erros(res)
        return res.json()

    @classmethod
    def delete(cls, name: str) -> dict[str, Any]:
        res = httpx.delete(
            f"{MELT_API_URL}{cls.relative_path}/{name}",
            headers=cls.get_headers(),
        )
        try:
            res.raise_for_status()
            return {"status_code": res.status_code}
        except httpx.HTTPError:
            body = res.json()
            return {"status_code": res.status_code, **body}
