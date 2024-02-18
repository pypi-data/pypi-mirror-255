import datetime
from typing import NotRequired, TypedDict
from pathlib import Path

from tauth.schemas import Creator


class IndexingSettings(TypedDict):
    model: str
    parsers: NotRequired[dict[str, str]]


class PrivateWorkspaceCreationRequest(TypedDict):
    name: str
    indexing_settings: IndexingSettings


class PrivateWorkspaceCreationResponse(PrivateWorkspaceCreationRequest):
    created_at: datetime
    created_by: Creator
    workspace_id: str


class PrivateWorkspace(TypedDict):
    id: str
    created_by: Creator
    name: str
    indexing_settings: IndexingSettings


class PrivateFile(TypedDict):
    created_by: Creator
    workspace_id: str
    filepath: Path | str
    filename: str
    filetype: str
    content: NotRequired[str]
    content_hash: NotRequired[str]
    content_type: NotRequired[str]
    media_type: NotRequired[str]
    size_bytes: int


class OperationExecution(TypedDict):
    created_at: datetime
    message: NotRequired[str]
    status: str


class IndexingOperation(TypedDict):
    type: str
    executions: NotRequired[list[OperationExecution]]


class PrivateWorkspaceIndexing(TypedDict):
    id: str
    workspace_id: str
    operations: NotRequired[list[IndexingOperation]]
