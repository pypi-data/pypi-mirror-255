from cdh_lava_core.alation_service.json_manifest import ManifestJson
from cdh_lava_core.alation_service.db_column import Column
from pandas import json_normalize
from bs4 import BeautifulSoup

import json
from jsonschema import validate
import sys
import os
import pandas as pd
import requests


from cdh_lava_core.cdc_log_service.environment_logging import LoggerSingleton

from cdh_lava_core.cdc_tech_environment_service import environment_http as cdc_env_http

import cdh_lava_core.cdc_tech_environment_service.environment_file as cdc_env_file
import cdh_lava_core.alation_service.token as alation_token_endpoint

# Get the currently running file name
NAMESPACE_NAME = os.path.basename(os.path.dirname(__file__))
# Get the parent folder name of the running file
SERVICE_NAME = os.path.basename(__file__)

ENVIRONMENT = "dev"

# Default request time out
REQUEST_TIMEOUT = 180


# Get the absolute path of the current script
current_script_path = os.path.abspath(__file__)

# Get the project root directory by going up one or more levels
project_root = os.path.dirname(os.path.dirname(current_script_path))


class User:
    """
    Represents a user and provides utility methods for user-related operations.

    This class offers functionalities to interact with user data, including methods to convert
    JSON strings to Python dictionaries and to retrieve user details from a specified API endpoint.

    Attributes:
    - No specific attributes defined in the class.

    Methods:
    - convert_to_json_if_string(input_data: Union[str, Any]) -> Union[dict, None]: Converts a JSON string to a Python dictionary.
    - get_users_from_user_id_json(config: dict, user_id_json: Union[str, dict]) -> pd.DataFrame: Fetches user details from an API.
    """

    def is_custom_object(self, obj):
        basic_types = (int, float, str, list, tuple, dict, set, bool, type(None))
        return not isinstance(obj, basic_types)

    def convert_to_json_if_string(self, input_data):
        """
        Converts a JSON string to a Python dictionary.

        Given a JSON string as input, this method attempts to parse it into a Python dictionary.
        If the input is not a string or if there's an error during parsing, appropriate messages
        are printed and None is returned.

        Parameters:
        - input_data (str or Any): JSON string or any data type.

        Returns:
        - dict or None: A Python dictionary if the input was a valid JSON string, otherwise None.

        Notes:
        - This method prints an error message if input_data is not a string or if JSON decoding fails.
        """
        if isinstance(input_data, str):
            try:
                # Convert the JSON string to a Python dictionary
                parsed_data = json.loads(input_data)
                return parsed_data
            except json.JSONDecodeError as e:
                print("Error decoding JSON:", str(e))
                return None

        elif self.is_custom_object(object):
            try:
                json.dumps(input_data)
                return input_data
            except (TypeError, OverflowError):
                print("Error decoding JSON:", str(e))
                return None
        else:
            # Handle non-string data based on your recipe
            print("Input data is not a valid json string or json.")
            return None

    def get_user_list_from_user_ids_json(
        self, user_id_json, edc_alation_api_token, edc_alation_base_url
    ):
        """
        Retrieves user details from an API endpoint given a JSON containing user IDs.

        This method fetches user details by making a request to a specific API endpoint.
        It then processes the data, including handling custom fields, and converts the result
        to a pandas DataFrame.

        Parameters:
        - user_id_json (str or dict): JSON string or dictionary containing user IDs with 'oid' key.
        - edc_alation_api_token (str): The API token to be used for authentication.
        - edc_alation_base_url (str): The base URL for making API calls.

        Returns:
        - pandas.DataFrame: DataFrame containing user details.

        Raises:
        - Exception: If there's an error in API request or response parsing.

        Notes:
        - This method changes the current working directory to the project root directory.
        - It assumes the existence of logger and tracer singletons and certain API structure.
        """

        tracer, logger = LoggerSingleton.instance(
            NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
        ).initialize_logging_and_tracing()
        tracer = tracer_singleton.get_tracer()

        with tracer.start_as_current_span("get_users_from_user_id_json"):
            # setting the base_url so that all we need to do is swap API endpoints
            base_url = edc_alation_base_url
            # api access key
            api_key = edc_alation_api_token
            # setting up this access key to be in the headers
            headers = {"token": api_key}
            # api for users
            metadata_endpoint = "/integration/v2"
            object_type = "user"
            api_url = f"{edc_alation_base_url}{metadata_endpoint}/{object_type}"

            limit = 500
            skip = 0

            user_id_json = self.convert_to_json_if_string(user_id_json)

            # Extract the 'oid' values and convert them to strings
            oid_values = [str(item["oid"]) for item in user_id_json]

            # Join the 'oid' values with '&' separator
            id_string = "&".join([f"id={oid}" for oid in oid_values])

            # Create a dictionary to hold the parameters
            params = {}
            params["limit"] = limit
            params["skip"] = skip
            # params['id'] = id_string

            obj_http = cdc_env_http.EnvironmentHttp()

            # make the API call
            users_result = obj_http.get(
                api_url, headers=headers, timeout=REQUEST_TIMEOUT, params=params
            )

            return users_result
