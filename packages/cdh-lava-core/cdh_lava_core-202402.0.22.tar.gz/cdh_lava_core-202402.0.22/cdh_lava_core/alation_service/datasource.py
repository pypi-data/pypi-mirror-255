import os
import sys
import json
import requests
from pandas import json_normalize

from cdh_lava_core.cdc_log_service.environment_logging import LoggerSingleton

from cdh_lava_core.cdc_tech_environment_service import environment_http as cdc_env_http

# Get the currently running file name
NAMESPACE_NAME = os.path.basename(os.path.dirname(__file__))
# Get the parent folder name of the running file
SERVICE_NAME = os.path.basename(__file__)
# Default request timout
REQUEST_TIMEOUT = 45


class DataSource:
    """
    A base class for interacting with Alation DataSource.
    """

    @staticmethod
    def fetch_datasource(edc_alation_api_token, edc_alation_base_url, datasource_id):
        """
        Fetches a specific datasource's details from an Alation instance using the given datasource ID.
        The method communicates with the Alation API using v1 (as v2 returns a 404 for this operation)
        to retrieve the datasource and performs various error checks to handle different response scenarios.

        Args:
            edc_alation_api_token (str): The API token used for authentication with the Alation instance.
            edc_alation_base_url (str): The base URL for the Alation instance.
            datasource_id (int): The unique ID representing the specific Alation datasource to fetch.

        Returns:
            response (requests.Response): A Response object containing the retrieved datasource details.
            Use the `.json()` method on the response to parse the data as JSON.

        Raises:
            HTTPError: If an HTTP error occurred during the request.
            ConnectionError: If a connection error occurred during the request.
            Timeout: If a timeout error occurred during the request.
            RequestException: For general request exceptions.
            ValueError: If the response status code is neither 200 nor 201.
            Exception: Any other unexpected exception encountered during the request.
        """

        tracer, logger = LoggerSingleton.instance(
            NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
        ).initialize_logging_and_tracing()
        logger.info(f"running_local:{running_local}")

        with tracer.start_as_current_span("fetch_datasource"):
            try:
                # Must use v1 of the API - v2 returns a 404
                api_url = f"{edc_alation_base_url}/integration/v1/datasource/{str(datasource_id)}/"

                # Set the headers for the API request
                headers = {"accept": "application/json", "Token": edc_alation_api_token}
                # Intentionally not set
                response_datasource_text = "not_set"

                # Log Parameters
                logger.info(f"api_url: {api_url}")

                # Make the API request
                obj_http = cdc_env_http.EnvironmentHttp()
                response_datasource = obj_http.get(
                    api_url, headers=headers, timeout=REQUEST_TIMEOUT, params=None
                )

                # Check the status code
                if response_datasource.status_code != 200:
                    # Raise an exception if the status code is not 200 (OK)
                    response_datasource.raise_for_status()

                # Check the response status code to determine if successful
                if response_datasource.status_code in (200, 201):
                    response_datasource_text = response_datasource.text
                    response_datasource_json = response_datasource.json()
                    datasource_title = response_datasource_json.get("title")
                    logger.info(f"datasource: {str(datasource_title)}")
                    return response_datasource
                else:
                    response_datasource_text = response_datasource.reason
                    raise ValueError(
                        "Failed to get Datasource :" + str(response_datasource_text)
                    )

            except requests.HTTPError as err:
                error_msg = f"HTTP Error occurred: {err}"
                exc_info = sys.exc_info()
                LoggerSingleton.instance(
                    NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
                ).error_with_exception(error_msg, exc_info)
                raise
            except requests.ConnectionError as err:
                error_msg = f"Connection Error occurred: {err}"
                exc_info = sys.exc_info()
                LoggerSingleton.instance(
                    NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
                ).error_with_exception(error_msg, exc_info)
                raise
            except requests.Timeout as err:
                error_msg = f"Timeout Error occurred: {err}"
                exc_info = sys.exc_info()
                LoggerSingleton.instance(
                    NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
                ).error_with_exception(error_msg, exc_info)
                raise
            except requests.RequestException as err:
                error_msg = f"An error occurred: {err}"
                exc_info = sys.exc_info()
                LoggerSingleton.instance(
                    NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
                ).error_with_exception(error_msg, exc_info)
                raise
            except Exception as ex:
                error_msg = "Error: %s", ex
                exc_info = sys.exc_info()
                LoggerSingleton.instance(
                    NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
                ).error_with_exception(error_msg, exc_info)
                raise

    @staticmethod
    def fetch_datasources(
        edc_alation_api_token, edc_alation_base_url, alation_datasource_id
    ):
        """
        Retrieves the list of datasources from an Alation instance for a specified table. This method communicates
        with the Alation API, fetches the datasources, and processes them to promote certain custom fields to the
        datasource level and to merge Steward information.

        Args:
            edc_alation_api_token (str): The API token used for authentication with the Alation instance.
            edc_alation_base_url (str): The base URL for the Alation instance.
            alation_datasource_id (int): The unique ID representing a specific Alation data source.

        Returns:
            DataFrame: A dataframe containing the datasources for the specified table. Each datasource
            is represented as a row in the dataframe with attributes as columns.

        Raises:
            Exception: Any exception encountered during the fetching and processing of the datasources.
        """

        tracer, logger = LoggerSingleton.instance(
            NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
        ).initialize_logging_and_tracing()

        with tracer.start_as_current_span("fetch_datasources"):
            datasource_to_process = {}

            try:
                collection_set_results = None

                if collection_set_results is not None:
                    message = "Add collection set results to datasource_to_process"
                    logger.info(message)

                # Set the headers for the API request
                headers = {"accept": "application/json"}
                headers["Token"] = edc_alation_api_token

                total_records = 100000
                limit = 250
                offset = 0

                merged_data = []  # Initialize an empty list to store JSON responses

                for offset in range(0, total_records, limit):
                    # Set the parameters for the API request
                    params = {}
                    params["limit"] = limit
                    params["skip"] = str(offset)

                    if alation_datasource_id != -1:
                        params["ds_id"] = alation_datasource_id

                    # Create the API URL
                    api_url = f"{edc_alation_base_url}/integration/v1/datasource/"

                    # Log Parameters
                    logger.info(f"api_url: {api_url}")
                    logger.info(f"params: {str(params)}")

                    # Make the API request
                    obj_http = cdc_env_http.EnvironmentHttp()
                    response_datasources = obj_http.get(
                        api_url, headers=headers, params=params, timeout=REQUEST_TIMEOUT
                    )

                    # Check the status code
                    if response_datasources.status_code != 200:
                        # Raise an exception if the status code is not 200 (OK)
                        response_datasources.raise_for_status()

                    response_datasources_json = response_datasources.json()

                    # Append the response to the merged_data list
                    merged_data.extend(response_datasources_json)

                    # when there are no more datasources all have been processed so break out of the loop
                    if len(response_datasources_json) == 0:
                        break

                    # Convert the merged data list to a single JSON string
                    merged_json_string = json.dumps(merged_data)
                    merged_data_json = json.loads(merged_json_string)

                    # Convert to dataframe
                    df_datasources = json_normalize(merged_data_json)

                    return df_datasources

            except Exception as ex:
                error_msg = "Error: %s: %s", ex, str(datasource_to_process)
                exc_info = sys.exc_info()
                LoggerSingleton.instance(
                    NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
                ).error_with_exception(error_msg, exc_info)
                raise

    @classmethod
    def check_datasource(
        cls,
        edc_alation_api_token,
        edc_alation_base_url,
        alation_datasource_id,
        alation_datasource_name,
    ):
        """
        Checks the given data source against the Alation API.

        Args:
            akatibn_datasource_name (str): The name of the data source to be checked.
            alation_datasource_id (int): The ID of the data source in Alation.
            alation_headers (dict): The headers to be used for Alation API requests. These should include authentication information.
            edc_alation_base_url (str): The base URL of the Alation instance.

        Returns:
            str: A status message indicating whether the data source was found or not. This could potentially be extended to return more detailed information.

        Raises:
            Exception: If there is an error in the API request, such as invalid authentication, an exception will be raised.

        Note:
            This function is designed to interact with the Alation API. Please ensure that all necessary access permissions and API credentials are correctly set up before using this function.
        """

        tracer, logger = LoggerSingleton.instance(
            NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
        ).initialize_logging_and_tracing()
        logger.info(f"running_local:{running_local}")

        with tracer.start_as_current_span("check_datasource"):
            try:
                # Must use v1 of the API - v2 returns a 404
                api_url = f"{edc_alation_base_url}/integration/v1/datasource/{str(alation_datasource_id)}/"

                headers = {"accept": "application/json"}
                headers["Token"] = edc_alation_api_token

                # Set the headers for the API request
                headers = {"accept": "application/json"}
                # Intentionally not set
                # headers["Token"] = edc_alation_api_token

                alation_datasource_name = str(alation_datasource_name)
                alation_datasource_name = alation_datasource_name.lower()
                # service_account_authentication for this datasource
                logger.info("Checking data source %s", alation_datasource_name)
                logger.info("API URL: %s", api_url)
                response_datasource = cls.fetch_datasource(
                    edc_alation_api_token, edc_alation_base_url, alation_datasource_id
                )
                logger.info(f"Response: {str(response_datasource)}")
                print(f"Type of response: {type(response_datasource)}")
                response_datasource_json = response_datasource.json()
                ds_title = response_datasource_json.get("title", "")
                ds_title = ds_title.lower()
                message = f"Found correct data source {ds_title}"
                logger.info(message)

                if alation_datasource_name not in ds_title:
                    message = f"Data source {alation_datasource_name} not found in {ds_title} from {api_url}"
                    raise ValueError(message)

                return response_datasource
            except Exception as ex:
                error_msg = "Error: %s", ex
                exc_info = sys.exc_info()
                LoggerSingleton.instance(
                    NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
                ).error_with_exception(error_msg, exc_info)
                raise

    @staticmethod
    def update_datasource(
        edc_alation_api_token,
        edc_alation_base_url,
        alation_datasource_id,
        datasource_title,
        datasource_description,
    ):
        tracer, logger = LoggerSingleton.instance(
            NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
        ).initialize_logging_and_tracing()

        with tracer.start_as_current_span("update_datasource"):
            try:
                # Must use v1 of the API - v2 returns a 404
                api_url = f"{edc_alation_base_url}/integration/v2/datasource/{str(alation_datasource_id)}"

                # Set the headers for the API request
                headers = {
                    "accept": "application/json",
                    "content-type": "application/json",
                    "Token": edc_alation_api_token,
                }
                # Intentionally not set
                response_datasource_text = "not_set"

                payload = {
                    "title": datasource_title,
                    "description": datasource_description,
                }

                # Log Parameters
                logger.info(f"api_url: {api_url}")

                # Make the API request

                response_datasource = requests.put(
                    api_url, headers=headers, timeout=REQUEST_TIMEOUT, json=payload
                )

                # Raise an exception if the response status code is not 200 or 201
                response_datasource.raise_for_status()

                # Check the response status code to determine if successful
                if response_datasource.status_code in (200, 201):
                    response_datasource_text = response_datasource.text
                    response_datasource_json = response_datasource.json()
                    datasource_title = response_datasource_json.get("title")
                    logger.info(f"datasource: {str(datasource_title)}")
                    return response_datasource
                else:
                    response_datasource_text = response_datasource.reason
                    raise ValueError(
                        "Failed to get Datasource :" + str(response_datasource_text)
                    )

            except requests.HTTPError as err:
                error_msg = f"HTTP Error occurred: {err}"
                exc_info = sys.exc_info()
                LoggerSingleton.instance(
                    NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
                ).error_with_exception(error_msg, exc_info)
                raise
            except requests.ConnectionError as err:
                error_msg = f"Connection Error occurred: {err}"
                exc_info = sys.exc_info()
                LoggerSingleton.instance(
                    NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
                ).error_with_exception(error_msg, exc_info)
                raise
            except requests.Timeout as err:
                error_msg = f"Timeout Error occurred: {err}"
                exc_info = sys.exc_info()
                LoggerSingleton.instance(
                    NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
                ).error_with_exception(error_msg, exc_info)
                raise
            except requests.RequestException as err:
                error_msg = f"An error occurred: {err}"
                exc_info = sys.exc_info()
                LoggerSingleton.instance(
                    NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
                ).error_with_exception(error_msg, exc_info)
                raise
            except Exception as ex:
                error_msg = "Error: %s", ex
                exc_info = sys.exc_info()
                LoggerSingleton.instance(
                    NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
                ).error_with_exception(error_msg, exc_info)
                raise

    @staticmethod
    def fetch_datasource_schemas(
        alation_headers, edc_alation_base_url, alation_datasource_id
    ):
        """
        Retrieves the schemas for a given data source from the Alation API.

        Args:
            alation_headers (dict): The headers to be used for Alation API requests. These should include authentication information.
            edc_alation_base_url (str): The base URL of the Alation instance.
            alation_datasource_id (int): The ID of the data source in Alation for which the schemas are to be fetched.

        Returns:
            list: A list of schemas associated with the provided data source. Each schema is represented as a dictionary.

        Raises:
            Exception: If there is an error in the API request, such as invalid authentication, an exception will be raised.

        Note:
            This function is designed to interact with the Alation API. Please ensure that all necessary access permissions and API credentials are correctly set up before using this function.
            This function uses a limit of 100 and a skip of 0 for pagination with the Alation API.
        """

        tracer, logger = LoggerSingleton.instance(
            NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
        ).initialize_logging_and_tracing()

        with tracer.start_as_current_span("fetch_datasource_schemas"):
            try:
                ds_id = alation_datasource_id
                # Create a connection to Alation
                print(f"alation_headers:{alation_headers}")
                print(f"alation_datasource_id: {alation_datasource_id}")
                print(f"edc_alation_base_url: {edc_alation_base_url}")
                # Pl. Update DS Server ID with the DS Server Id you have created
                # Pl. Update limit and Skip
                limit = 100
                skip = 0
                params = {}
                params["ds_id"] = ds_id
                params["limit"] = limit
                params["skip"] = skip
                params_json = json.dumps(params)
                api_url = f"{edc_alation_base_url}/integration/v2/schema/"
                print(f"api_url:{api_url}")
                # Get the schemas for the datasource
                response = requests.get(api_url, headers=alation_headers, params=params)
                schemas = json.loads(response.text)

                # Close the connection to Alation
                response.close()

                return schemas
            except Exception as ex:
                error_msg = "Error: %s", ex
                exc_info = sys.exc_info()
                LoggerSingleton.instance(
                    NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
                ).error_with_exception(error_msg, exc_info)
                raise
