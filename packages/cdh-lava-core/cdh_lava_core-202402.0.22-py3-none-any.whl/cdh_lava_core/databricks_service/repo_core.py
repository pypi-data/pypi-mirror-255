""" Module for rep_core for it_cdc_admin_service that handles repository and cluster functions with minimal dependencies. """

import os
import sys
from html.parser import HTMLParser  # web scraping html
from urllib.parse import urlparse
from pathlib import Path
import requests
from datetime import datetime
import json

# certs
import certifi

from cdh_lava_core.cdc_log_service.environment_logging import LoggerSingleton

# Get the currently running file name
NAMESPACE_NAME = os.path.basename(os.path.dirname(__file__))
# Get the parent folder name of the running file
SERVICE_NAME = os.path.basename(__file__)


class RepoCore:
    @staticmethod
    def get_cicd_destination_path(
        cdh_folder_config: str, data_product_id: str, environment: str
    ) -> str:
        """
        Get the destination path for the CICD action.

        Args:
            cdh_folder_config (str): The CDH folder configuration.
            data_product_id (str): The data product ID.
            environment (str): The environment.

        Returns:
            str: The destination path for the CICD action.
        """

        tracer, logger = LoggerSingleton.instance(
            NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
        ).initialize_logging_and_tracing()

        with tracer.start_as_current_span("get_cicd_destination_path"):
            try:
                cicd_action_folder = cdh_folder_config.replace("config", "cicd")

                current_date_time = datetime.now().strftime("%Y_%m_%d_%I_%M_%S_%p")

                cicd_action_folder = cicd_action_folder.replace("abfss", "https")
                url = urlparse(cicd_action_folder)
                container = url.netloc.split("@")[0]
                base_address = url.netloc.split("@")[1]
                path = url.path
                destination_path = f"https://{base_address}/{container}{path}pull_request_{current_date_time}.json"

                return destination_path

            except Exception as ex:
                error_msg = "Error: %s", ex
                exc_info = sys.exc_info()
                LoggerSingleton.instance(
                    NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
                ).error_with_exception(error_msg, exc_info)
                raise

    @classmethod
    def pull_repository_latest(
        cls,
        config: dict,
        token: str,
        base_path: str,
        repository_name: str,
        branch_name: str,
        data_product_id: str,
        environment: str,
    ) -> str:
        """
        Pulls the latest version of a repository from a Databricks workspace.

        Args:
            config (dict): The configuration settings for the Databricks instance.
            token (str): The authentication token for accessing the Databricks API.
            base_path (str): The base path of the repository in the Databricks workspace.
            repository_name (str): The name of the repository to pull.
            branch_name (str): The name of the branch to switch to after pulling the repository.
            data_product_id (str): The ID of the data product associated with the repository.
            environment (str): The environment in which the repository is being pulled.

        Returns:
            str: The response data from the Databricks API.

        Raises:
            Exception: If an error occurs while pulling the repository.

        """

        tracer, logger = LoggerSingleton.instance(
            NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
        ).initialize_logging_and_tracing()

        with tracer.start_as_current_span("pull_repository_latest"):
            try:
                databricks_instance_id = config["databricks_instance_id"]
                json_text = {"path": base_path}
                headers = {"Authentication": f"Bearer {token}"}
                api_url = f"https://{databricks_instance_id}"
                url = f"{api_url}/api/2.0/workspace/list"
                verify = certifi.where()

                logger.info(f"------- Fetch {base_path}  -------")
                logger.info(f"url:{str(url)}")
                headers_redacted = str(headers).replace(token, "[bearer REDACTED]")
                logger.info(f"headers:{headers_redacted}")

                response = requests.get(
                    url=url, headers=headers, json=json_text, verify=verify
                )
                data = None

                try:
                    data = response.json()
                    response_text_fetch = (
                        f"Suceess: Received list_repos with length : {len(str(data))}"
                    )
                    response_text_fetch = (
                        response_text_fetch + f" when posting to : {url}"
                    )
                    print(f"{response_text_fetch}")
                    print(f"listed files for : {base_path}")
                    print(str(data))
                    lst = data["objects"]
                    repos = list(
                        filter(
                            lambda itm: str(Path(itm["path"]).stem).upper()
                            == repository_name.upper(),
                            lst,
                        )
                    )

                    if repos[0] is None:
                        repo_data = "Error Repo Not found"
                    else:
                        repo_object = repos[0]
                        repo_id = repo_object["object_id"]
                        url = f"{api_url}/api/2.0/repos/{repo_id}"
                        print(f"repo_id:{repo_id} branch_name:{branch_name}")
                        repo_data = requests.patch(
                            url=url,
                            headers=headers,
                            verify=verify,
                            json={"branch": branch_name},
                        ).json()
                except Exception as exception_object:
                    filter_object = HTMLFilter()
                    filter_object.feed(response.text)
                    response_text = filter_object.text
                    repo_data = (
                        f"Response : error - {exception_object}: {response_text}"
                    )

                print(repo_data)

                return repo_data
            except Exception as ex:
                error_msg = "Error: %s", ex
                exc_info = sys.exc_info()
                LoggerSingleton.instance(
                    NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
                ).error_with_exception(error_msg, exc_info)
                raise

    @staticmethod
    def import_file(
        config, content_data, content_type, file_path, data_product_id, environment
    ) -> bool:
        """
        Imports a file into Databricks workspace.

        Args:
            config (dict): Configuration parameters.
            content_data (bytes or str): Content of the file to be imported.
            content_type (str): Type of the content_data ('bytes' or 'text').
            file_path (str): Path of the file in the Databricks workspace.

        Returns:
            bool: True if the file import is successful, False otherwise.
        """

        tracer, logger = LoggerSingleton.instance(
            NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
        ).initialize_logging_and_tracing()

        with tracer.start_as_current_span("import_file"):
            try:
                environment = config["environment"]
                data_product_id = config["data_product_id"]
                data_product_id_root = config["data_product_id_root"]
                file_name = os.path.basename(file_path)
                databricks_instance_id = config["databricks_instance_id"]
                token = config["access_token"]
                bearer = "Bearer " + token
                headers = {"Authorization": bearer, "Content-Type": "application/json"}
                headers_redacted = str(headers).replace(bearer, "[bearer REDACTED]")
                api_version = "/api/2.0"
                databricks_instance_id = config["databricks_instance_id"]
                api_command = "/workspace/import"
                url = f"https://{databricks_instance_id}{api_version}{api_command}"

                file_path = file_path.replace("/Workspace", "")

                logger.info(f"content_type:{content_type}")
                logger.info(f"url:{url}")

                if content_type == "bytes":
                    # , "Content-Type": "multipart/form-data"
                    headers_import = {"Authorization": bearer}
                    headers_redacted = str(headers_import).replace(
                        bearer, "[bearer REDACTED]"
                    )
                    try:
                        content_data.decode("UTF-8")
                    except (UnicodeDecodeError, AttributeError):
                        content_data = bytes(content_data, "utf-8")
                        pass

                    files = {"upload_file": content_data}
                    multipart_form_data = {"path": f"{file_path}"}

                    logger.info(f"multipart_form_data:{str(multipart_form_data)}")
                    logger.info(f"headers:{headers_redacted}")

                    # binary
                    # https://dbc-a1b2345c-d6e7.cloud.databricks.com/api/2.0/workspace/import \
                    # --header 'Content-Type: multipart/form-data' \
                    # --form path=/Users/me@example.com/MyFolder/MyNotebook \
                    # --form content=@myCode.py.zip

                    response_binary = CDHObject()
                    response_binary.text = "Empty. Unable to retrieve post response"
                    # data=multipart_form_data,
                    try:
                        response_binary = requests.post(
                            url=url,
                            files=files,
                            data=multipart_form_data,
                            headers=headers_import,
                        )
                        print(f"post : success : {url} ")
                        response_binary_text = json.loads(response_binary.text)
                        response_binary_text = json.dumps(response_binary_text.json())
                        print(f"parse : success : {url}")
                        response_binary_text_message = (
                            "Received Cluster API Response : "
                        )
                        response_binary_text_message += (
                            f"{response_binary_text} when posting to : {url}  "
                        )
                        response_binary_text_message += f"to import file: {file_path}"
                    except Exception as exception_check:
                        html_filter = HTMLFilter()
                        html_filter.feed(response_binary.text)
                        response_install_text_message = html_filter.text
                        print(f"url : error - {str(exception_check)}")
                        print("Error IMPORT-FILE-RESPONSE")
                        print(f"response error code:{str(response_binary)}")
                        print(f"response error message:{response_install_text_message}")
                elif content_type == "text":
                    # text
                    # curl -n -X POST https://<databricks-instance>/api/2.0/workspace/import
                    # -F path="/Users/user@example.com/new-notebook" -F format=SOURCE -F language=SCALA -F overwrite=true -F content=@notebook.scala

                    headers_import = {
                        "Authorization": bearer,
                        "Accept": "application/json",
                    }
                    headers_redacted = str(headers_import).replace(
                        bearer, "[bearer REDACTED]"
                    )

                    logger.info(f"headers:{headers_redacted}")
                    logger.info(f"json:{str(content_data[ 0 : 100 ])}...")

                    response_json = requests.post(
                        url=url, json=content_data, headers=headers_import
                    )

                return response_json
            except Exception as ex:
                error_msg = "Error: %s", ex
                exc_info = sys.exc_info()
                LoggerSingleton.instance(
                    NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
                ).error_with_exception(error_msg, exc_info)
                raise


class HTMLFilter(HTMLParser):
    """
    A class for filtering HTML content and extracting text data.
    """

    text = ""

    def handle_data(self, data):
        self.text += data


class CDHObject(object):
    """
    Represents a CDH object.
    """

    pass
