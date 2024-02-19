# Standard core library imports
import os
import sys

# Standard library imports
import json
import re
import math

# Third-party imports
import requests
import pandas as pd

# Local application/library specific imports
from cdh_lava_core.cdc_log_service.environment_logging import LoggerSingleton
from cdh_lava_core.cdc_tech_environment_service import environment_http as cdc_env_http

# Constants
# Get the currently running file name
NAMESPACE_NAME = os.path.basename(os.path.dirname(__file__))
# Get the parent folder name of the running file
SERVICE_NAME = os.path.basename(__file__)
# Default limit item number of items to retrieve
LIMIT = 500
REQUEST_TIMEOUT = 60


class EdcAlationError(Exception):
    """
    This class is a custom exception class for handling errors related to EdcAlation.

    It inherits from the built-in Exception class in Python and extends it by providing a custom message.

    Attributes
    ----------
    message : str
        The error message to be displayed when the exception is raised.

    Methods
    -------
    __init__(self, message):
        Constructs a new 'EdcAlationError' object.

    Parameters
    ----------
    message : str
        The error message to be displayed when the exception is raised.
    """

    def __init__(self, message):
        """
        Constructs a new 'EdcAlationError' object.

        Parameters
        ----------
        message : str
            The error message to be displayed when the exception is raised.
        """
        self.message = message
        super().__init__(message)


