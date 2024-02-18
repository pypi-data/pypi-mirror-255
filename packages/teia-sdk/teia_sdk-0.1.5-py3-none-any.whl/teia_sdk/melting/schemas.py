from datetime import datetime
from typing import Literal, Optional, TypedDict

from melting_schemas.completion.chat import (
    ChatMLMessage,
    StreamTimings,
    Timings,
    TokenUsage,
)
from melting_schemas.historian import Templating
from melting_schemas.meta import Creator


class ChatCompletionResponse(TypedDict):
    _id: str
    created_at: datetime
    created_by: Creator
    finish_reason: Literal["stop", "length"]
    messages: list[ChatMLMessage]
    output: ChatMLMessage
    settings: dict
    templating: Optional[Templating]
    timings: Timings | StreamTimings
    usage: TokenUsage
