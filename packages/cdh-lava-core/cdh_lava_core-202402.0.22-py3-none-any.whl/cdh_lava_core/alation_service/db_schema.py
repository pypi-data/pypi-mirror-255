import requests
import json
import os
import sys
import concurrent.futures
import platform
import datetime
from cdh_lava_core.alation_service.db_table import Table
from cdh_lava_core.alation_service.token import TokenEndpoint
from cdh_lava_core.alation_service.custom_fields import CustomFields
from cdh_lava_core.alation_service.tags import Tags
from cdh_lava_core.alation_service.id_finder import IdFinder
from cdh_lava_core.alation_service.datasource import DataSource
from cdh_lava_core.alation_service.json_manifest import ManifestJson
from cdh_lava_core.alation_service.excel_manifest import ManifestExcel

import pandas as pd

from cdh_lava_core.cdc_log_service.environment_logging import LoggerSingleton

from cdh_lava_core.cdc_tech_environment_service import (
    environment_file as cdc_env_file,
    environment_http as cdc_env_http,
)


# Get the currently running file name
NAMESPACE_NAME = os.path.basename(os.path.dirname(__file__))
# Get the parent folder name of the running file
SERVICE_NAME = os.path.basename(__file__)
TIMEOUT_ONE_MIN = 60  # or set to whatever value you want
REQUEST_TIMEOUT = 45

# We have implementing batching and multithreading
# Because average calls before force_submit is milliseconds
# Multi-threading is not really helping much at all
# So set to lower number 4
if platform.system() != "Windows":
    NUM_THREADS_MAX = 4
else:
    NUM_THREADS_MAX = 4

ENCODE_PERIOD = False