class CustomFields:
    """
    A class for interacting with the bulk metadata upload from the Alation API.
    """

    def __init__(self):
        """
        Initializes an instance of the CustomFields class.
        """
        self.updates = []

    def format_fields(self, obj):
        """Format the fields of an object as name-value pairs.

        Args:
            obj: The object whose fields will be formatted.

        Returns:
            str: A formatted string containing the name, type, and value of each field.

        This function takes an object 'obj' and retrieves its fields using the 'vars' function.
        It then iterates over each field, extracting the field name, type, and value. The
        extracted information is formatted into a string of the form:
        "name (type): value", and all field strings are collected in a list.

        Finally, the function joins the field strings using newline characters and returns
        the resulting formatted string.

        If a TypeError occurs during the field retrieval process, the function returns
        a string indicating the type and value of the object itself.

        Note: This function assumes that the object 'obj' has public fields accessible
        using the 'vars' function and that the fields can be reliably converted to strings.
        """

        try:
            fields = vars(obj)
            field_strings = []

            for name, value in fields.items():
                field_type = type(value).__name__
                field_value = str(value)
                field_string = f"{name} ({field_type}): {field_value}"
                field_strings.append(field_string)

            return "\n".join(field_strings)

        except TypeError:
            return f"Variable of type {type(obj).__name__} with value: {obj}"

    def has_special_chars(self, string):
        """Check if a string contains any special characters.

        Args:
            string (str): The string to be checked.

        Returns:
            bool: True if the string contains at least one special character,
                False otherwise.

        The function uses a regular expression pattern to match any character that
        isn't alphanumeric, a dot, or an underscore. It then searches for a match
        of the pattern in the string using re.search. If a match is found, it
        indicates the presence of a special character, and the function returns
        True. Otherwise, it returns False.
        """
        pattern = r"[^a-zA-Z0-9._]"
        # re.search returns a match object if the pattern is found in the string, and None otherwise
        match = re.search(pattern, string)
        return match is not None

    def get_alation_data(self, fields):
        """
        Returns a dictionary with 'title' and 'description' fields of the provided object.

        Args:
            fields (Column, Table): An instance of either Column or Table class.

        Returns:
            dict: A dictionary with 'title' and 'description' of the provided fields object.
            If 'title' or 'description' is None, it is not included in the dictionary.
            If both are None, an empty dictionary is returned.
        """

        from .db_table import Table
        from .db_column import Column

        if isinstance(fields, (Column, Table)):
            return {
                k: v
                for k, v in {
                    "title": fields.title,
                    "description": fields.description,
                }.items()
                if v is not None
            }
        elif isinstance(fields, dict):
            return fields
        else:
            msg = self.format_fields(fields)
            error_msg = f"fields {msg} should be an instance of Column or Table"
            raise EdcAlationError(error_msg)

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
        components = key.split(".")

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
            parameters["schema_name"] = schema_name
        if table_name:
            parameters["table_name"] = table_name
        if column:
            parameters["name"] = column
        parameters["limit"] = LIMIT

        return parameters

    def get_custom_fields(
        self,
        edc_alation_api_token,
        edc_alation_base_url,
        data_product_id: str,
        environment: str,
    ):
        """
        Retrieves data from a specified API endpoint.

        Args:
            edc_alation_api_token (str): The API token for authentication.
            edc_alation_base_url (str): The base URL of the API.

        Returns:
            dict: A dictionary containing the retrieved data.

        Raises:
            EdcAlationError: If there is an error during the retrieval process.
        """

        tracer, logger = LoggerSingleton.instance(
            NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
        ).initialize_logging_and_tracing()

        with tracer.start_as_current_span("get_custom_fields"):
            try:
                params = {"limit": "1000"}

                # Create headers
                headers = {
                    "Token": edc_alation_api_token,
                    "Accept": "application/json",
                    "cache-control": "no-cache",
                }

                obj_http = cdc_env_http.EnvironmentHttp()
                metadata_endpoint = "/integration/v2"
                object_type = "custom_field"
                api_url = f"{edc_alation_base_url}{metadata_endpoint}/{object_type}"
                response_custom = obj_http.get(
                    api_url,
                    headers,
                    REQUEST_TIMEOUT,
                    params,
                    data_product_id,
                    environment,
                )

                # Check the status code
                if response_custom.status_code != 200:
                    # Raise an exception if the status code is not 200 (OK)
                    response_custom.raise_for_status()

                custom_result = response_custom.json()
                number_received = custom_result.get("number_received")
                logger.info(f"number_received: {number_received}")
                updated_objects = custom_result.get("updated_objects")
                new_objects = custom_result.get("new_objects")
                error_objects = custom_result.get("error_objects")
                if error_objects and len(error_objects) > 0:
                    error_message = ", ".join(str(e) for e in error_objects)
                    raise EdcAlationError(
                        f"Errors occurred: {error_message}: api_url {api_url} : params {params}"
                    )
                error = custom_result.get("error")
                if len(error) > 0:
                    raise EdcAlationError(
                        f"Errors occurred: {error}: api_url {api_url}  : params {params}"
                    )

                if updated_objects == 0 and new_objects == 0:
                    error_message = "No objects updated or created"
                    raise EdcAlationError(
                        f"Errors occurred: {error_message}: api_url {api_url} : params {params}"
                    )

                return custom_result

            except Exception as ex:
                error_msg = f"Error: {str(ex)}"
                exc_info = sys.exc_info()
                LoggerSingleton.instance(
                    NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
                ).error_with_exception(error_msg, exc_info)
                raise

    def get_object_by_key(
        self,
        edc_alation_api_token,
        edc_alation_base_url,
        object_type,
        alation_datasource_id,
        key,
        data_product_id,
        environment,
    ):
        """
        Retrieves data from a specified API endpoint.

        Args:
            edc_alation_api_token (str): The API token for authentication.
            edc_alation_base_url (str): The base URL of the API.
            object_type (str): The type of object to retrieve.
            alation_datasource_id (int): The ID of the data source.
            key (str): The key used for retrieval.

        Returns:
            dict: A dictionary containing the retrieved data.

        Raises:
            EdcAlationError: If there is an error during the retrieval process.
        """

        tracer, logger = LoggerSingleton.instance(
            NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
        ).initialize_logging_and_tracing()

        with tracer.start_as_current_span("get_object_by_key"):
            try:
                # Check if the alation_datasource_id is an integer
                if not isinstance(alation_datasource_id, int):
                    raise EdcAlationError("alation_datasource_id must be an integer.")

                # Remove the data source ID from the key if it exists to avoid duplicate data source ID
                key = key.replace(str(alation_datasource_id) + ".", "")

                # Add the data source ID to the key
                full_key = f"{alation_datasource_id}.{key}"

                # Check if the key contains special characters
                if self.has_special_chars(full_key):
                    logger.warning(
                        f"The following submitted key contains special characters: {str(full_key)}"
                    )

                # Create headers
                headers = {
                    "Token": edc_alation_api_token,
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                    "cache-control": "no-cache",
                }

                params = self.parse_key(full_key)
                obj_http = cdc_env_http.EnvironmentHttp()
                metadata_endpoint = "/integration/v2"
                api_url = f"{edc_alation_base_url}{metadata_endpoint}/{object_type}"
                response_custom = obj_http.get(
                    api_url,
                    headers,
                    REQUEST_TIMEOUT,
                    params,
                    data_product_id,
                    environment,
                )

                # Check the status code
                if response_custom.status_code != 200:
                    # Raise an exception if the status code is not 200 (OK)
                    response_custom.raise_for_status()

                custom_result = response_custom.json()
                number_received = custom_result.get("number_received")
                logger.info(f"number_received: {number_received}")
                updated_objects = custom_result.get("updated_objects")
                new_objects = custom_result.get("new_objects")
                error_objects = custom_result.get("error_objects")
                if error_objects and len(error_objects) > 0:
                    error_message = ", ".join(str(e) for e in error_objects)
                    raise EdcAlationError(
                        f"Errors occurred: {error_message}: api_url {api_url} : params {params}"
                    )
                error = custom_result.get("error")
                if len(error) > 0:
                    raise EdcAlationError(
                        f"Errors occurred: {error}: api_url {api_url}  : params {params}"
                    )

                if updated_objects == 0 and new_objects == 0:
                    error_message = "No objects updated or created"
                    raise EdcAlationError(
                        f"Errors occurred: {error_message}: api_url {api_url} : params {params}"
                    )

                return custom_result

            except Exception as ex:
                error_msg = f"Error: {str(ex)} : {str(key)}: {str(object_type)}"
                exc_info = sys.exc_info()
                LoggerSingleton.instance(
                    NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
                ).error_with_exception(error_msg, exc_info)
                raise

    def wrap_with_quotes(self, key):
        """
        Wraps a string key with double quotes if it is not already wrapped.

        Args:
            key (str): The string key to be wrapped.

        Returns:
            str: The key wrapped with double quotes, if it was not already wrapped.

        Example:
            >>> key1 = 'example'
            >>> key2 = '"example"'
            >>> wrapped_key1 = wrap_with_quotes(key1)
            >>> wrapped_key2 = wrap_with_quotes(key2)
            >>> print(wrapped_key1)
            "example"
            >>> print(wrapped_key2)
            "example"
        """

        if key.startswith('"') and key.endswith('"'):
            return key  # Key is already wrapped

        return f'"{key}"'  # Wrap the key with double quotes

    def encode_key_with_special_characters(self, key):
        """
        Encodes a key by replacing special characters with their corresponding escape sequences.

        Args:
            key (str): The key to be encoded.

        Returns:
            str: The encoded key.
        """
        special_characters = {
            "!": "%21",
            '"': "%22",
            "#": "%23",
            "$": "%24",
            "%": "%25",
            "&": "%26",
            "'": "%27",
            "(": "%28",
            ")": "%29",
            "*": "%2A",
            "+": "%2B",
            ",": "%2C",
            "-": "%2D",
            ".": "%2E",
            "/": "%2F",
            ":": "%3A",
            ";": "%3B",
            "<": "%3C",
            "=": "%3D",
            ">": "%3E",
            "?": "%3F",
            "@": "%40",
            "[": "%5B",
            "\\": "%5C",
            "]": "%5D",
            "^": "%5E",
            "_": "%5F",
            "`": "%60",
            "{": "%7B",
            "}": "%7D",
            "~": "%7E",
        }

        for char, escape_sequence in special_characters.items():
            key = key.replace(char, escape_sequence)

        return key

    def handle_null(self, value):
        """
        Handles null values by returning the original value if it is not None,
        otherwise returns "N/A".

        Args:
            value: The value to be handled.

        Returns:
            The original value if it is not None, otherwise "N/A".
        """
        return value if value is not None else "N/A"

    # Recursive function to replace null with empty string
    def replace_null_with_empty(self, obj):
        """
        Recursively replaces null values in a dictionary or list with "N/A".

        Args:
            obj (dict or list): The object to process.

        Returns:
            dict or list: The processed object with null values replaced by "N/A".
        """
        if isinstance(obj, dict):
            return {
                k: self.replace_null_with_empty(v) if v is not None else "N/A"
                for k, v in obj.items()
            }
        elif isinstance(obj, list):
            return [
                self.replace_null_with_empty(elem) if elem is not None else "N/A"
                for elem in obj
            ]
        return obj

    def replace_nan_with_blank(self, d):
        """
        Recursively replace NaN and None values with blank strings in a dictionary.
        """
        if d is None:
            return ""

        if isinstance(d, dict):
            for key, value in d.items():
                d[key] = self.replace_nan_with_blank(value)
        elif isinstance(d, list):
            return [self.replace_nan_with_blank(item) for item in d]
        elif isinstance(d, float) and math.isnan(d):
            return ""
        return d

    def update(
        self,
        edc_alation_api_token,
        edc_alation_base_url,
        object_type,
        alation_datasource_id,
        key,
        fields_dict,
        force_submit,
        editable_fields,
        date_fields,
        data_product_id,
        environment,
    ):
        """
        Update business metadata on an object in Alation.

        Parameters
        ----------
        edc_alation_api_token : str
            The API token for authenticating requests to the Alation API.

        edc_alation_base_url : str
            The base URL of the Alation instance.

        object_type : str
            The Alation object type which can be one of the following:
                - source
                - schema
                - table
                - attribute (aka database column)
                - attribute_value (Column values custom metadata, generally not used)

        alation_datasource_id : int
            The ID of the data source that this object belongs to.

        key : str
            The object key in Alation. See the Alation API documentation for details. The key format depends on the object type.
                - schema: <source_id>.<schema_name>
                - table: <source_id>.<schema_name>.<table_name>
                - attribute (aka database column): <source_id>.<schema_name>.<table_name>.<attribute_name>

        fields : dict
            The fields to update. It should be a dictionary containing key-value pairs representing the field names and their corresponding values.

        force_submit : bool
            Specifies whether to force the submission of updates even if the batch size is not reached.

        Raises
        ------
        EdcAlationError
            If an error occurs during the update process.
        """

        tracer, logger = LoggerSingleton.instance(
            NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
        ).initialize_logging_and_tracing()

        with tracer.start_as_current_span("update"):
            logger.info(f"date_fields: {date_fields} not yet supported")

            array_of_json = None
            try:
                batch_size = 50

                fields = {}

                # Check if the fields_dict is a Table object
                # If it is a Table object, then extract the properties (attributes) to a dictionary with key-value pairs

                from .db_table import Table
                from .db_column import Column
                
                if isinstance(fields_dict, Table):
                    # Extract properties (attributes) to a dictionary with key-value pairs
                    fields_dict = vars(fields_dict)

                # If it is a Column object, then extract the properties (attributes) to a dictionary with key-value pairs
                if isinstance(fields_dict, Column):
                    # Extract properties (attributes) to a dictionary with key-value pairs
                    fields_dict = vars(fields_dict)

                if isinstance(fields_dict, dict):
                    fields = fields_dict
                else:
                    if object_type == "attribute":
                        field_name = key.split(".")[-1]
                        if field_name in editable_fields and field_name != "key":
                            fields = {field_name: fields_dict}
                        elif field_name == "key":
                            fields = {key: fields_dict}
                        else:
                            logger.warning(
                                f"Errors occurred and cannot process object {str(field_name)} of type: {type(fields_dict)} because it is not a valid Column in editable fields {str(editable_fields)}"
                            )
                    else:
                        raise EdcAlationError(
                            f"Errors occurred and cannot process object: {key} of type: {type(fields_dict)} because it is not a valid Table, Column or Dictionary: {str(fields_dict)}"
                        )

                # If table check if the user is authorized to update the table
                # if not isinstance(alation_datasource_id, int):
                #    raise EdcAlationError(
                #        "alation_datasource_id must be an integer.")

                # Remove the datasource id from the key if it exists to avoid duplicate datasource id
                key = key.replace(str(alation_datasource_id) + ".", "")

                # object_type == 'schema' or
                # For db schema handle keys that contain special characters
                # if (object_type == 'table') and '.' in full_key:
                #    full_key = self.wrap_with_quotes(full_key)

                # Add the datasource id to the key
                full_key = f"{alation_datasource_id}.{key}"

                # Check if the key contains special characters
                if self.has_special_chars(full_key):
                    logger.warning(
                        f"The following submitted key contains special characters: {str(full_key)}"
                    )

                # Create a new dictionary with only the valid editable fields
                #  key.split(".")[-1] is field_name
                fields_to_process = {
                    key: value
                    for key, value in fields.items()
                    if key.split(".")[-1] in editable_fields
                }

                # If the fields is a dictionary, then it is ready to queue for processing
                if not isinstance(fields_to_process, dict):
                    error_msg = f"Errors occurred and cannot process object: {key} of type: {type(fields_dict)} because it is missing fields: {str(fields_dict)}"
                    raise EdcAlationError(error_msg)

                params = {"create_new": "false", "replace_values": "true"}

                # Loop through the dictionary and urlencode the values
                for key, value in fields_to_process.items():
                    # Encode keys if columns/attributes
                    if key == "key":
                        if object_type == "attribute":
                            fields_to_process[
                                key
                            ] = self.encode_key_with_special_characters(value)
                    # Default to empty string if value is None
                    if value is None:
                        value = "N/A"

                # Add the key to the fields
                single_update_init = {"key": full_key, **fields_to_process}
                logger.info(f"single_update_init: {single_update_init}")

                # Replace null values with empty strings
                single_update = self.replace_null_with_empty(single_update_init)

                # Add the update to the updates list
                # If there is a value to set in addition to key
                if len(single_update) > 1:
                    self.updates.append(single_update)

                # Submit the updates if the batch size is reached or if force_submit is True
                if len(self.updates) >= batch_size or force_submit:
                    data = ""

                    # Create json to validate
                    array_of_json = [
                        json.dumps(u, cls=EnhancedJSONEncoder, separators=(",", ":"))
                        for u in self.updates
                    ]
                    if len(array_of_json) > 1:
                        data = ",".join(array_of_json)
                        data = "[" + data + "]"
                    else:
                        data = array_of_json[0]

                    # Validate json
                    try:
                        # Parse the data to check for JSON parsing errors
                        data_json = json.loads(data)
                        logger.info(f"Successfully parsed data_json: {len(data_json)}")
                    except json.JSONDecodeError as ex:
                        error_msg = f"Error parsing data_json: {ex} : {data}"
                        logger.error(error_msg)
                        raise

                    cleaned_data = self.replace_nan_with_blank(self.updates)

                    data_str = "\n".join(
                        json.dumps(item, cls=EnhancedJSONEncoder)
                        for item in cleaned_data
                    )

                    # submit the batch
                    logger.info(f"Submitting {object_type} batch")
                    metadata_endpoint = "/api/v1/bulk_metadata/custom_fields/default"
                    api_url = f"{edc_alation_base_url}{metadata_endpoint}/{object_type}"

                    # Create headers
                    headers = {
                        "Token": edc_alation_api_token,
                        "Content-Type": "application/json",
                        "accept": "application/json",
                    }

                    # Submit the updates using the constructed URL and data
                    response = requests.post(
                        api_url,
                        headers=headers,
                        data=data_str,
                        params=params,
                        verify=True,
                        timeout=REQUEST_TIMEOUT,
                    )
                    response_json = response.json()

                    # Clear updates after submission
                    self.updates = []
                    logger.info(f"Response Status {object_type} batch of {data}")
                    response.raise_for_status()
                    result = response_json
                    number_received = result.get("number_received")
                    logger.info(f"number_received: {number_received}")
                    updated_objects = result.get("updated_objects")
                    new_objects = result.get("new_objects")
                    error_objects = result.get("error_objects")
                    if error_objects and len(error_objects) > 0:
                        error_message = ", ".join(str(e) for e in error_objects)
                        raise EdcAlationError(
                            f"Errors occurred: {error_message}: api_url {api_url} : data {data}"
                        )
                    error = result.get("error")
                    if len(error) > 0:
                        raise EdcAlationError(
                            f"Errors occurred: {error}: api_url {api_url} : data {data}"
                        )

                    if updated_objects == 0 and new_objects == 0:
                        error_message = "No objects updated or created"
                        raise EdcAlationError(
                            f"Errors occurred: {error_message}: api_url {api_url} : data {data}"
                        )

                    return {
                        "status": "success",
                        "message": "Batch complete",
                    }, response_json
                else:
                    return {"status": "success", "message": "Batch not submitted"}, {
                        "number_of_updates",
                        len(self.updates),
                        "batch_size",
                        batch_size,
                        "force_submit",
                        force_submit,
                    }

            except Exception as ex:
                error_msg = f"Error: {str(ex)} : {str(key)}: {str(fields_dict)}"
                exc_info = sys.exc_info()
                LoggerSingleton.instance(
                    NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
                ).error_with_exception(error_msg, exc_info)
                raise


class EnhancedJSONEncoder(json.JSONEncoder):
    """
    JSON Encoder subclass that allows serialization of pandas Timestamp and NaT objects.

    This encoder handles the problem where certain Python objects, like pandas Timestamps
    and NaT, are not directly serializable to JSON using the standard library's json module.
    Timestamp objects are converted to string representations, while NaT values are transformed
    into None (or any other representation you prefer).

    """

    def default(self, o):
        """
        Convert the given object to a JSON serializable format.

        Args:
            o: The object to be converted.

        Returns:
            The JSON serializable representation of the object.
        """
        if isinstance(o, pd.Timestamp):
            return o.strftime("%Y-%m-%d %H:%M:%S")
        elif pd.isna(o):  # This checks for both NaT and NaN
            return None  # or use a string like "null" or "missing"
        return super().default(o)
