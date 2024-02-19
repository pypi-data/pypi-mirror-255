"""
This module provides the Query class for fetching and processing queries from the EDC Alation API.

The module provides the following:

1. Constants for namespace name, service name, and timeouts.

2. The Query class, which provides a method `fetch_query` to fetch all the queries from an API and 
processes each query to fetch details, query text, and latest results. This method also handles 
exceptions, logs different stages of query processing, and reports if any error occurs.

The `fetch_query` method uses the Singleton design pattern to get instances of Logger and Tracer 
from the `environment_logging` and `environment_tracing` modules respectively. It also uses an 
instance of the `EnvironmentHttp` class from the `environment_http` module to make HTTP requests.

The module uses the requests library for making API requests and uses json and csv libraries for 
processing the API responses.

This module can be run as a standalone script or can be imported and used in other modules.

 
Constants:
    NAMESPACE_NAME (str): Name of the currently running file
    SERVICE_NAME (str): Name of the parent folder of the running file
    REQUEST_TIMEOUT (int): Timeout for requests in seconds
    TIMEOUT_ONE_MIN (int): Constant for a timeout of one minute in seconds
"""

import os
import sys
import json
import csv
import requests
import pandas as pd

from cdh_lava_core.cdc_log_service.environment_logging import LoggerSingleton

from cdh_lava_core.cdc_tech_environment_service import environment_http as cdc_env_http


# Get the currently running file name
NAMESPACE_NAME = os.path.basename(os.path.dirname(__file__))
# Get the parent folder name of the running file
SERVICE_NAME = os.path.basename(__file__)
REQUEST_TIMEOUT = 45
TIMEOUT_ONE_MIN = 60
LIMIT = 100  # Set the batch size


