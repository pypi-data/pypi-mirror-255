"""
This module provides a client for managing interactions with the Databricks Workspace API, enabling
operations such as listing, creating directories, deleting paths, and importing or exporting files
within the Databricks workspace. It supports a range of functionalities tailored towards
efficient workspace management, including handling notebooks, directories, and other file types
through REST API calls. The WorkspaceClient class encapsulates methods for these operations, offering
an interface for tasks like listing workspace objects, creating and deleting directories, importing
HTML and DBC files, managing notebooks, and retrieving object status, with support for recursive
operations and filtering by object types.

Classes:
    WorkspaceClient: A client class for interacting with the Databricks workspace API. It requires
    a RestClient instance for API requests and provides methods to list, create, delete, import,
    and export workspace objects, including notebooks and directories.

Usage:
    The WorkspaceClient class simplifies interactions with the Databricks workspace, abstracting
    the complexity of direct API calls. It allows users to programmatically manage their workspace
    resources, such as creating directories for organization, importing notebooks for execution or
    sharing, and exporting content for backup or analysis. The class methods are designed for
    ease of use, making workspace management more accessible and efficient.
"""

import os
import base64
import urllib
from urllib.parse import urlencode
from typing import Union

from cdh_lava_core.databricks_service.dbx_db_rest import RestClient
from cdh_lava_core.databricks_service.dbx_rest.common import ApiContainer


