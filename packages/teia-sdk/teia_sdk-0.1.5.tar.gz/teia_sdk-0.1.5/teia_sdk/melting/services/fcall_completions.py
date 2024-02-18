import httpx
from typing import Optional
from melting_schemas.completion.fcall import RawFCallRequest, FCallCompletionCreationResponse

from .. import TEIA_API_KEY, MELT_API_URL
from ...utils import handle_erros


class FCallCompletionsClient:
    relative_path = "/text-generation/fcall-completions"
    client = httpx.Client(timeout=60)

    @classmethod
    def get_headers(cls) -> dict[str, str]:
        obj = {
            "Authorization": f"Bearer {TEIA_API_KEY}",
        }
        return obj

    @classmethod
    def create_one(cls, body: RawFCallRequest, user_email: Optional[str] = None) -> FCallCompletionCreationResponse:
        headers = cls.get_headers()
        if user_email:
            headers["X-User-Email"] = user_email

        res = cls.client.post(
            f"{MELT_API_URL}{cls.relative_path}/create",
            headers=headers,
            json=body.dict(),
        )
        handle_erros(res)
        return res.json()