class Query:
    """
    Query class is used for fetching and processing queries.

    ...

    Attributes
    ----------
    None

    Methods
    -------
    get_query_list(edc_alation_api_token: str, edc_alation_base_url: str) -> None:
        Fetches all the queries from an API and processes each query to fetch details, query text,
        and latest results. This method also handles exceptions, logs different stages of
        query processing and reports if any error occurs.
    """

    def get_query_list(
        self,
        edc_alation_api_token,
        edc_alation_base_url,
        alation_datasource_id,
        data_product_id,
        environment,
    ):
        """
        Fetches all the queries from an API and processes each query to fetch details, query text,
        and latest results. This method also handles exceptions, logs different stages of
        query processing and reports if any error occurs.

        Parameters:
        ----------
        edc_alation_api_token : str
            API token to access the EDC Alation API.

        edc_alation_base_url : str
            The base URL for the EDC Alation API.

        Returns:
        -------
        None

        Raises:
        ------
        Exception
            If an error occurs during the process of fetching and processing the queries.
        """

        headers = {
            "Token": edc_alation_api_token,
            "Content-Type": "application/json",
            "accept": "application/json",
        }

        tracer, logger = LoggerSingleton.instance(
            NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
        ).initialize_logging_and_tracing()

        with tracer.start_as_current_span("get_query_list"):
            try:
                all_queries = []  # Initialize empty list to collect all queries
                skip = 0  # Start from the first item

                while True:  # We'll break from the loop when we fetch all data
                    logger.info("Get query list")
                    api_url = "/integration/v1/query/"
                    query_list_url = edc_alation_base_url + api_url

                    obj_http = cdc_env_http.EnvironmentHttp()
                    params = {
                        "datasource_id": alation_datasource_id,
                        "limit": LIMIT,
                        "skip": skip,
                    }
                    response_list = obj_http.get(
                        query_list_url,
                        headers=headers,
                        timeout=TIMEOUT_ONE_MIN,
                        params=params,
                    )
                    logger.info(f"query_list_url: {query_list_url}")
                    logger.info(f"query_list_params: {str(params)}")
                    queries = json.loads(response_list.text)
                    if (
                        not queries
                    ):  # If no more queries are returned, break from the loop
                        break

                    for query in queries:
                        # Append each query to the all_queries list
                        all_queries.append(query)

                    skip += LIMIT

                # Convert the list of queries to a JSON object
                response_queries_list_json = all_queries

                return response_queries_list_json

            except Exception as ex:
                error_msg = f"Error: {str(ex)}"
                exc_info = sys.exc_info()
                LoggerSingleton.instance(
                    NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
                ).error_with_exception(error_msg, exc_info)
                raise

    def get_query_results(
        self,
        edc_alation_api_token,
        edc_alation_base_url,
        alation_datasource_id,
        query_id,
        data_product_id,
        environment,
    ):
        """
        Fetches all the queries from an API and processes each query to fetch details, query text,
        and latest results. This method also handles exceptions, logs different stages of
        query processing and reports if any error occurs.

        Parameters:
        ----------
        edc_alation_api_token : str
            API token to access the EDC Alation API.

        edc_alation_base_url : str
            The base URL for the EDC Alation API.

        Returns:
        -------
        None

        Raises:
        ------
        Exception
            If an error occurs during the process of fetching and processing the queries.
        """

        headers = {
            "Token": edc_alation_api_token,
            "Content-Type": "application/json",
            "accept": "application/json",
        }

        tracer, logger = LoggerSingleton.instance(
            NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
        ).initialize_logging_and_tracing()

        with tracer.start_as_current_span("fetch_query"):
            try:
                obj_http = cdc_env_http.EnvironmentHttp()
                logger.info("##### Get all queries #####")
                api_url = "/integration/v1/query/"

                # Ensure query_id is a string
                query_id = str(query_id)
                logger.info(f"##### Get details for a single query {query_id} #####")
                query_detail_url = edc_alation_base_url + api_url + query_id

                response_detail = obj_http.get(
                    query_detail_url,
                    headers=headers,
                    timeout=TIMEOUT_ONE_MIN,
                    params=None,
                )
                query_detail = json.loads(response_detail.text)
                detail = query_detail.get("detail")
                logger.info(f"query_detail: {query_detail}")
                query_title = "not_set"
                if detail == "You do not have permission to perform this action.":
                    query_title = "No Permission"
                    logger.info(f"id: {query_id}, title: {query_title}")
                else:
                    detail_id = query_detail["id"]
                    query_title = query_detail["title"]
                    if query_title is not None:
                        query_title = query_title.replace("\n", " ")
                        logger.info(f"detail_id: {detail_id}, title: {query_title}")

                # Get query text
                api_url = f"/integration/v1/query/{query_id}/sql/"
                query_text_url = edc_alation_base_url + api_url
                logger.info(f"query_text_url:{query_text_url}")
                response_query_text = requests.get(
                    query_text_url, headers=headers, timeout=TIMEOUT_ONE_MIN
                )
                response_content_text = "not_set"
                # Check the response status code to determine if the request was
                # successful
                if response_query_text.status_code in (200, 201):
                    # Extract the API token from the response
                    response_content_text = response_query_text.content.decode("utf-8")
                    # logger.info(f"SQL Query Text response: {query_text}")
                else:
                    logger.info(
                        "Failed to get SQL Query Text :" + str(response_content_text)
                    )

                query_text = response_content_text
                query_text = query_text.replace("\n", " ").replace("'", "'")

                # Get latest result id
                api_url = f"/integration/v1/query/{query_id}/result/latest/"
                query_url = edc_alation_base_url + api_url
                logger.info(f"query_url: {query_url}")
                logger.info(f"headers length: {len(headers)}")
                # Send the request to the Alation API endpoint.
                # The endpoint for executing queries is `/integration/v1/query`.
                response_query = requests.get(
                    query_url, headers=headers, timeout=TIMEOUT_ONE_MIN
                )
                logger.info(
                    "response_query.content:" + response_query.content.decode("utf-8")
                )

                json_response = json.loads(response_query.content)
                execution_result_id = json_response["id"]

                # Get lastest results and place in dataframe
                api_url = f"/integration/v1/result/{execution_result_id}/csv/"
                result_url = edc_alation_base_url + api_url

                with requests.Session() as s:
                    response = requests.get(result_url, headers=headers)
                    decoded_content = response.content.decode("utf-8")
                    csv_reader = csv.reader(decoded_content.splitlines(), delimiter=",")

                    columns = []
                    query_data = []
                    i_record = 0
                    for row in csv_reader:
                        if i_record != 0:
                            query_data.append(row)
                        else:
                            columns = row
                            i_record = i_record + 1

                    df_query_results = pd.DataFrame(query_data)
                    df_query_results.columns = columns
                    return df_query_results

            except Exception as ex:
                error_msg = f"Error: {str(ex)}"
                exc_info = sys.exc_info()
                LoggerSingleton.instance(
                    NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
                ).error_with_exception(error_msg, exc_info)
                raise