class WorkspaceClient(ApiContainer):
    """
    A client for interacting with the Databricks workspace API.

    Args:
        client (RestClient): The REST client used to make API requests.

    Attributes:
        client (RestClient): The REST client used to make API requests.
    """

    def __init__(self, client: RestClient):
        self.client = client

    def ls(self, path, recursive=False, object_types=None):
        """
        List the objects in the workspace at the specified path.

        Args:
            path (str): The path in the workspace.
            recursive (bool, optional): Whether to list objects recursively. Defaults to False.
            object_types (list[str], optional): The types of objects to include in the listing. Defaults to ["NOTEBOOK"].

        Returns:
            list[dict] or None: A list of objects in the workspace, or None if the path does not exist.
        """
        object_types = object_types or ["NOTEBOOK"]

        if not recursive:
            try:
                results = self.client.execute_get_json(
                    f"{self.client.endpoint}/api/2.0/workspace/list?path={path}",
                    expected=[200, 404],
                )
                if results is None:
                    return None
                else:
                    return results.get("objects", [])

            except Exception as e:
                raise Exception(f"Unexpected exception listing {path}") from e
        else:
            entities = []
            queue = self.ls(path)

            if queue is None:
                return None

            while len(queue) > 0:
                next_item = queue.pop()
                object_type = next_item["object_type"]
                if object_type in object_types:
                    entities.append(next_item)
                elif object_type == "DIRECTORY":
                    result = self.ls(next_item["path"])
                    if result is not None:
                        queue.extend(result)

            return entities

    def mkdirs(self, path) -> dict:
        """
        Create directories in the workspace.

        Args:
            path (str): The path of the directories to create.

        Returns:
            dict: The response from the API.
        """
        return self.client.execute_post_json(
            f"{self.client.endpoint}/api/2.0/workspace/mkdirs", {"path": path}
        )

    def delete_path(self, path) -> dict:
        """
        Delete a path in the workspace.

        Args:
            path (str): The path to delete.

        Returns:
            dict: The response from the API.
        """
        payload = {"path": path, "recursive": True}
        return self.client.execute_post_json(
            f"{self.client.endpoint}/api/2.0/workspace/delete",
            payload,
            expected=[200, 404],
        )

    def import_html_file(self, html_path: str, content: str, overwrite=True) -> dict:
        """
        Import an HTML file into the workspace.

        Args:
            html_path (str): The path of the HTML file in the workspace.
            content (str): The content of the HTML file.
            overwrite (bool, optional): Whether to overwrite an existing file with the same path. Defaults to True.

        Returns:
            dict: The response from the API.
        """

        payload = {
            "content": base64.b64encode(content.encode("utf-8")).decode("utf-8"),
            "path": html_path,
            "language": "PYTHON",
            "overwrite": overwrite,
            "format": "SOURCE",
        }
        return self.client.execute_post_json(
            f"{self.client.endpoint}/api/2.0/workspace/import", payload
        )

    def import_dbc_files(
        self, target_path, source_url=None, overwrite=True, local_file_path=None
    ):
        """
        Import DBC files into the workspace.

        Args:
            target_path (str): The path in the workspace to import the DBC files.
            source_url (str, optional): The URL of the DBC file to import. Either `source_url` or `local_file_path` must be specified. Defaults to None.
            overwrite (bool, optional): Whether to overwrite an existing file with the same path. Defaults to True.
            local_file_path (str, optional): The local file path of the DBC file to import. Either `source_url` or `local_file_path` must be specified. Defaults to None.

        Raises:
            AssertionError: If both `source_url` and `local_file_path` are None.

        Returns:
            dict: The response from the API.
        """

        if local_file_path is None and source_url is None:
            raise AssertionError(
                f"Either the local_file_path ({local_file_path}) or source_url ({source_url}) parameter must be specified"
            )

        if local_file_path is None:
            file_name = source_url.split("/")[-1]
            local_file_path = f"/tmp/{file_name}"

        if source_url is not None:
            if os.path.exists(local_file_path):
                os.remove(local_file_path)

            # noinspection PyUnresolvedReferences
            urllib.request.urlretrieve(source_url, local_file_path)

        with open(local_file_path, mode="rb") as file:
            content = file.read()

        if overwrite:
            self.delete_path(target_path)

        self.mkdirs("/".join(target_path.split("/")[:-1]))

        payload = {
            "content": base64.b64encode(content).decode("utf-8"),
            "path": target_path,
            "overwrite": False,
            "format": "DBC",
        }
        return self.client.execute_post_json(
            f"{self.client.endpoint}/api/2.0/workspace/import", payload
        )

    def import_notebook(
        self, language: str, notebook_path: str, content: str, overwrite=True
    ) -> dict:
        """
        Import a notebook into the workspace.

        Args:
            language (str): The language of the notebook.
            notebook_path (str): The path of the notebook in the workspace.
            content (str): The content of the notebook.
            overwrite (bool, optional): Whether to overwrite an existing file with the same path. Defaults to True.

        Returns:
            dict: The response from the API.
        """

        payload = {
            "content": base64.b64encode(content.encode("utf-8")).decode("utf-8"),
            "path": notebook_path,
            "language": language,
            "overwrite": overwrite,
            "format": "SOURCE",
        }
        return self.client.execute_post_json(
            f"{self.client.endpoint}/api/2.0/workspace/import", payload
        )

    def export_notebook(self, path: str) -> str:
        """
        Export a notebook from the workspace.

        Args:
            path (str): The path of the notebook in the workspace.

        Returns:
            str: The content of the exported notebook.
        """

        params = urlencode({"path": path, "direct_download": "true"})
        return self.client.execute_get(
            f"{self.client.endpoint}/api/2.0/workspace/export?{params}"
        ).text

    def export_dbc(self, path):
        """
        Export a DBC file from the workspace.

        Args:
            path (str): The path of the DBC file in the workspace.

        Returns:
            bytes: The content of the exported DBC file.
        """

        params = urlencode({"path": path, "format": "DBC", "direct_download": "true"})
        return self.client.execute_get(
            f"{self.client.endpoint}/api/2.0/workspace/export?{params}"
        ).content

    def get_status(self, path) -> Union[None, dict]:
        """
        Get the status of an object in the workspace.

        Args:
            path (str): The path of the object in the workspace.

        Returns:
            dict or None: The status of the object, or None if the object does not exist.
        """

        params = urlencode({"path": path})
        response = self.client.execute_get(
            f"{self.client.endpoint}/api/2.0/workspace/get-status?{params}",
            expected=[200, 404],
        )
        if response.status_code == 404:
            return None
        else:
            assert (
                response.status_code == 200
            ), f"({response.status_code}): {response.text}"
            return response.json()
