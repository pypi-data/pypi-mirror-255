from azure.storage.queue import QueueServiceClient
from azure.identity import ClientSecretCredential
import requests
from typing import List
import json
from html.parser import HTMLParser  # web scraping html
import subprocess
import os

from cdh_lava_core.cdc_log_service.environment_logging import LoggerSingleton

from cdh_lava_core.cdc_tech_environment_service import environment_file as cdc_env_file

# Get the currently running file name
NAMESPACE_NAME = os.path.basename(os.path.dirname(__file__))
# Get the parent folder name of the running file
SERVICE_NAME = os.path.basename(__file__)


class GitHubRelease:
    # Get the currently running file name
    NAMESPACE_NAME = os.path.basename(os.path.dirname(__file__))
    # Get the parent folder name of the running file
    SERVICE_NAME = os.path.basename(__file__)

    @staticmethod
    def get_releases(
        gh_access_token: str,
        gh_owner_name: str,
        gh_repository_name: str,
        data_product_id: str,
        environment: str,
    ):
        """
        Retrieves the releases of a GitHub repository.

        Args:
            gh_access_token (str): The access token for authenticating the request.
            gh_owner_name (str): The name of the owner of the GitHub repository.
            gh_repository_name (str): The name of the GitHub repository.
            data_product_id (str): The ID of the data product.
            environment (str): The environment in which the request is being made.

        Returns:
            tuple: A tuple containing the HTTP status code, response content, and API URL.
        """

        tracer, logger = LoggerSingleton.instance(
            NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
        ).initialize_logging_and_tracing()

        with tracer.start_as_current_span("get_releases"):
            headers = {
                "Accept": "application/vnd.github.v3+json",
                "Authorization": f"Bearer {gh_access_token}",
            }

            api_url = f"https://api.github.com/repos/{gh_owner_name}/{gh_repository_name}/releases"

            logger.info(f"api_url:{str(api_url)}")

            try:
                response = requests.get(api_url, headers=headers, timeout=60)
            except requests.exceptions.RequestException as e:
                logger.error(f"Request failed: {e}")
                return 500, f"Request failed: {e}", api_url

            # Convert the response text to JSON
            try:
                response_content = response.json()
            except json.JSONDecodeError as e:
                logger.error(f"Failed to decode JSON: {e}")
                return response.status_code, f"Failed to decode JSON: {e}", api_url

            # Log the response content
            logger.info(f"response_content: {response_content}")

            return response.status_code, response_content, api_url
