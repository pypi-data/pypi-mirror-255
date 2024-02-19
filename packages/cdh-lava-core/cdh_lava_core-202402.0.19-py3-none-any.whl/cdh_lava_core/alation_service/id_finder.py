"""
This module provides classes and functions for interacting with the Alation V2 API.

The `EdcAlationError` class is a custom exception for handling errors related to the Alation API.

The `IdFinder` class is a subclass of the `Endpoint` class for interacting with the Alation V2 API. It 
provides methods for parsing keys and finding the IDs of objects in Alation based on object type and name.

Functions:
    `split_outside_quotes`: Splits a string on a specified delimiter outside quotes.
    `parse_key`: Parses a key in the format 'ds_id.schema_name.table_name.column' and returns a dictionary of the non-null values.
    `find`: Finds the identifier for an object in Alation given a name and object type.

Notes:
- This module uses the `cdc_log_service` and `cdc_tech_environment_service` packages for logging and HTTP requests.
- This module requires a user with admin privileges for the Alation API.
- The Alation API may return multiple IDs for a given name and object type, in which case the `find` function will raise a ValueError.
"""

import sys
import os
import re

from cdh_lava_core.alation_service.endpoint import Endpoint
from cdh_lava_core.cdc_log_service.environment_logging import LoggerSingleton
from cdh_lava_core.cdc_tech_environment_service import environment_http as cdc_env_http

# Get the currently running file name
NAMESPACE_NAME = os.path.basename(os.path.dirname(__file__))
# Get the parent folder name of the running file
SERVICE_NAME = os.path.basename(__file__)
REQUEST_TIMEOUT = 45
LIMIT = 1000  # Limit the number of records returned by the API

# This isn't a true endpoint as it actually points to multiple URLS


class EdcAlationError(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(message)


class IdFinder(Endpoint):
    """
    A class for interacting with the Alation V2 API to find the IDs of objects by type and name.

    This is a subclass of Endpoint, so users should instantiate the class by providing an API token
    and the base URL of the Alation server to work with.

    Note that this functionality may require a user with admin priviledges.
    """

    def split_outside_quotes(self, string_to_split, delimiter):
        """
        Splits a given string by the specified delimiter, excluding portions of the string that are inside quotes.

        This method is useful when you want to split a string, but some parts of the string are enclosed in
        quotes and should be treated as a single unit even if they contain the delimiter.

        Parameters
        ----------
        string_to_split : str
            The string to be split.

        delimiter : str
            The delimiter to split the string by.

        Returns
        -------
        list
            A list of substrings, with the original string split by the delimiter, but excluding portions
            within quotes.

        Notes
        -----
        - The method takes into account escaped quotes.
        - If the delimiter is present within quotes, it will be treated as part of the quoted string, not a delimiter.
        """

        # Matches quoted strings, taking into account escaped quotes
        quote_pat = re.compile(r'"([^"\\]*(?:\\.[^"\\]*)*)"')

        # Start and end indices of quoted strings
        quotes = [m.span() for m in quote_pat.finditer(string_to_split)]

        # Starting from the end of the string, split on delimiter outside quotes
        chunks = []
        pos = len(string_to_split)
        for start, end in reversed(quotes):
            chunks.append(string_to_split[end:pos])
            pos = start
        chunks.append(string_to_split[:pos])

        # Split the chunks on delimiter and reverse back to original order
        components = [c.split(delimiter) for c in reversed(chunks)]

        # Flatten the list of lists
        components = [item for sublist in components for item in sublist]

        return components

    def parse_key(self, key):
        """
        Parse a key in the format 'ds_id.schema_name.table_name.column'
        and create a parameters dictionary for the non-null values.

        Args:
            key (str): The key to be parsed.

        Returns:
            dict: A dictionary containing the non-null values as key-value pairs.
                Possible keys: 'ds_id', 'schema_name', 'table_name', 'column'.
        """

        # Split the key into components using the dot (.) separator
        # components = key.split('.')
        # This regex splits on periods not enclosed by double quotes
        components = self.split_outside_quotes(key, ".")

        # Extract ds_id, schema_name, table_name, and column
        ds_id = components[0]
        schema_name = components[1] if len(components) >= 2 else None
        table_name = components[2] if len(components) >= 3 else None
        column = components[3] if len(components) >= 4 else None

        # Create a parameters dictionary for non-null values
        parameters = {}
        if ds_id:
            parameters["ds_id"] = ds_id
        if schema_name:
            parameters["name"] = schema_name
        if table_name:
            parameters["schema_name"] = schema_name
            parameters["name"] = table_name
        if column:
            parameters["name"] = column
        parameters["limit"] = LIMIT

        return parameters

    def find(
        self,
        object_type,
        key,
        data_product_id,
        environment,
    ):
        """
        Finds the identifier for an object in Alation given a name and object type.

        Parameters
        ----------
        object_type : str
            The Alation object type: "schema", "table" or "attribute". Note that columns are called attributes in Alation.
        name : str
            The name of the object in Alation.

        Returns
        -------
        int or None
            If the call finds a single object, it will return the ID for the object. If it can't find anything or if it finds more than one object, it will return None.
        """

        tracer, logger = LoggerSingleton.instance(
            NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
        ).initialize_logging_and_tracing()

        with tracer.start_as_current_span("find"):
            api_url = ""
            try:
                # Create headers
                headers = {"Token": self.token, "Accept": "application/json"}
                params = self.parse_key(key)
                metadata_endpoint = "/integration/v2"
                base_url = self.base_url
                api_url = f"{base_url}{metadata_endpoint}/{object_type}"
                obj_http = cdc_env_http.EnvironmentHttp()
                response = obj_http.get(
                    api_url,
                    headers,
                    REQUEST_TIMEOUT,
                    params,
                    data_product_id,
                    environment,
                )
                # Check the status code
                if response.status_code != 200:
                    # Raise an exception if the status code is not 200 (OK)
                    response.raise_for_status()
                response_json = response.json()
                if len(response_json) == 1:
                    return response_json[0]["id"]
                else:
                    raise ValueError(
                        f"Found  {len(response_json)} ids for object_type: {object_type} key: {key}"
                    )

            except Exception as ex:
                error_msg = f"Error: {str(ex)}"
                exc_info = sys.exc_info()
                LoggerSingleton.instance(
                    NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
                ).error_with_exception(error_msg, exc_info)
                raise
