from azure.storage.queue import QueueServiceClient
from azure.identity import ClientSecretCredential
import requests
from typing import List
import json
from html.parser import HTMLParser  # web scraping html
import subprocess
import os

from cdh_lava_core.cdc_log_service.environment_logging import LoggerSingleton

# Get the currently running file name
NAMESPACE_NAME = os.path.basename(os.path.dirname(__file__))
# Get the parent folder name of the running file
SERVICE_NAME = os.path.basename(__file__)


class GitHubSecret:
    """Represents a GitHub secret.

    Attributes:
        _summary_: _type_ - _description_

    Returns:
        None
    """

    # Get the currently running file name
    NAMESPACE_NAME = os.path.basename(os.path.dirname(__file__))
    # Get the parent folder name of the running file
    SERVICE_NAME = os.path.basename(__file__)

    @staticmethod
    def get_github_secret(
        gh_access_token, gh_owner_name, gh_repository_name, gh_secret_name
    ):
        """
        Retrieves a secret value from a GitHub repository using the GitHub API.

        Args:
            gh_access_token (str): The GitHub personal access token with appropriate permissions.
            gh_owner_name (str): The owner or organization name of the GitHub repository.
            gh_repository_name (str): The name of the GitHub repository.
            gh_secret_name (str): The name of the secret to retrieve.

        Returns:
            str: The value of the retrieved secret.

        Raises:
            requests.exceptions.RequestException: If an error occurs while making the API request.
            KeyError: If the secret value is not found in the API response.

        """

        tracer, logger = LoggerSingleton.instance(
            NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
        ).initialize_logging_and_tracing()

        with tracer.start_as_current_span("get_github_secret"):
            headers = {
                "Accept": "application/vnd.github.v3+json",
                "Authorization": f"Bearer {gh_access_token}",
            }

            api_url = f"https://api.github.com/repos/{gh_owner_name}/{gh_repository_name}/actions/secrets/{gh_secret_name}"

            print(f"api_url:{str(api_url)}")

            try:
                response = requests.get(api_url, headers=headers)
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

            # Extract the secret value
            secret_value = response_content.get("secret", {}).get("value", None)

            if secret_value is not None:
                print(f"Secret Value Len: {str(len(secret_value))}")
            else:
                return response.status_code, response_content, api_url

            return response.status_code, response_content, api_url

    @staticmethod
    def get_github_secret_interactive(
        gh_owner_name, gh_repository_name, gh_secret_name
    ):
        """
        Retrieves a secret value from a GitHub repository using the GitHub CLI.
        This function checks if the user is already logged in using GitHub CLI and
        prompts them to manually login if they're not. The function then proceeds to
        retrieve the secret value from the specified GitHub repository.

        Args:
            gh_owner_name (str): The owner or organization name of the GitHub repository.
            gh_repository_name (str): The name of the GitHub repository.
            gh_secret_name (str): The name of the secret to retrieve.

        Returns:
            int, dict, str: The status code of the response, the content of the response
            as a dictionary, and the API url string respectively.

        Raises:
            subprocess.CalledProcessError: If an error occurs while making the API request.
        """
        logger_singleton = LoggerSingleton.instance(NAMESPACE_NAME, SERVICE_NAME)

        # Check if user is logged in
        try:
            subprocess.check_output(["gh", "auth", "status"], stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError:
            print(
                "Please login using GitHub CLI by typing 'gh auth login' in your terminal."
            )
            return

        with tracer.start_as_current_span("get_github_secret"):
            command = f"gh secret list --repo {gh_owner_name}/{gh_repository_name}"
            print(f"Command:{str(command)}")

            try:
                # Use gh CLI tool to make the command
                gh_response = subprocess.check_output(command.split())
                response_content = gh_response.decode("utf-8")
            except subprocess.CalledProcessError as e:
                logger.error(f"Command failed: {e}")
                return 500, f"Command failed: {e}", command

            # Log the response content
            logger.info(f"response_content: {response_content}")

            # Check if the secret exists
            secret_exists = gh_secret_name in response_content

            if secret_exists:
                print(f"Secret {gh_secret_name} exists.")
                try:
                    api_url = f"https://api.github.com/repos/{gh_owner_name}/{gh_repository_name}/actions/secrets/{gh_secret_name}"
                    gh_response = subprocess.check_output(
                        ["gh", "api", api_url], universal_newlines=True
                    )
                    response_content = json.loads(gh_response)
                except subprocess.CalledProcessError as e:
                    logger.error(f"Command failed: {e}")
                    return 500, f"Command failed: {e}", command

            else:
                return 404, f"Secret {gh_secret_name} not found.", command

            return 200, response_content, command


class HTMLFilter(HTMLParser):
    """Parses HTMLData

    Args:
        HTMLParser (_type_): _description_
    """

    text = ""

    def handle_data(self, data):
        """Parses HTMLData

        Args:
            data (_type_): _description_
        """
        self.text += data