class EdcAlationError(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(message)


class Schema:
    """
    A base class for interacting with Alation Schema.
    """

    @staticmethod
    def fetch_schema(
        edc_alation_api_token,
        edc_alation_base_url,
        alation_schema_id,
        data_product_id,
        environment,
    ):
        """
        Retrieves details for a specific schema from Alation using the provided schema ID.

        Args:
            edc_alation_api_token (str): Headers to be used in the request, typically including authentication information.
            edc_alation_base_url (str): The base URL of the Alation instance.
            alation_schema_id (int): ID of the Alation schema to retrieve.

        Returns:
            dict: A dictionary containing details of the schema.
        """

        tracer, logger = LoggerSingleton.instance(
            NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
        ).initialize_logging_and_tracing()

        with tracer.start_as_current_span("fetch_schema_" + str(alation_schema_id)):
            try:
                # Log the parameters
                logger.info(
                    "edc_alation_api_token length: %s",
                    str(len(edc_alation_api_token)),
                )
                logger.info("alation_schema_id: %s", str(alation_schema_id))
                logger.info("edc_alation_base_url: %s", str(edc_alation_base_url))
                schema_id = alation_schema_id

                # Set the headers for the request
                headers = {
                    "accept": "application/json",
                    "Token": edc_alation_api_token,
                }

                # Set the default values for the limit and skip parameters
                limit = 100
                skip = 0

                # Create a dictionary to hold the parameters
                params = {}
                params["limit"] = limit
                params["skip"] = skip
                params["id"] = schema_id
                api_url = f"{edc_alation_base_url}/integration/v2/schema/"
                logger.info(f"api_url: {api_url}")
                logger.info(f"params: {str(params)}")
                # Make the schema request to Alation
                obj_http = cdc_env_http.EnvironmentHttp()
                response_schema = obj_http.get(
                    api_url,
                    headers=headers,
                    params=params,
                    timeout=REQUEST_TIMEOUT,
                )
                response_schema_json = response_schema.json()

                # Check the response status code to determine if successful
                if len(response_schema_json) == 1:
                    schema_result = response_schema_json[0]

                    response_schema_text = "not_set"
                    datasource_id = -1
                    if "title" in schema_result:
                        datasource_id = schema_result.get("ds_id")
                        cdh_datasource = DataSource()
                        response_datasource = cdh_datasource.fetch_datasource(
                            edc_alation_api_token,
                            edc_alation_base_url,
                            datasource_id,
                        )
                        datasource_result = response_datasource.json()
                        return response_schema, datasource_result
                    else:
                        response_schema_text = schema_result.get("reason")
                        error_msg = "Failed to get schema:" + str(response_schema_text)
                        error_msg = error_msg + " for api_url: " + str(api_url)
                        error_msg = error_msg + " for schema_id: " + str(schema_id)
                        error_msg = (
                            error_msg + " and datasource_id: " + str(datasource_id)
                        )
                        error_msg = (
                            error_msg + " and schema_result: " + str(schema_result)
                        )
                        logger.error(error_msg)
                        raise EdcAlationError(error_msg)
                else:
                    error_msg = "Failed to get schema_result"
                    raise EdcAlationError(error_msg)
            except Exception as ex:
                error_msg = "Error: %s", ex
                exc_info = sys.exc_info()
                LoggerSingleton.instance(
                    NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
                ).error_with_exception(error_msg, exc_info)
                raise

    @staticmethod
    def get_excel_manifest_file_path_temp(
        upload_or_download,
        repository_path,
        environment,
        alation_user_id,
        data_product_id,
    ):
        """
        Constructs a temporary path for an Excel manifest file based on various parameters and the current date/time.

        Args:
            upload_or_download (str): Denotes whether the action is an 'upload' or 'download'.
            repository_path (str): The path to the directory where the Excel manifest file will be stored.
            environment (str): Specifies the environment under which the file is being managed.
            alation_user_id (str): Unique identifier of an Alation user.

        Returns:
            str: The full path to the temporary Excel manifest file.

        Raises:
            Exception: If an error occurs during the construction of the Excel file path.
        """

        tracer, logger = LoggerSingleton.instance(
            NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
        ).initialize_logging_and_tracing()

        with tracer.start_as_current_span("get_excel_manifest_file_path_temp"):
            try:
                # Get current time
                current_date = datetime.datetime.now()

                yyyy_string = current_date.year
                mm_string = current_date.month
                dd_string = current_date.day
                # Format as a 24-hour time string
                time_str = current_date.strftime("%H_%M_%S")

                datasource_title = "temp"
                schema_name = "manifest"

                obj_file = cdc_env_file.EnvironmentFile()

                file_name = (
                    obj_file.scrub_file_name(datasource_title)
                    + "_"
                    + obj_file.scrub_file_name(schema_name)
                    + str(yyyy_string)
                    + "_"
                    + str(mm_string)
                    + "_"
                    + str(dd_string)
                    + "_"
                    + str(time_str)
                    + "_"
                    + str(alation_user_id)
                    + "_"
                    + upload_or_download
                    + ".xlsx"
                )

                right_most_150_chars = file_name[-80:]
                file_name = right_most_150_chars

                manifest_path = (
                    repository_path
                    + "/"
                    + environment
                    + "_manifest"
                    + "_"
                    + upload_or_download
                    + "s"
                    + "/"
                )
                manifest_path = obj_file.convert_to_current_os_dir(manifest_path)
                logger.info("manifest_path: " + manifest_path)

                manifest_excel_file = manifest_path + file_name
                logger.info("manifest_excel_file: " + manifest_excel_file)

                return manifest_excel_file
            except Exception as ex:
                # Corrected error message formatting
                error_msg = f"Excel Error: {str(ex)}"
                exc_info = sys.exc_info()
                LoggerSingleton.instance(
                    NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
                ).error_with_exception(error_msg, exc_info)
                raise

    @staticmethod
    def get_excel_manifest_file_path(
        upload_or_download,
        repository_path,
        datasource_title,
        schema_name,
        environment,
        alation_user_id,
        data_product_id,
    ):
        """_summary_

        Args:
            upload_or_download (_type_): _description_
            yyyy (_type_): _description_
            mm (_type_): _description_
            dd (_type_): _description_
            repository_path (_type_): _description_
            datasource_title (_type_): _description_
            schema_name (_type_): _description_
            environment (_type_): _description_
        """

        tracer, logger = LoggerSingleton.instance(
            NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
        ).initialize_logging_and_tracing()

        with tracer.start_as_current_span("get_excel_manifest_file_path"):
            try:
                # Get current time
                current_date = datetime.datetime.now()

                yyyy_string = current_date.year
                mm_string = current_date.month
                dd_string = current_date.day
                # Format as a 24-hour time string
                time_str = current_date.strftime("%H_%M_%S")

                if (
                    schema_name == "object_name_is_missing"
                    or schema_name == "object name is missing"
                ):
                    raise ValueError("Invalid schema_name value.")

                obj_file = cdc_env_file.EnvironmentFile()

                file_name = (
                    obj_file.scrub_file_name(datasource_title)
                    + "_"
                    + obj_file.scrub_file_name(schema_name)
                    + str(yyyy_string)
                    + "_"
                    + str(mm_string)
                    + "_"
                    + str(dd_string)
                    + "_"
                    + str(time_str)
                    + "_"
                    + str(alation_user_id)
                    + "_"
                    + upload_or_download
                    + ".xlsx"
                )

                right_most_150_chars = file_name[-80:]
                file_name = right_most_150_chars

                manifest_path = (
                    repository_path
                    + "/"
                    + environment
                    + "_manifest"
                    + "_"
                    + upload_or_download
                    + "s"
                    + "/"
                )
                manifest_path = obj_file.convert_to_current_os_dir(manifest_path)
                logger.info("manifest_path: " + manifest_path)

                manifest_excel_file = manifest_path + file_name
                logger.info("manifest_excel_file: " + manifest_excel_file)

                return manifest_excel_file
            except Exception as ex:
                # Corrected error message formatting
                error_msg = f"Excel Error: {str(ex)}"
                exc_info = sys.exc_info()
                LoggerSingleton.instance(
                    NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
                ).error_with_exception(error_msg, exc_info)
                raise

    @staticmethod
    def get_json_manifest_file_path(
        upload_or_download,
        repository_path,
        datasource_title,
        schema_name,
        environment,
        alation_user_id,
        data_product_id,
    ):
        """Get the file name for the manifest JSON file.

        Args:
            upload_or_download (str): The type of operation, whether "upload" or "download".
            repository_path (str): The path to the repository.
            datasource_title (str): The title of the data source.
            schema_name (str): The name of the schema.
            environment (str): The environment name.
            alation_user_id (str): The ID of the Alation user.

        Returns:
            str: The file name for the manifest JSON file.
        """

        tracer, logger = LoggerSingleton.instance(
            NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
        ).initialize_logging_and_tracing()

        with tracer.start_as_current_span("get_json_manifest_file_path"):
            try:
                # Get current time
                current_date = datetime.datetime.now()

                yyyy_string = current_date.year
                mm_string = current_date.month
                dd_string = current_date.day
                # Format as a 24-hour time string
                time_str = current_date.strftime("%H_%M_%S")

                if (
                    schema_name == "object_name_is_missing"
                    or schema_name == "object name is missing"
                ):
                    raise ValueError("Invalid schema_name value.")

                obj_file = cdc_env_file.EnvironmentFile()

                manifest_path = (
                    repository_path
                    + "/"
                    + environment
                    + "_manifest"
                    + "_"
                    + upload_or_download
                    + "s"
                    + "/"
                )

                logger.info("manifest_path: " + manifest_path)

                file_name = (
                    obj_file.scrub_file_name(datasource_title)
                    + "_"
                    + obj_file.scrub_file_name(schema_name)
                    + str(yyyy_string)
                    + "_"
                    + str(mm_string)
                    + "_"
                    + str(dd_string)
                    + "_"
                    + str(time_str)
                    + "_"
                    + str(alation_user_id)
                    + "_"
                    + upload_or_download
                    + ".json"
                )

                right_most_150_chars = file_name[-80:]
                file_name = right_most_150_chars

                manifest_path = obj_file.convert_to_current_os_dir(manifest_path)
                manifest_file = manifest_path + file_name

                logger.info(f"manifest_file: {manifest_file}")

                return manifest_file
            except Exception as ex:
                error_msg = "Error: %s", ex
                exc_info = sys.exc_info()
                LoggerSingleton.instance(
                    NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
                ).error_with_exception(error_msg, exc_info)
                raise

    @staticmethod
    def get_json_data_definition_file_path(
        repository_path, environment, data_product_id
    ):
        """
        Get the file path for the 'manifest.schema.json' file associated with the specified environment.

        This method constructs the file path for the 'manifest.schema.json' file based on the provided
        repository_path and environment. The file is expected to be located in the schema directory of the specified environment.

        Args:
            repository_path (str): The path to the repository containing the schema directories.
            environment (str): The name of the environment to which the schema belongs.

        Returns:
            str: The file path for the 'manifest.schema.json' file.

        Raises:
            Exception: If any error occurs during the file path construction.

        Note:
            This method assumes that the 'manifest.schema.json' file is located within the schema directory
            of the specified environment.

        Example:
            repository_path = '/path/to/repository'
            environment = 'dev'
            json_data_definition_file_path = get_json_data_definition_file_path(repository_path, environment)
            print(json_data_definition_file_path)
            # Output: '/path/to/repository/dev_data_definitions/manifest.schema.json'
        """

        tracer, logger = LoggerSingleton.instance(
            NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
        ).initialize_logging_and_tracing()

        with tracer.start_as_current_span("get_json_data_definition_file_path"):
            try:
                obj_file = cdc_env_file.EnvironmentFile()
                data_definition_path = (
                    repository_path + "/" + environment + "_data_definitions"
                )
                logger.info("data_definition_path: " + data_definition_path)
                file_name = "manifest.schema.json"

                data_definition_path = obj_file.convert_to_current_os_dir(
                    data_definition_path
                )

                # Join the directory path with the filename
                json_data_definition_file_path = os.path.join(
                    data_definition_path, file_name
                )

                logger.info(
                    f"json_data_definition_file_path: {json_data_definition_file_path}"
                )

                return json_data_definition_file_path

            except Exception as ex:
                error_msg = "Error: %s", ex
                exc_info = sys.exc_info()
                LoggerSingleton.instance(
                    NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
                ).error_with_exception(error_msg, exc_info)
                raise

    @staticmethod
    def get_excel_data_definition_file_path(repository_path, environment):
        """
        Get the file path for the 'get_excel_data_definition_file_path.xlsx' file associated with the specified environment.

        This method constructs the file path for the 'excel_data_definitionsx' file based on the provided
        repository_path and environment. The file is expected to be located in the schema directory of the specified environment.

        Args:
            repository_path (str): The path to the repository containing the schema directories.
            environment (str): The name of the environment to which the schema belongs.

        Returns:
            str: The file path for the 'excel_data_definition_for_tables_sql.xlsx' file.

        Raises:
            Exception: If any error occurs during the file path construction.

        Note:
            This method assumes that the 'excel_data_definition_for_tables_sql.xlsx' file is located within the schema directory
            of the specified environment.

        Example:
            repository_path = '/path/to/repository'
            environment = 'dev'
            excel_data_definition_file_path = get_excel_data_definition_file_path(repository_path, environment)
            print(excel_data_definition_file_path)
            # Output: '/path/to/repository/dev_data_definitions/excel_data_definition_for_tables_sql.xlsx'
        """

        tracer, logger = LoggerSingleton.instance(
            NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
        ).initialize_logging_and_tracing()

        with tracer.start_as_current_span("get_excel_data_definition_file_path"):
            try:
                obj_file = cdc_env_file.EnvironmentFile()
                data_definition_path = (
                    repository_path + "/" + environment + "_data_definitions"
                )

                data_definition_path = obj_file.convert_to_current_os_dir(
                    data_definition_path
                )

                logger.info("data_definition_path: " + data_definition_path)
                data_definition_xls_file = "excel_data_definition_for_tables_sql.xlsx"

                # Join the directory path with the filename
                excel_data_definition_file_path = os.path.join(
                    data_definition_path, data_definition_xls_file
                )

                logger.info(
                    f"excel_data_definition_file_path: {excel_data_definition_file_path}"
                )

                return excel_data_definition_file_path
            except Exception as ex:
                error_msg = "Error: %s", ex
                exc_info = sys.exc_info()
                LoggerSingleton.instance(
                    NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
                ).error_with_exception(error_msg, exc_info)
                raise

    @classmethod
    def download_manifest_excel(
        cls, alation_schema_id, config, json_data_definition_file_path, data_product_id
    ):
        """
        Downloads the schema manifest Excel file for a given Alation schema ID.

        This method generates the Excel file data using the `generate_excel_file_data` method of the
        `alation_manifest_excel.ManifestExcel` class, then generates the Excel file using the
        `create_excel_from_data` method of the same class.

        Parameters
        ----------
        alation_schema_id : int
            The ID of the Alation schema for which to download the manifest Excel file.
        config : dict
            The configuration parameters for the operation.

        Returns
        -------
        str
            The path to the downloaded manifest Excel file.

        Raises
        ------
        Exception
            If an error occurs during the operation, an exception is raised and logged.
        """

        environment = config["environment"]

        tracer, logger = LoggerSingleton.instance(
            NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
        ).initialize_logging_and_tracing()

        with tracer.start_as_current_span("download_manifest_excel"):
            try:
                logger.info("alation_schema_id: " + str(alation_schema_id))

                table = Table(None, json_data_definition_file_path)

                manifest_excel = ManifestExcel()
                (
                    df_schema,
                    df_tables,
                    manifest_excel_file,
                    df_table_fields_data_definition,
                    df_columns,
                    df_column_fields_data_definition,
                ) = manifest_excel.generate_excel_file_data(
                    alation_schema_id, config, json_data_definition_file_path
                )

                manifest_excel_file = manifest_excel.create_excel_from_data(
                    config,
                    df_tables,
                    manifest_excel_file,
                    df_table_fields_data_definition,
                    df_columns,
                    df_column_fields_data_definition,
                )

                return manifest_excel_file

                # Get the data source title from
            except Exception as ex:
                error_msg = "Excel Error: %s", ex
                exc_info = sys.exc_info()
                LoggerSingleton.instance(
                    NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
                ).error_with_exception(error_msg, exc_info)
                raise

    @staticmethod
    def json_serial(obj):
        if isinstance(obj, pd.Series):
            return obj.tolist()  # or convert obj to dict using obj.to_dict()
        raise TypeError(f"Type {type(obj)} not serializable")

    @classmethod
    def download_manifest_json(cls, alation_schema_id, config):
        """
        Downloads the schema manifest for a given Alation schema ID using provided configuration.

        This method retrieves the schema manifest from an Alation instance. The manifest contains
        detailed information about the schema, including data types, relations, and other properties.

        Args:
            alation_schema_id (int): The unique identifier for the schema in the Alation system.
            This ID is used to locate the specific schema for which the manifest is required.

            config (dict): A configuration dictionary containing necessary parameters for connecting
            to the Alation instance. This might include authentication details and network configurations.

        Returns:
            dict: The schema manifest represented as a dictionary. The keys and values in this dictionary
            represent properties of the schema and their corresponding values as present in the Alation system.
        """

        data_product_id = config["data_product_id"]
        environment = config["environment"]

        tracer, logger = LoggerSingleton.instance(
            NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
        ).initialize_logging_and_tracing()

        schema_id = alation_schema_id
        schema_name = None

        with tracer.start_as_current_span("download_manifest_json"):
            try:
                # Get configuration parameteres
                environment = config.get("environment")
                edc_alation_base_url = config.get("edc_alation_base_url")
                repository_path = config.get("repository_path")
                alation_user_id = config.get("edc_alation_user_id")

                # Log the configuration parameters
                logger.info(f"edc_alation_base_url: {edc_alation_base_url}")
                logger.info(f"environment: {environment}")
                logger.info(f"schema_id: {schema_id}")

                if not edc_alation_base_url:
                    raise ValueError("edc_alation_base_url is not set in config.")

                # Get the Alation API Access Token
                token_endpoint = TokenEndpoint(edc_alation_base_url)
                (
                    status_code,
                    edc_alation_api_token,
                    api_refresh_token,
                ) = token_endpoint.get_api_token_from_config(config)
                logger.info(f"status_code: {status_code}")
                logger.info(
                    f"edc_alation_api_token length:{str(len(edc_alation_api_token))}"
                )
                if len(edc_alation_api_token.strip()) == 0:
                    msg = "Alation API Access Token is not set"
                    logger.error(msg)
                    raise ValueError(msg)

                # Get the schema and datasource details
                schema_result, datasource_result = cls.fetch_schema(
                    edc_alation_api_token, edc_alation_base_url, schema_id
                )

                schema_result_json = schema_result.json()

                # Set the schema name, datasource title and datasource_id
                schema_name = schema_result_json[0].get("name")
                datasource_title = datasource_result.get("title")
                datasource_id = datasource_result.get("id")
                alation_datasource_id = datasource_id

                # Log the schema details
                logger.info(f"schema_result length: {str(len(schema_result_json))}")
                logger.info(f"datasource_result length: {str(len(datasource_result))}")

                json_data_definition_file_path = cls.get_json_data_definition_file_path(
                    repository_path=repository_path,
                    environment=environment,
                )
                # Get the schema manifest
                msg = f"Loading manifest schema from {json_data_definition_file_path}"
                logger.info(msg)
                manifest = ManifestJson(json_data_definition_file_path)

                # Get the manifest file name
                manifest_json_file = cls.get_json_manifest_file_path(
                    "download",
                    repository_path,
                    datasource_title,
                    schema_name,
                    environment,
                    alation_user_id,
                )

                # Check if the datasource exists
                datasource = DataSource()
                datasource.check_datasource(
                    edc_alation_api_token,
                    edc_alation_base_url,
                    alation_datasource_id,
                    datasource_title,
                )

                # Get the schema structure
                manifest_dict = cls.fetch_schema_structure(
                    edc_alation_api_token,
                    edc_alation_base_url,
                    manifest,
                    datasource_id,
                    schema_id,
                )

                # Write the file
                jsonString = json.dumps(
                    manifest_dict, indent=4, default=cls.json_serial
                )
                jsonFile = open(manifest_json_file, "w", encoding="utf-8")
                jsonFile.write(jsonString)
                jsonFile.close()

                msg = "Wrote ManifestJson template file: " + manifest_json_file
                logger.info(msg)
                logger.info(
                    f"Validating the manifest file at {manifest_json_file} with schema"
                )

                # validate the manifest file
                metadata = manifest.validate_manifest(
                    manifest_json_file, json_data_definition_file_path
                )
                logger.info("Metadata File Validated")
                logger_singleton.force_flush()

                return manifest_json_file
            except Exception as ex:
                error_msg = "Error: %s", ex
                exc_info = sys.exc_info()
                LoggerSingleton.instance(
                    NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
                ).error_with_exception(error_msg, exc_info)
                raise

    @classmethod
    def fetch_schema_structure(
        cls,
        edc_alation_api_token,
        edc_alation_base_url,
        manifest,
        alation_datasource_id,
        alation_schema_id,
    ):
        """
        Retrieves the structure of a specific schema from Alation using the provided schema ID and manifest.

        Args:
            edc_alation_api_token (str): The API token for authenticating with the Alation instance.
            edc_alation_base_url (str): The base URL of the Alation instance.
            manifest (dict): The manifest defining the structure of the schema.
            alation_datasource_id (int): The ID of the Alation data source related to the schema.
            alation_schema_id (int): The ID of the Alation schema whose structure is to be retrieved.

        Raises:
            ValueError: If the response from the Alation API is not successful.

        Returns:
            tuple: A tuple containing the status code and a dictionary representing the structure of the schema.
        """

        try:
            tracer, logger = LoggerSingleton.instance(
                NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
            ).initialize_logging_and_tracing()

            with tracer.start_as_current_span("fetch_schema_structure"):
                schema_result_json = None

                try:
                    schema_results, datasource_result = cls.fetch_schema(
                        edc_alation_api_token,
                        edc_alation_base_url,
                        alation_schema_id,
                    )
                    schema_result_json = schema_results.json()
                except requests.exceptions.RequestException as ex_r:
                    error_msg = "Error in requests: %s", str(ex_r)
                    exc_info = sys.exc_info()
                    LoggerSingleton.instance(
                        NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
                    ).error_with_exception(error_msg, exc_info)
                    raise
                except Exception as ex_:
                    error_msg = "Error: %s", str(ex_)
                    exc_info = sys.exc_info()
                    LoggerSingleton.instance(
                        NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
                    ).error_with_exception(error_msg, exc_info)
                    raise

                logger.info(f"Info for schema ID: {alation_schema_id}")
                found_schema = False
                (
                    schema_fields,
                    expected_table_fields,
                    expected_column_fields,
                    required_table_fields,
                ) = manifest.get_manifest_expected_fields()
                manifest_dict = {}
                manifest_dict["tables"] = []

                for schema in schema_result_json:
                    logger.info(f"schema_id: {str(schema['id'])}")
                    if schema["id"] == int(alation_schema_id):
                        found_schema = True

                        schema_name = schema["name"]
                        logger.info(
                            f"Found the desired schema with name: {schema_name}"
                        )
                        logger.info(f"Structure length: {str(len(schema))}")
                        for field in schema_fields:
                            # Check if this field is already populated, otherwise use a default value
                            if field in schema:
                                manifest_dict[field] = schema[field]
                            else:
                                # Check if this field is in the list of custom fields
                                found_custom_field = False
                                for custom_field in schema["custom_fields"]:
                                    formatted_field_name = field.lower().replace(
                                        " ", ""
                                    )
                                    formatted_custom_field_name = (
                                        custom_field["field_name"]
                                        .lower()
                                        .replace(" ", "")
                                    )
                                    if (
                                        formatted_field_name
                                        in formatted_custom_field_name
                                    ):
                                        found_custom_field = True
                                        manifest_dict[field] = custom_field["value"]
                                # Exceptions to the rule - Fields that need to be manually mapped
                                if not found_custom_field:
                                    # Enter the schema name in the identifier field
                                    if field == "identifier" and "name" in schema:
                                        manifest_dict[field] = schema["name"]
                                    elif field == "alationDatasourceID":
                                        manifest_dict[field] = alation_datasource_id
                                    elif field == "alationSchemaID":
                                        manifest_dict[field] = alation_schema_id
                                    else:
                                        manifest_dict[field] = schema_fields[field]

                        # Get the json schema file path
                        # TODO Pass in the json schema file path

                        table = Table(None, None)

                        # Iterate through each table and add a manifest template entry
                        df_tables, tables_dict = table.fetch_schema_tables(
                            edc_alation_api_token,
                            edc_alation_base_url,
                            alation_datasource_id,
                            alation_schema_id,
                            schema_results,
                        )

                        if tables_dict:
                            # Determine the number of threads to use
                            num_threads = min(NUM_THREADS_MAX, len(tables_dict))

                            # Using ThreadPoolExecutor
                            with concurrent.futures.ThreadPoolExecutor(
                                max_workers=num_threads
                            ) as executor:
                                futures = {}
                                for (
                                    unfetched_table,
                                    table_info,
                                ) in tables_dict.items():
                                    future = executor.submit(
                                        table.fetch_table_and_columns,
                                        edc_alation_api_token,
                                        edc_alation_base_url,
                                        alation_datasource_id,
                                        alation_schema_id,
                                        table_info,
                                        expected_table_fields,
                                        expected_column_fields,
                                        schema_results,
                                    )
                                    futures[unfetched_table] = future

                                for future in concurrent.futures.as_completed(
                                    futures.values()
                                ):
                                    manifest_dict["tables"].append(future.result())
                        else:
                            error_msg = "No tables found"
                            raise EdcAlationError(error_msg)

                if not found_schema:
                    error_msg = "Could not find the schema ID in the list of schemas for this data source"
                    raise EdcAlationError(error_msg)

                # Create a JSON structure containing the schema, tables, and columns
                return manifest_dict

        except Exception as ex:
            error_msg = str(ex)
            exc_info = sys.exc_info()
            logger_singleton.error_with_exception(error_msg, exc_info)
            raise EdcAlationError(error_msg) from ex

    @classmethod
    def upload_manifest_json(cls, metadata_json_data, config, authenticated_user_id):
        """
        Uploads a schema manifest to Alation.

        Args:
            metadata_json_data (dict): Contains metadata information such as the Alation Schema ID.
            config (dict): Configuration data with the following keys:
                - edc_alation_base_url (str): The base URL of the Alation instance.
                - yyyy (str): Year component for manifest file generation.
                - mm (str): Month component for manifest file generation.
                - dd (str): Day component for manifest file generation.
                - repository_path (str): Path to the repository for manifest file.
                - environment (str): The current environment in use.
                - edc_json_schema_location (str): The location of EDC schema.
                - edc_alation_user_id (str): The user ID for Alation API.

        Returns:
            manifest_dict (dict): A dictionary with the key "result" set to "success" if the operation completes successfully.
        """

        data_product_id = config["data_product_id"]
        environment = config["environment"]

        tracer, logger = LoggerSingleton.instance(
            NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
        ).initialize_logging_and_tracing()

        with tracer.start_as_current_span("upload_schema_manifest"):
            try:
                # Get the configuration data
                edc_alation_base_url = config.get("edc_alation_base_url")
                # Format as a 24-hour time string
                repository_path = config.get("repository_path")
                environment = config.get("environment")
                alation_user_id = config.get("edc_alation_user_id")

                # Get the Alation Schema ID form the json
                alation_schema_id = metadata_json_data["alationSchemaID"]

                logger.info(f"alation_user_id:{alation_user_id}")

                # Get the API access token
                token_endpoint = TokenEndpoint(edc_alation_base_url)
                (
                    status_code,
                    edc_alation_api_token,
                    alation_refresh_token,
                ) = token_endpoint.get_api_token_from_config(config)
                logger.info(f"get_api_token_from_config:status_code:{status_code}")
                msg = f"edc_alation_api_token length:{str(len(edc_alation_api_token))}"
                logger.info(msg)

                if len(edc_alation_api_token.strip()) == 0:
                    msg = "Alation API Access Token is not set"
                    raise ValueError(msg)

                # Get the schema and datasource information
                schema_results, datasource_results = cls.fetch_schema(
                    edc_alation_api_token,
                    edc_alation_base_url,
                    alation_schema_id,
                )

                # Get the schema and datasource information
                schema_result_json = schema_results.json()
                schema_name = schema_result_json[0].get("name")
                datasource_title = datasource_results.get("title")
                alation_datasource_id = datasource_results.get("id")

                # Get the json schema file path
                json_data_definition_file_path = cls.get_json_data_definition_file_path(
                    repository_path, environment
                )

                table = Table(None, json_data_definition_file_path)

                # Get expected table structure from Excel structure file
                df_tables, tables_dict = table.fetch_schema_tables(
                    config,
                    alation_datasource_id,
                    alation_schema_id,
                    datasource_results,
                    schema_results,
                )

                manifest = ManifestJson(json_data_definition_file_path)

                schema = manifest.fetch_schema_data()

                excel_data_definition_file = cls.get_excel_data_definition_file_path(
                    repository_path, environment
                )
                df_table_fields_data_definition = pd.read_excel(
                    excel_data_definition_file
                )

                # Get the valid editable fields
                editable_fields = table.fetch_editable_fields(
                    df_tables, df_table_fields_data_definition
                )

                # Get the valid date fields
                # Todo - do not hardcode
                date_fields = ["Metadata Last Updated", "Last Update"]

                # Get the manifest file name
                manifest_json_file = cls.get_json_manifest_file_path(
                    "upload",
                    repository_path,
                    datasource_title,
                    schema_name,
                    environment,
                    alation_user_id,
                )

                # Write the manifest file
                with open(manifest_json_file, "w", encoding="utf-8") as f:
                    json.dump(metadata_json_data, f)

                # Validate the manifest file
                msg = "Validating the manifest file at {0} with schema".format(
                    manifest_json_file
                )
                logger.info(msg)

                metadata = manifest.validate_manifest(
                    manifest_json_file, json_data_definition_file_path
                )
                logger.info(
                    f"Metadata File Validated file of length {str(len(metadata))}"
                )

                # Update based on ManifestJson file
                if (
                    token_endpoint.validate_refresh_token(
                        alation_user_id, alation_refresh_token
                    )
                    is not None
                ):
                    custom_fields_endpoint = CustomFields()
                    logger.info(
                        "Created custom fields endpoint for updating custom fields via API"
                    )

                    tags_endpoint = Tags(edc_alation_api_token, edc_alation_base_url)
                    logger.info("Created tags endpoint for updating tags via API")

                    id_finder_endpoint = IdFinder(
                        edc_alation_api_token, edc_alation_base_url
                    )

                    # encode key
                    # always encode schema name regardless of ENCODE_PERIOD
                    if "." in schema_name:
                        encoded_schema_name = f'"{schema_name}"'
                    else:
                        encoded_schema_name = schema_name

                    # Update the schema
                    logger.info(
                        "Created id finder for getting detailed information on Alation objects"
                    )
                    logger.info(
                        "Updating the schema fields for data source {0} and schema {1}".format(
                            alation_datasource_id, schema_name
                        )
                    )

                    response_content = custom_fields_endpoint.update(
                        edc_alation_api_token,
                        edc_alation_base_url,
                        "schema",
                        alation_datasource_id,
                        encoded_schema_name,
                        schema,
                        True,
                        editable_fields=editable_fields,
                        date_fields=date_fields,
                    )
                    logger.info("response_content: " + str(response_content))
                    schema_key = str(alation_datasource_id) + "." + encoded_schema_name
                    schema_id = id_finder_endpoint.find("schema", schema_key)
                    for tag in manifest.tags:
                        tags_endpoint.apply("schema", schema_id, tag)

                    logger.info("df_tables: " + str(df_tables))
                    authorized_tables = {}
                    unauthorized_tables = {}

                    for k, v in df_tables.items():
                        steward_value = v.get("Steward", [])

                        if not isinstance(steward_value, (list, tuple, str)):
                            steward_value = []

                        if authenticated_user_id in steward_value:
                            authorized_tables[k] = v
                        else:
                            unauthorized_tables[k] = v

                    authorized_tables_count = len(authorized_tables.items())
                    unauthorized_table_count = len(unauthorized_tables.items())

                    if authorized_tables:
                        # Update the tables
                        tables_dict = manifest.get_tables_data()
                        if tables_dict:
                            total_items = len(tables_dict.items())
                            # reinit endpoint
                            obj_custom_fields_endpoint = CustomFields()

                            for idx, (table_name, value) in enumerate(
                                tables_dict.items()
                            ):
                                # Set force_submit to True on the last item
                                force_submit = idx == total_items - 1

                                table_result = table.update_table_structure(
                                    edc_alation_api_token,
                                    edc_alation_base_url,
                                    alation_datasource_id,
                                    schema_name,
                                    value,
                                    force_submit=force_submit,
                                    obj_custom_fields_endpoint=obj_custom_fields_endpoint,
                                    editable_fields=editable_fields,
                                    table_name=table_name,
                                    date_fields=date_fields,
                                )
                                logger.info("table_result: " + str(table_result))
                            # Commented out the threading because complexity not worth it
                            # compared to batching updates in sets of 50
                            # and limiting updates to differences

                            # num_threads = min(NUM_THREADS_MAX, len(tables_dict))

                            # Using ThreadPoolExecutor
                            # with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
                            #    futures = []
                            #    items = list(tables_dict.items())
                            #    total_items = len(items)

                            # for idx, (key, value) in enumerate(items):
                            # Set force_submit to True on the last item

                            #    future = executor.submit(cls.update_table_structure, edc_alation_api_token,
                            #                             edc_alation_base_url, alation_datasource_id, schema_name,
                            #                             value, force_submit=force_submit)
                            #    futures.append(future)

                            # Wait for all futures to complete
                            # concurrent.futures.wait(futures)
                            return (
                                tables_dict,
                                authorized_tables_count,
                                unauthorized_table_count,
                            )

                        else:
                            error_msg = "No tables found"
                            raise EdcAlationError(error_msg)

                    else:
                        error_msg = "No tables found"
                        raise EdcAlationError(error_msg)
                else:
                    error_msg = "Refresh token is not valid"
                    raise EdcAlationError(error_msg)
            except Exception as ex:
                error_msg = "Error: %s", ex
                exc_info = sys.exc_info()
                LoggerSingleton.instance(
                    NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
                ).error_with_exception(error_msg, exc_info)
                raise

    @classmethod
    def upload_manifest_excel(
        cls,
        manifest_excel_file_path,
        config,
        json_data_definition_file_path,
        authenticated_user_id,
    ):
        """
        Uploads a schema manifest to Alation.

        Args:
            metadata_excel_data (dict): Contains metadata information such as the Alation Schema ID.
            config (dict): Configuration data with the following keys:
                - edc_alation_base_url (str): The base URL of the Alation instance.
                - yyyy (str): Year component for manifest file generation.
                - mm (str): Month component for manifest file generation.
                - dd (str): Day component for manifest file generation.
                - repository_path (str): Path to the repository for manifest file.
                - environment (str): The current environment in use.
                - edc_json_schema_location (str): The location of EDC schema.
                - edc_alation_user_id (str): The user ID for Alation API.

        Returns:
            manifest_dict (dict): A dictionary with the key "result" set to "success" if the operation completes successfully.
        """

        data_product_id = config["data_product_id"]
        environment = config["environment"]

        tracer, logger = LoggerSingleton.instance(
            NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
        ).initialize_logging_and_tracing()

        with tracer.start_as_current_span("upload_schema_manifest"):
            try:
                # Get the configuration data
                edc_alation_base_url = config.get("edc_alation_base_url")
                # Format as a 24-hour time string
                repository_path = config.get("repository_path")
                environment = config.get("environment")
                alation_user_id = config.get("edc_alation_user_id")
                json_data_definition_file_path = cls.get_json_data_definition_file_path(
                    repository_path, environment
                )
                logger.info(f"alation_user_id:{alation_user_id}")

                # Get the API access token
                token_endpoint = TokenEndpoint(edc_alation_base_url)
                (
                    status_code,
                    edc_alation_api_token,
                    alation_refresh_token,
                ) = token_endpoint.get_api_token_from_config(config)
                logger.info(f"get_api_token_from_config:status_code:{status_code}")
                msg = f"edc_alation_api_token length:{str(len(edc_alation_api_token))}"
                logger.info(msg)

                if len(edc_alation_api_token.strip()) == 0:
                    msg = "Alation API Access Token is not set"
                    raise ValueError(msg)

                manifest_excel = ManifestExcel()
                df_tables = manifest_excel.read_manifest_excel_file_tables_worksheet(
                    manifest_excel_file_path
                )
                alation_schema_id = df_tables["schema_id"][0]
                logger.info(f"alation_schema_id:{alation_schema_id}")

                # Get the schema and datasource information
                schema_results, datasource_results = cls.fetch_schema(
                    edc_alation_api_token,
                    edc_alation_base_url,
                    alation_schema_id,
                )

                schema_result_json = schema_results.json()
                schema_name = schema_result_json[0].get("name")
                alation_datasource_id = datasource_results.get("id")

                table = Table(None, json_data_definition_file_path)

                # Get expected table structure from Excel structure file
                df_tables_expected, tables_dict = table.fetch_schema_tables(
                    edc_alation_api_token,
                    edc_alation_base_url,
                    alation_datasource_id,
                    alation_schema_id,
                    schema_results,
                )

                excel_data_definition_file = cls.get_excel_data_definition_file_path(
                    repository_path, environment
                )
                df_table_fields_data_definition = pd.read_excel(
                    excel_data_definition_file
                )

                # Get the valid editable fields
                editable_fields = table.fetch_editable_fields(
                    df_tables_expected, df_table_fields_data_definition
                )

                date_fields = ["Metadata Last Updated", "Last Update"]

                # Update based on ManifestJson file
                if (
                    token_endpoint.validate_refresh_token(
                        alation_user_id, alation_refresh_token
                    )
                    is not None
                ):
                    custom_fields_endpoint = CustomFields()
                    logger.info(
                        "Created custom fields endpoint for updating custom fields via API"
                    )

                    tags_endpoint = Tags(edc_alation_api_token, edc_alation_base_url)
                    logger.info("Created tags endpoint for updating tags via API")

                    id_finder_endpoint = IdFinder(
                        edc_alation_api_token, edc_alation_base_url
                    )

                    # encode key
                    # always encode schema name regardless of ENCODE_PERIOD
                    if "." in schema_name:
                        encoded_schema_name = f'"{schema_name}"'
                    else:
                        encoded_schema_name = schema_name

                    # Update the schema
                    logger.info(
                        "Created id finder for getting detailed information on Alation objects"
                    )
                    logger.info(
                        f"Updating the schema fields for data source {alation_datasource_id} and schema {schema_name}"
                    )

                    # TODO Update schema info when the schema tab is implemented
                    # response_content = custom_fields_endpoint.update(edc_alation_api_token, edc_alation_base_url,
                    #                                                  "schema", alation_datasource_id, encoded_schema_name, schema, True, editable_fields=editable_fields)
                    # logger.info("response_content: " + str(response_content))
                    # TODO Update the schema tags
                    # schema_key = str(alation_datasource_id) + \
                    #     "." + encoded_schema_name
                    # schema_id = id_finder_endpoint.find('schema', schema_key)
                    # for tag in manifest.tags:
                    #    tags_endpoint.apply('schema', schema_id, tag)

                    # Convert df_tables to a dictionary with 'table_name' as the key
                    tables_dict = df_tables.set_index("name").to_dict(orient="index")

                    logger.info("tables_dict: " + str(tables_dict))
                    authorized_tables = {}
                    unauthorized_tables = {}

                    for k, v in tables_dict.items():
                        steward_value = v.get("Steward", [])

                        if not isinstance(steward_value, (list, tuple, str)):
                            steward_value = []

                        if authenticated_user_id in steward_value:
                            authorized_tables[k] = v
                        else:
                            unauthorized_tables[k] = v

                    authorized_tables_count = len(authorized_tables.items())
                    unauthorized_table_count = len(unauthorized_tables.items())

                    if authorized_tables:
                        total_items = len(authorized_tables.items())
                        # reinit endpoint
                        obj_custom_fields_endpoint = CustomFields()

                        for idx, (key, table_dict) in enumerate(
                            authorized_tables.items()
                        ):
                            # Set force_submit to True on the last item
                            force_submit = idx == total_items - 1

                            table_name = key
                            table_result = table.update_table_structure(
                                edc_alation_api_token,
                                edc_alation_base_url,
                                alation_datasource_id,
                                schema_name,
                                table_dict,
                                force_submit=force_submit,
                                obj_custom_fields_endpoint=obj_custom_fields_endpoint,
                                editable_fields=editable_fields,
                                table_name=table_name,
                                date_fields=date_fields,
                            )
                            logger.info("table_result: " + str(table_result))

                        # Commented out the threading because complexity not worth it
                        # compared to batching updates in sets of 50
                        # and limiting updates to differences

                        # num_threads = min(NUM_THREADS_MAX, len(tables_dict))

                        # Using ThreadPoolExecutor
                        # with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
                        #    futures = []
                        #    items = list(tables_dict.items())
                        #    total_items = len(items)

                        # for idx, (key, value) in enumerate(items):
                        # Set force_submit to True on the last item

                        #    future = executor.submit(cls.update_table_structure, edc_alation_api_token,
                        #                             edc_alation_base_url, alation_datasource_id, schema_name,
                        #                             value, force_submit=force_submit)
                        #    futures.append(future)

                        # Wait for all futures to complete
                        # concurrent.futures.wait(futures)
                        return (
                            tables_dict,
                            authorized_tables_count,
                            unauthorized_table_count,
                        )

                    else:
                        error_msg = "No tables found"
                        raise EdcAlationError(error_msg)
                else:
                    error_msg = "Refresh token is not valid"
                    raise EdcAlationError(error_msg)
            except Exception as ex:
                error_msg = f"Error: {str(ex)}"
                exc_info = sys.exc_info()
                LoggerSingleton.instance(
                    NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
                ).error_with_exception(error_msg, exc_info)
                raise
