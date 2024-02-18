import logging
import os
from pathlib import Path
from typing import Optional
from fastapi import UploadFile

from starlette import status as http_status
import httpx

from .exceptions import (
    PrivateWorkspaceFileNotFound,
    PrivateWorkspaceNotFound,
)
from .schemas import (
    PrivateFile,
    PrivateWorkspace,
    PrivateWorkspaceCreationRequest,
    PrivateWorkspaceCreationResponse,
    PrivateWorkspaceIndexing,
)

from ..utils import handle_erros

try:
    TEIA_API_KEY = os.environ["TEIA_API_KEY"]
    DATASOURCES_API_URL = os.getenv(
        "DATASOURCES_API_URL", "https://datasources.teialabs.com.br"
    )
except KeyError:
    m = "[red]MissingEnvironmentVariables[/red]: "
    m += "[yellow]'TEIA_API_KEY'[/yellow] cannot be empty."
    print(m)
    exit(1)


class PrivateWorkspaceClient:
    relative_path = "/api/workspaces"

    @classmethod
    def get_headers(cls) -> dict[str, str]:
        obj = {
            "Authorization": f"Bearer {TEIA_API_KEY}",
        }
        return obj

    @classmethod
    def get_headers_with_user_email(cls, user_email: Optional[str] = None) -> dict[str, str]:
        headers = cls.get_headers()
        if user_email is not None:
            headers["X-User-Email"] = user_email
        return headers

    @classmethod
    def upload_many_files(
        cls,
        workspace_id: str,
        file_paths: Optional[list[Path]] = None,
        files: Optional[list[UploadFile]] = None,
        user_email: Optional[str] = None,
    ):
        """
        Uploads files to be processed.
        """
        if files is None and file_paths is None:
            raise ValueError("Either 'files' or 'file_paths' must be provided.")

        if files is None:
            files = []
            for p in file_paths:
                files.append(("files", open(p, "rb")))

        headers = cls.get_headers_with_user_email(user_email)
        res = httpx.put(
            f"{DATASOURCES_API_URL}{cls.relative_path}/{workspace_id}/files",
            headers=headers,
            files=files,
        )
        return res.json()

    @classmethod
    def create_private_workspace(
        cls,
        workspace: PrivateWorkspaceCreationRequest,
        user_email: Optional[str] = None,
    ) -> PrivateWorkspaceCreationResponse:
        """
        Create a private workspace.
        """
        headers = cls.get_headers_with_user_email(user_email)
        res = httpx.post(
            f"{DATASOURCES_API_URL}{cls.relative_path}/",
            headers=headers,
            json=workspace,
        )
        handle_erros(res)
        return res.json()

    @classmethod
    def get_many_private_workspaces(
        cls,
        sort: Optional[str] = None,
        order: Optional[str] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        workspace_id: Optional[str] = None,
        name: Optional[str] = None,
        user_email: Optional[str] = None,
    ) -> list[PrivateWorkspace]:
        """
        Retrieve a list of private workspaces.
        """
        params = {
            "sort": sort,
            "order": order,
            "limit": limit,
            "offset": offset,
            "workspace_id": workspace_id,
            "name": name,
        }
        params = {k: v for k, v in params.items() if v is not None}
        headers = cls.get_headers_with_user_email(user_email)
        res = httpx.get(
            f"{DATASOURCES_API_URL}{cls.relative_path}/",
            headers=headers,
            params=params,
        )
        handle_erros(res)
        return res.json()

    @classmethod
    def get_private_workspace(
        cls, workspace_id: str, user_email: Optional[str] = None
    ) -> PrivateWorkspace:
        """
        Get a private workspace.
        """
        headers = cls.get_headers_with_user_email(user_email)
        res = httpx.get(
            f"{DATASOURCES_API_URL}{cls.relative_path}/{workspace_id}/",
            headers=headers,
        )
        if res.status_code == http_status.HTTP_404_NOT_FOUND:
            raise PrivateWorkspaceNotFound(f"Workspace '{workspace_id}' not found.")
        handle_erros(res)
        return res.json()

    @classmethod
    def list_file(
        cls,
        workspace_id: str,
        file_path: str | Path,
        return_file_content: Optional[bool] = None,
        user_email: Optional[str] = None,
    ) -> PrivateFile:
        """
        Show a specific file in a given private workspace.
        """
        headers = cls.get_headers_with_user_email(user_email)
        res = httpx.get(
            f"{DATASOURCES_API_URL}{cls.relative_path}/{workspace_id}/files/{file_path}",
            headers=headers,
            params={"return_content": return_file_content},
        )
        if res.status_code == http_status.HTTP_404_NOT_FOUND:
            raise PrivateWorkspaceFileNotFound(f"File '{file_path}' not found.")

        handle_erros(res)
        return res.json()

    @classmethod
    def list_many_files(
        cls,
        workspace_id: str,
        file_path: Optional[str] = None,
        file_name: Optional[str] = None,
        file_type: Optional[str] = None,
        return_file_content: Optional[bool] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        sort: Optional[str] = None,
        order: Optional[str] = None,
        user_email: Optional[str] = None,
    ) -> list[PrivateFile]:
        """
        Shows files in a given private workspace.
        """
        params = {
            "file_path": file_path,
            "file_name": file_name,
            "file_type": file_type,
            "return_file_content": return_file_content,
            "limit": limit,
            "offset": offset,
            "sort": sort,
            "order": order,
        }
        params = {k: v for k, v in params.items() if v is not None}
        headers = cls.get_headers_with_user_email(user_email)
        res = httpx.get(
            f"{DATASOURCES_API_URL}{cls.relative_path}/{workspace_id}/files/",
            headers=headers,
            params=params,
        )
        handle_erros(res)
        return res.json()

    @classmethod
    def upload_file(
        cls, workspace_id: str, file_path: Path, file: Optional[UploadFile] = None,
        user_email: Optional[str] = None
    ) -> PrivateFile:
        """
        Uploads a file to be processed.
        """
        if file is None:
            file = open(file_path, "rb")
        file = {"file": file}

        headers = cls.get_headers_with_user_email(user_email)
        res = httpx.put(
            f"{DATASOURCES_API_URL}{cls.relative_path}/{workspace_id}/files/{file_path}",
            headers=headers,
            files=file,
        )
        handle_erros(res)
        return res.json()

    @classmethod
    def delete_file(cls, workspace_id: str, file_path: str | Path, user_email: Optional[str] = None):
        """
        Delete a file from a private workspace.
        """
        headers = cls.get_headers_with_user_email(user_email)
        res = httpx.delete(
            f"{DATASOURCES_API_URL}{cls.relative_path}/{workspace_id}/files/{file_path}",
            headers=headers,
        )
        handle_erros(res)
        return res

    @classmethod
    def create_indexing(cls, workspace_id: str, user_email: Optional[str] = None) -> PrivateWorkspaceIndexing:
        """
        Uploads a file to be processed.
        """
        headers = cls.get_headers_with_user_email(user_email)
        res = httpx.post(
            f"{DATASOURCES_API_URL}{cls.relative_path}/{workspace_id}/indexings/",
            headers=headers,
        )
        handle_erros(res)
        return res.json()

    @classmethod
    def get_indexing(
        cls,
        workspace_id: str,
        indexing_id: str,
        user_email: Optional[str] = None,
    ) -> PrivateWorkspaceIndexing:
        """
        Get information from an indexing process.
        """
        headers = cls.get_headers_with_user_email(user_email)
        res = httpx.get(
            f"{DATASOURCES_API_URL}{cls.relative_path}/{workspace_id}/indexings/{indexing_id}",
            headers=headers,
        )
        handle_erros(res)
        return res.json()

    @classmethod
    def get_many_indexings(
        cls,
        workspace_id: str,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        sort: Optional[str] = None,
        order: Optional[str] = None,
        user_email: Optional[str] = None,
    ) -> list[PrivateWorkspaceIndexing]:
        """
        Get information from all indexing processes in a workspace.
        """
        params = {
            "limit": limit,
            "offset": offset,
            "sort": sort,
            "order": order,
        }
        params = {k: v for k, v in params.items() if v is not None}
        headers = cls.get_headers_with_user_email(user_email)
        res = httpx.get(
            f"{DATASOURCES_API_URL}{cls.relative_path}/{workspace_id}/indexings/",
            headers=headers,
            params=params,
        )
        handle_erros(res)
        return res.json()

    @classmethod
    def delete_private_workspace(cls, workspace_id: str, user_email: Optional[str] = None):
        """
        Delete workspace and all resources related to it.
        """
        headers = cls.get_headers_with_user_email(user_email)
        res = httpx.delete(
            f"{DATASOURCES_API_URL}{cls.relative_path}/{workspace_id}",
            headers=headers,
        )
        handle_erros(res)
        return res

    @classmethod
    def search_on_workspace(
        cls,
        workspace_id: str,
        query: str,
        num_results: Optional[int] = None,
        schemaless: Optional[bool] = None,
        user_email: Optional[str] = None,
    ) -> list[dict]:
        """
        Perform an embedding search in a private workspace.
        """
        params = {
            "query": query,
            "num_results": num_results,
            "schemaless": schemaless,
        }
        params = {k: v for k, v in params.items() if v is not None}
        headers = cls.get_headers_with_user_email(user_email)
        res = httpx.post(
            f"{DATASOURCES_API_URL}{cls.relative_path}/{workspace_id}/search/",
            headers=headers,
            params=params,
        )
        handle_erros(res)
        return res.json()
