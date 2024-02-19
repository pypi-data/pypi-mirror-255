import json
from jsonschema import validate
import sys
import os

import pandas as pd
import requests
import numpy as np


from cdh_lava_core.alation_service.json_manifest import ManifestJson
from cdh_lava_core.alation_service.db_column import Column
from cdh_lava_core.alation_service.id_finder import IdFinder
from cdh_lava_core.alation_service.tags import Tags

from pandas import json_normalize
from bs4 import BeautifulSoup

from cdh_lava_core.cdc_log_service.environment_logging import LoggerSingleton

from cdh_lava_core.cdc_tech_environment_service import (
    environment_file as cdc_env_file,
    environment_http as cdc_env_http,
)

# Get the currently running file name
NAMESPACE_NAME = os.path.basename(os.path.dirname(__file__))
# Get the parent folder name of the running file
SERVICE_NAME = os.path.basename(__file__)

ENVIRONMENT = "dev"
TIMEOUT_ONE_MIN = 60  # or set to whatever value you want
REQUEST_TIMEOUT = 45

ENCODE_PERIOD = False

# Get the absolute path of the current script
current_script_path = os.path.abspath(__file__)

# Get the project root directory by going up one or more levels
project_root = os.path.dirname(os.path.dirname(current_script_path))


class Table:
    """
    Represents a table object.

    """

    def __init__(
        self, table_json, data_definition_file_path, data_product_id, environment
    ):
        """
        Initializes a Table object using the provided table JSON.

        Args:
            table_json (dict): The JSON data representing the table.

        Raises:
            Exception: If an error occurs during initialization.

        """

        tracer, logger = LoggerSingleton.instance(
            NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
        ).initialize_logging_and_tracing()

        with tracer.start_as_current_span("__init__"):
            try:
                self.data_definition_file_path = data_definition_file_path

                if table_json is None:
                    return

                manifest = ManifestJson(data_definition_file_path)

                # get the expected fields from the manifest
                (
                    schema_fields,
                    expected_table_fields,
                    expected_column_fields,
                    required_table_fields,
                ) = manifest.get_manifest_expected_fields()

                msg = "Schema fields length: " + str(len(schema_fields))
                logger.info(msg)
                msg = "Expected table fields length: " + str(
                    len(expected_column_fields)
                )
                logger.info(msg)

                # add specified tables fields to the table object and update if necessary
                for key in expected_table_fields:
                    if key in table_json:
                        setattr(self, key, table_json[key])

                missing_keys = [
                    key for key in required_table_fields if not hasattr(self, key)
                ]

                if missing_keys:
                    logger.error(f"Missing keys: {missing_keys}")

                # get the extra description fields from the table JSON
                self.extra_description_fields = (
                    self.get_table_extra_description_columns(table_json)
                )

                self.name = table_json.get("name")
                self.title = table_json.get("title")
                self.description = self.format_description(table_json)

                tags = table_json.get("tags")
                if tags is not None:
                    self.tags = tags
                else:
                    self.tags = []
                columns_json = table_json.get("columns")

                if columns_json is not None:
                    # self.columns = list(
                    #     map(lambda c: Column(c, data_definition_file_path), columns_json))
                    self.columns = {
                        column.name: column
                        for column in map(
                            lambda c: Column(
                                c,
                                self.data_definition_file_path,
                                data_product_id,
                                environment,
                            ),
                            columns_json,
                        )
                    }

                else:
                    self.columns = None
            except Exception as ex:
                error_msg = "Error: %s", ex
                exc_info = sys.exc_info()
                LoggerSingleton.instance(
                    NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
                ).error_with_exception(error_msg, exc_info)
                raise

    @classmethod
    def fetch_table_and_columns(
        cls,
        edc_alation_api_token,
        edc_alation_base_url,
        alation_datasource_id,
        alation_schema_id,
        unfetched_table,
        expected_table_fields,
        expected_column_fields,
        schema_results,
        data_product_id,
        environment,
    ):
        """
        Fetches the structure of a table, including its columns, based on the provided information.

        Args:
            alation_datasource_id (str): The Alation data source ID associated with the table.
            alation_schema_id (str): The Alation schema ID associated with the table.
            alation_headers (dict): The headers to be used for making API requests to Alation.
            edc_alation_base_url (str): The base URL for the Alation instance.
            unfetched_table (dict): A dictionary representing the unfetched table.
            expected_table_fields (list): A list of expected fields for the table.
            expected_column_fields (list): A list of expected fields for the columns in the table.

        Returns:
            dict: A dictionary representing the fetched table. The dictionary includes details about the table
                and its columns. If the table has no columns, 'columns' key will have an empty list value.

        This function will:
            - Populate the fetched table dictionary with data from the unfetched table or with default values.
            - Retrieve all columns associated with the table from Alation and create a dictionary for each column.
            - Append each column dictionary to the 'columns' key in the fetched table dictionary.
        """

        if len(unfetched_table) >= len(expected_table_fields):
            fetched_table = {}
            for tf in expected_table_fields:
                # see if this field is already populated, otherwise use a default value
                if tf in unfetched_table:
                    fetched_table[tf] = unfetched_table[tf]
                else:
                    fetched_table[tf] = expected_table_fields[tf]

        # iterate through each column associated with this table and add a manifest template entry
        custom_field_dict = unfetched_table.get("custom_fields")
        alation_table_id = unfetched_table.get("id")
        df_columns = cls.fetch_table_columns(
            edc_alation_api_token,
            edc_alation_base_url,
            alation_datasource_id,
            alation_schema_id,
            alation_table_id,
            schema_results,
            data_product_id,
            environment,
        )
        if len(df_columns) > 0:
            fetched_table["columns"] = []
            # for each column associated with this table...
            for column_name, content in df_columns.items():
                this_column_dict = {}
                # get expected custom fields
                for column_name in expected_column_fields:
                    # if expected column field is already populated, use that value, otherwise use a default value
                    if column_name in df_columns.columns:
                        this_column_dict[column_name] = content
                    else:
                        this_column_dict[column_name] = expected_column_fields[
                            column_name
                        ]
                fetched_table["columns"].append(this_column_dict)
            # iterate through each custom_field_dict
            if custom_field_dict:
                fetched_table["customfields"] = []
            # for each custon field associated with this table...
            for i in custom_field_dict:
                this_custom_flds_dict = {}
                this_custom_flds_dict[i["field_name"]] = i["value"]
                fetched_table["customfields"].append(this_custom_flds_dict)

        return fetched_table

    @staticmethod
    def fetch_table_columns(
        edc_alation_api_token,
        edc_alation_base_url,
        alation_datasource_id,
        alation_schema_id,
        alation_table_id,
        schema_results,
        data_product_id,
        environment,
    ):
        """
        Get the list of columns for a specific table in the Alation instance.

        Args:
            edc_alation_api_token (str): The API token for authenticating with the Alation instance.
            edc_alation_base_url (str): The base URL of the Alation instance.
            alation_schema_id (int): The ID of the Alation schema.
            alation_datasource_id (int): The ID of the Alation data source.
            alation_table_id (int): The ID of the Alation table.

        Returns:
            list: The list of columns for the specified table. Each column is represented as a dictionary.
        """

        tracer, logger = LoggerSingleton.instance(
            NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
        ).initialize_logging_and_tracing()

        with tracer.start_as_current_span("fetch_table_columns"):
            column_to_process = {}

            try:
                schema_result_json = schema_results.json()
                schema_custom_fields = schema_result_json[0].get("custom_fields")
                schema_steward_list = None
                if schema_custom_fields is not None:
                    schema_steward_list = [
                        item["value"]
                        for item in schema_custom_fields
                        if item["field_name"] == "Steward"
                    ]
                    # if list of 1 set to first value
                    if len(schema_steward_list) == 1 and isinstance(
                        schema_steward_list[0], list
                    ):
                        schema_steward_list = schema_steward_list[0]

                    if schema_steward_list:
                        logger.info(f"schema_steward_list: {str(schema_steward_list)}")
                    else:
                        logger.info(f"schema_steward_list not found")

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
                    params["schema_id"] = alation_schema_id
                    params["ds_id"] = alation_datasource_id

                    if alation_table_id != -1:
                        params["table_id"] = alation_table_id

                    # Create the API URL
                    api_url = f"{edc_alation_base_url}/integration/v2/column/"

                    # Log Parameters
                    logger.info(f"api_url: {api_url}")
                    logger.info(f"params: {str(params)}")

                    # Make the API request
                    obj_http = cdc_env_http.EnvironmentHttp()

                    response_columns = obj_http.get(
                        api_url,
                        headers,
                        REQUEST_TIMEOUT,
                        params,
                        data_product_id,
                        environment,
                    )

                    # Check the status code
                    if response_columns.status_code != 200:
                        # Raise an exception if the status code is not 200 (OK)
                        response_columns.raise_for_status()

                    # Append the response to the merged_data list
                    merged_data.extend(response_columns_json)

                    # when there are no more columns all have been processed so break out of the loop
                    if len(response_columns_json) == 0:
                        break

                # Convert the merged data list to a single JSON string
                merged_json_string = json.dumps(merged_data)
                merged_data_json = json.loads(merged_json_string)

                # Go through all tables listed for this schema and add to our manifest template
                # Convert to Python object

                expanded_json = []
                for existing_column_item in merged_data_json:
                    new_item = existing_column_item.copy()  # start with existing fields

                    column_steward_list = None  # Initialize the variable here
                    for custom_field in new_item["custom_fields"]:
                        # handle stewards
                        if custom_field["field_name"] == "Steward":
                            column_steward_list = custom_field["value"]

                            # Create a list of unique otype and oid combinations from column_steward_list
                            combinations = {
                                (item["otype"], item["oid"])
                                for item in schema_steward_list + column_steward_list
                            }

                            # Add items from schema_steward_list to column_steward_list if not present
                            for combined_item in combinations:
                                search_otype = combined_item[0]
                                search_oid = combined_item[1]
                                found_column_items = [
                                    column_item
                                    for column_item in column_steward_list
                                    if column_item.get("otype") == search_otype
                                    and column_item.get("oid") == search_oid
                                ]

                                if not found_column_items:
                                    for (
                                        schema_item
                                    ) in (
                                        schema_steward_list
                                    ):  # corrected to schema_steward_list
                                        item_copy = schema_item.copy()
                                        item_copy["is_inherited"] = "inherited"
                                        column_steward_list.append(item_copy)
                                else:
                                    # The item exists in column_steward_list, set is_inherited to empty string
                                    found_column_items[0]["is_inherited"] = ""

                            # Modify 'Steward' field_name to 'Steward_Initial'
                            custom_field["field_name"] = "Steward_Initial"

                    # Add new 'Steward' attribute with value "merged" if column_steward_list is not None
                    if column_steward_list is not None:
                        new_item["custom_fields"].append(
                            {"field_name": "Steward", "value": column_steward_list}
                        )

                    # Promote custom fields to the column level
                    for field in existing_column_item["custom_fields"]:
                        # add custom fields
                        new_item[field["field_name"]] = field["value"]

                    expanded_json.append(new_item)

                # Convert to dataframe
                df_columns = json_normalize(expanded_json)

                return df_columns

            except Exception as ex:
                error_msg = "Error: %s: %s", ex, str(column_to_process)
                exc_info = sys.exc_info()
                LoggerSingleton.instance(
                    NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
                ).error_with_exception(error_msg, exc_info)
                raise

    def fetch_table_columns_extended(
        self,
        edc_alation_api_token,
        edc_alation_base_url,
        alation_datasource_id,
        alation_schema_id,
        alation_table_id,
        schema_results,
        data_product_id,
        environment,
    ):
        """
        Fetches tables for a specified schema from Alation, processes and matches them with a predefined Excel schema.

        This function retrieves tables related to a specified schema from Alation for further Excel processing.
        It starts by fetching the schema tables, then gets the expected table structure from an Excel structure file.
        The function processes and matches the data with the predefined Excel schema, ensuring that the columns are
        in the desired order. The data is then parsed, cleaned, and prepared for output, handling various data types
        like HTML and JSON. The final dataframe is printed, showcasing the tables sorted based on the Excel schema's order.

        Args:
            edc_alation_api_token (str): API token for the EDC Alation integration.
            edc_alation_base_url (str): Base URL for the EDC Alation.
            alation_datasource_id (int): The Alation ID of the datasource to fetch tables from.
            alation_schema_id (int): The Alation ID of the schema to fetch tables from.
            schema_results: Results obtained for the schema. (Expected type needs to be provided)

        Returns:
            tuple: Contains:
                - DataFrame: Processed dataframe containing the tables.
                - List: Columns that are suggested to be hidden.
                - DataFrame: Dataframe representing the field definitions from Excel.

        Raises:
            AssertionError: An error occurs if the status code from the token endpoint is not 200.
            ValueError: Errors that arise from parsing non-HTML content.
            Exception: General exceptions are logged with their error messages.

        Note:
            The function utilizes the BeautifulSoup library to handle and parse HTML content and json library for JSON content.
        """

        tracer, logger = LoggerSingleton.instance(
            NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
        ).initialize_logging_and_tracing()

        with tracer.start_as_current_span("fetch_table_columns_extended"):
            write_to_debug_excel = True

            #############################
            # Get Raw data from API
            #############################

            # Get db colunns from Alation for the specfied db column
            df_columns = self.fetch_table_columns(
                edc_alation_api_token,
                edc_alation_base_url,
                alation_datasource_id,
                alation_schema_id,
                alation_table_id,
                schema_results,
                data_product_id,
                environment,
            )

            # Save to excel for debugging
            # Define an Excel writer object
            if write_to_debug_excel:
                with pd.ExcelWriter(
                    "debug_df_columns.xlsx", engine="openpyxl"
                ) as writer:
                    # Save the entire DataFrame to the first sheet
                    df_columns.to_excel(writer, sheet_name="df_columns", index=False)

                    # Save only the columns (as a list) to the second sheet
                    pd.DataFrame(df_columns.columns, columns=["Column Names"]).to_excel(
                        writer, sheet_name="columns", index=False
                    )

            #############################
            # Get Expected data from data definition file
            #############################

            # Get expected column structure from Excel structure file
            (
                df_column_fields_data_definition,
                excel_data_definition_file,
            ) = self.fetch_column_definitions()

            if write_to_debug_excel:
                # Save to excel for debugging
                df_columns.to_excel(
                    "debug_df_column_fields_data_definition.xlsx", engine="openpyxl"
                )

            # Get ordered columns
            df_ordered_columns = df_column_fields_data_definition[
                df_column_fields_data_definition["excel_column_order"] > 0
            ]

            # Create a list of column names from df_table_fields_data_definition in the order specified by excel_column_order
            ordered_columns = df_ordered_columns.sort_values("excel_column_order")[
                "field_name"
            ].tolist()

            # Save to excel for debugging
            df_ordered_columns = pd.DataFrame(
                ordered_columns, columns=["ordered_columns"]
            )
            df_ordered_columns.to_excel(
                "debug_df_ordered_columns.xlsx", engine="openpyxl"
            )

            # Get a list of columns that exist in both df_columns and ordered_columns
            column_column_names = df_columns.columns.tolist()

            # Get the intersection of columns_expected and columns_present to preserve valid column order
            columns_undesired = [
                col for col in column_column_names if col not in ordered_columns
            ]

            # Get the list of columns not in valid_columns and append them at the end
            columns_desired = [
                col for col in ordered_columns if col not in column_column_names
            ]

            # Add columns_desired with NaN values
            for col in columns_desired:
                df_columns[col] = np.nan

            # Reorder the DataFrame columns using the desired order
            df_fields_enriched = df_columns[ordered_columns + columns_undesired]

            if write_to_debug_excel:
                # Define an Excel writer object
                with pd.ExcelWriter(
                    "debug_df_fields_enriched.xlsx", engine="openpyxl"
                ) as writer:
                    # Save the entire DataFrame to the first sheet
                    df_fields_enriched.to_excel(
                        writer, sheet_name="df_fields_enriched", index=False
                    )

                    # Save only the columns (as a list) to the second sheet
                    pd.DataFrame(
                        df_fields_enriched.columns, columns=["Column Names"]
                    ).to_excel(writer, sheet_name="columns", index=False)

            # Get valid object_set columns from expected column structure
            visible_fields = self.fetch_visible_fields(
                df_fields_enriched, df_column_fields_data_definition
            )

            extended_field_field_names = df_fields_enriched.columns.tolist()

            # Create a list of columns to hide from df_columns
            hidden_fields = [
                col for col in extended_field_field_names if col not in visible_fields
            ]

            # Save to excel for debugging
            df_hidden_fields = pd.DataFrame(hidden_fields, columns=["hidden_fields"])
            df_hidden_fields.to_excel("debug_df_hidden_fields.xlsx", engine="openpyxl")

            #############################
            # Handle HTML and JSON data
            #############################

            # Get valid object_set columns from expected column structure
            valid_object_set_columns = self.fetch_valid_object_set_fields(
                df_column_fields_data_definition, df_fields_enriched
            )

            # Save to excel for debugging
            df_valid_object_set_columns = pd.DataFrame(
                valid_object_set_columns, columns=["valid_object_set_columns"]
            )
            df_valid_object_set_columns.to_excel(
                "debug_df_valid_object_set_columns.xlsx", engine="openpyxl"
            )

            # get users lookup column / valueset column
            df_users, data_definition_file = self.fetch_valueset("User")

            # Convert valid object_set columns
            for column in valid_object_set_columns:
                # for each row in the column
                for idx in df_fields_enriched.index:
                    # Get the value at the current cell
                    cell_value = df_fields_enriched.loc[idx, column]
                    try:
                        # Try to parse it as HTML
                        if cell_value is None:
                            cell_value = ""

                        if not isinstance(cell_value, (list, np.ndarray)):
                            if pd.isna(cell_value):
                                cell_value = ""

                        if isinstance(cell_value, str):
                            cell_value = self.wrap_in_brackets(cell_value)
                            # Parse the JSON string into a Python dictionary
                            parsed_data = json.loads(cell_value)
                        else:
                            parsed_data = cell_value

                        if column == "Steward":
                            # Create a dataframe from the list of dictionaries
                            df_stewards = pd.DataFrame(parsed_data)

                            # Perform left join on 'oid' (from df_stewards) and 'user_id' (from df_users)
                            merged_df = df_stewards.merge(
                                df_users, left_on="oid", right_on="user_id", how="left"
                            )

                            # Drop the redundant 'oid' column from df_users
                            merged_df.drop(columns="user_id", inplace=True)

                            # Create the comma-delimited list in the desired format
                            user_list = [
                                f"{row['user_full_name']} ({row['user_email']}:{row['oid']})"
                                for _, row in merged_df.iterrows()
                            ]

                            # Join the list elements with commas
                            comma_delimited_list = ", ".join(user_list)

                            # Replace the cell value with the parsed HTML
                            # This assumes that you want the first column, as pd.read_html returns a list of columns

                        df_fields_enriched.loc[idx, column] = comma_delimited_list

                    except Exception as ex:
                        error_msg = f"Error: {str(ex)}"
                        exc_info = sys.exc_info()
                        logger_singleton.error_with_exception(error_msg, exc_info)
                        pass

            # Get valid html columns from expected column structure
            valid_html_columns = self.fetch_html_fields(
                df_column_fields_data_definition, df_fields_enriched
            )

            # Convert valid html columns
            for column in valid_html_columns:
                # for each row in the column
                for idx in df_fields_enriched.index:
                    # Get the value at the current cell
                    cell_value = df_fields_enriched.loc[idx, column]
                    try:
                        # Try to parse it as HTML
                        if cell_value is None:
                            cell_value = ""

                        if pd.isna(cell_value):
                            cell_value = ""

                        soup = BeautifulSoup(cell_value, "html.parser")

                        # Check if 'html' and 'body' tags exist
                        if not soup.html:
                            soup = BeautifulSoup(
                                "<html><body>" + str(soup) + "</body></html>",
                                "html.parser",
                            )

                        # Extract text from the HTML document
                        text = soup.get_text()

                        # Replace the cell value with the parsed HTML
                        # This assumes that you want the first column, as pd.read_html returns a list of columns
                        df_fields_enriched.loc[idx, column] = text
                    except ValueError:
                        # pd.read_html throws a ValueError if it can't parse the input as HTML
                        # If this happens, we'll just leave the cell value as it is
                        pass

            # Set the option to display all columns
            pd.set_option("display.max_columns", None)
            df_columns_formatted = df_fields_enriched.fillna("")

            # Define an Excel writer object
            if write_to_debug_excel:
                with pd.ExcelWriter(
                    "debug_df_columns_formatted.xlsx", engine="openpyxl"
                ) as writer:
                    # Save the entire DataFrame to the first sheet
                    df_columns_formatted.to_excel(
                        writer, sheet_name="df_columns_formatted", index=False
                    )

                    # Save only the columns (as a list) to the second sheet
                    pd.DataFrame(
                        df_columns_formatted.columns, columns=["Column Names"]
                    ).to_excel(writer, sheet_name="columns", index=False)

            df_columns_formatted = df_columns_formatted.sort_values(
                by=["table_name", "name"]
            )

            return df_columns_formatted, df_column_fields_data_definition

    def fetch_table_definitions_path(self):
        """
        Get the file path of the 'excel_data_definition_for_tables_sql.xlsx' file based on the provided data_definition_file_path.

        This function takes no arguments and utilizes the 'self.data_definition_file_path' attribute to extract the directory path
        where the 'excel_data_definition_for_tables_sql.xlsx' file is expected to be located. It then constructs the complete file path
        by joining the directory path with the filename. The constructed file path is returned.

        Returns:
            str: The complete file path of the 'excel_data_definition_for_tables_sql.xlsx' file based on the provided data_definition_file_path.

        Note:
            This function assumes the existence of the 'self.data_definition_file_path' attribute representing the file path of the source schema.


        """
        # Get the directory part of the file path
        directory_path = os.path.dirname(self.data_definition_file_path)

        data_definition_xls_file = "excel_data_definition_for_tables_sql.xlsx"

        # Join the directory path and the file name
        data_definition_xls_file_path = os.path.join(
            directory_path, data_definition_xls_file
        )

        return data_definition_xls_file_path

    def fetch_column_definitions_path(self):
        """
        Get the file path of the 'excel_data_definition_for_columns_sql.xlsx' file based on the provided data_definition_file_path.

        This function takes no arguments and utilizes the 'self.data_definition_file_path' attribute to extract the directory path
        where the 'excel_data_definition_for_columns_sql.xlsx' file is expected to be located. It then constructs the complete file path
        by joining the directory path with the filename. The constructed file path is returned.

        Returns:
            str: The complete file path of the 'excel_data_definition_for_columns_sql.xlsx' file based on the provided data_definition_file_path.

        Note:
            This function assumes the existence of the 'self.data_definition_file_path' attribute representing the file path of the source schema.


        """
        # Get the directory part of the file path
        directory_path = os.path.dirname(self.data_definition_file_path)

        data_definition_xls_file = "excel_data_definition_for_columns_sql.xlsx"

        # Join the directory path and the file name
        data_definition_xls_file_path = os.path.join(
            directory_path, data_definition_xls_file
        )

        return data_definition_xls_file_path

    def fetch_table_definitions(self, data_product_id, environment):
        """
        Reads an Excel file containing a schema for SQL tables from a specific location in the file system.

        The function first changes the current working directory to the project root directory, and then creates
        an instance of the EnvironmentFile class. It constructs a path to the file location based on the current
        environment and checks whether the file exists. The function reads the Excel file into a pandas DataFrame
        and returns the DataFrame and the file path.

        The function raises an AssertionError if the file does not exist.

        Returns:
            tuple: A tuple containing a pandas DataFrame representing the content of the Excel file and the path
            to the file.
        """

        tracer, logger = LoggerSingleton.instance(
            NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
        ).initialize_logging_and_tracing()

        with tracer.start_as_current_span("fetch_table_definitions"):
            # Get the file utility object
            obj_file = cdc_env_file.EnvironmentFile()

            # Get the excel schema file
            excel_data_definition_file_path = self.fetch_table_definitions_path()
            file_exists = obj_file.file_exists(
                True, excel_data_definition_file_path, data_product_id, environment
            )
            logger.info(f"file_exists: {file_exists}")
            df_fields_excel_table = pd.read_excel(excel_data_definition_file_path)
            return df_fields_excel_table, excel_data_definition_file_path

    def fetch_column_definitions(self, data_product_id, environment):
        """
        Reads an Excel file containing a schema for SQL columns from a specific location in the file system.

        The function first changes the current working directory to the project root directory, and then creates
        an instance of the EnvironmentFile class. It constructs a path to the file location based on the current
        environment and checks whether the file exists. The function reads the Excel file into a pandas DataFrame
        and returns the DataFrame and the file path.

        The function raises an AssertionError if the file does not exist.

        Returns:
            tuple: A tuple containing a pandas DataFrame representing the content of the Excel file and the path
            to the file.
        """

        tracer, logger = LoggerSingleton.instance(
            NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
        ).initialize_logging_and_tracing()

        with tracer.start_as_current_span("fetch_column_definitions"):
            # Get the file utility object
            obj_file = cdc_env_file.EnvironmentFile()

            # Get the excel schema file
            excel_data_definition_file_path = self.fetch_column_definitions_path()
            running_local = config.get("running_local")
            file_exists = obj_file.file_exists(
                running_local,
                excel_data_definition_file_path,
                data_product_id,
                environment,
            )
            logger.info(f"file_exists: {file_exists}")
            df_fields_excel_column = pd.read_excel(excel_data_definition_file_path)
            return df_fields_excel_column, excel_data_definition_file_path

    def fetch_required_fields(
        self, df_tables, df_table_fields_data_definition, data_product_id, environment
    ):
        """
        Retrieve a list of valid required columns from the Excel schema DataFrame based on the provided table DataFrame.

        Parameters:
            df_table_fields_data_definition (pd.DataFrame): A pandas DataFrame representing the Excel schema with column information.
            df_tables (pd.DataFrame): A pandas DataFrame representing the table for which valid required columns are to be determined.

        Returns:
            list: A list of column names from the Excel schema DataFrame that are marked as 'allow-edits' and exist in the table DataFrame.
        """
        tracer, logger = LoggerSingleton.instance(
            NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
        ).initialize_logging_and_tracing()

        with tracer.start_as_current_span("fetch_required_fields"):
            # Column that stores flag indicating if column contains HTML
            column_name_flagging_required = "excel_is_required"
            logger.info(
                f"column_name_flagging_required: {column_name_flagging_required}"
            )

            if column_name_flagging_required in df_table_fields_data_definition.columns:
                # html columns
                df_required_fields_excel_schema = df_table_fields_data_definition[
                    df_table_fields_data_definition[column_name_flagging_required]
                    == "required"
                ]
                required_columns = df_required_fields_excel_schema[
                    "field_name"
                ].tolist()
            else:
                # Assuming you have a DataFrame named 'df_table_fields_data_definition'
                # To list all columns of the DataFrame 'df_table_fields_data_definition'
                column_list = df_table_fields_data_definition.columns.tolist()
                logger.info(str(column_list))
                logger.warning(
                    f"No {column_name_flagging_required} column in Excel schema file"
                )
                required_columns = []

            # Get a list of columns that exist in both df_tables and l
            table_column_names = df_tables.columns.tolist()
            valid_required_fields = [
                col for col in required_columns if col in table_column_names
            ]

            return valid_required_fields

    def fetch_date_fields(self, df_tables, df_table_fields_data_definition):
        """
        Retrieve a list of valid date columns from the Excel schema DataFrame based on the provided table DataFrame.

        This function extracts column names from the Excel schema DataFrame (df_table_fields_data_definition) that are marked with
        'DATE' as the field type ('field_type_alation'). It then checks if these columns exist in the table DataFrame
        (df_tables). If a column is present in both the Excel schema and the table, it is considered a valid date column.

        Additionally, if the 'description' column is not marked as an date column in the schema but is present in the table,
        it is also included in the list of valid date columns.

        Parameters:
            df_table_fields_data_definition (pd.DataFrame): A pandas DataFrame representing the Excel schema with column information.
            df_tables (pd.DataFrame): A pandas DataFrame representing the table for which valid date columns are to be determined.

        Returns:
            list: A list of column names from the Excel schema DataFrame that are marked as 'DATE' and exist in the table DataFrame,
                including the 'description' column if present in the table but not explicitly marked as an date column in the schema.
        """
        tracer, logger = LoggerSingleton.instance(
            NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
        ).initialize_logging_and_tracing()

        with tracer.start_as_current_span("fetch_date_columns"):
            # Column that stores flag indicating if column contains date
            column_name_flagging_date = "field_type_alation"
            logger.info(f"column_name_flagging_date: {column_name_flagging_date}")

            if column_name_flagging_date in df_table_fields_data_definition.columns:
                # date columns
                df_date_fields_excel_schema = df_table_fields_data_definition[
                    df_table_fields_data_definition[column_name_flagging_date] == "DATE"
                ]
                date_columns = df_date_fields_excel_schema["field_name"].tolist()
            else:
                # Assuming you have a DataFrame named 'df_table_fields_data_definition'
                # To list all columns of the DataFrame 'df_table_fields_data_definition'
                column_list = df_table_fields_data_definition.columns.tolist()
                logger.info(str(column_list))
                logger.warning(
                    f"No {column_name_flagging_date} column in Excel schema file"
                )
                date_columns = []

            # Get a list of columns that exist in both df_tables and date_columns
            table_column_names = df_tables.columns.tolist()
            date_fields = [col for col in date_columns if col in table_column_names]

            return date_fields

    def fetch_visible_fields(
        self,
        df_tables,
        df_table_fields_data_definition,
        data_product_id: str,
        environment: str,
    ):
        """
        Retrieve a list of valid date columns from the Excel schema DataFrame based on the provided table DataFrame.

        This function extracts column names from the Excel schema DataFrame (df_table_fields_data_definition) that are marked with
        'DATE' as the field type ('field_type_alation'). It then checks if these columns exist in the table DataFrame
        (df_tables). If a column is present in both the Excel schema and the table, it is considered a valid date column.

        Additionally, if the 'description' column is not marked as an date column in the schema but is present in the table,
        it is also included in the list of valid date columns.

        Parameters:
            df_table_fields_data_definition (pd.DataFrame): A pandas DataFrame representing the Excel schema with column information.
            df_tables (pd.DataFrame): A pandas DataFrame representing the table for which valid date columns are to be determined.

        Returns:
            list: A list of column names from the Excel schema DataFrame that are marked as 'DATE' and exist in the table DataFrame,
                including the 'description' column if present in the table but not explicitly marked as an date column in the schema.
        """
        tracer, logger = LoggerSingleton.instance(
            NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
        ).initialize_logging_and_tracing()

        with tracer.start_as_current_span("fetch_visible_fields"):
            # Column that stores flag indicating if column contains date
            column_name_flagging_visibility = "excel_visbility"
            logger.info(
                f"column_name_flagging_visibility: {column_name_flagging_visibility}"
            )

            if (
                column_name_flagging_visibility
                in df_table_fields_data_definition.columns
            ):
                # date columns
                df_date_fields_excel_schema = df_table_fields_data_definition[
                    df_table_fields_data_definition[column_name_flagging_visibility]
                    == "visible"
                ]
                visible_fields = df_date_fields_excel_schema["field_name"].tolist()
            else:
                # Assuming you have a DataFrame named 'df_table_fields_data_definition'
                # To list all columns of the DataFrame 'df_table_fields_data_definition'
                column_list = df_table_fields_data_definition.columns.tolist()
                logger.info(str(column_list))
                logger.warning(
                    f"No {column_name_flagging_visibility} column in Excel schema file"
                )
                visible_fields = []

            # Get a list of columns that exist in both df_tables and date_columns
            table_column_names = df_tables.columns.tolist()
            visible_fields = [
                col for col in table_column_names if col in visible_fields
            ]

            return visible_fields

    def fetch_valid_object_set_fields(
        self, df_table_fields_data_definition, df_tables, data_product_id, environment
    ):
        """
        Retrieve a list of valid object_set columns from the Excel schema DataFrame based on the provided table DataFrame.

        This function extracts column names from the Excel schema DataFrame (df_table_fields_data_definition) that are marked with
        'OBJECT_SET' as the field type ('field_type_alation'). It then checks if these columns exist in the table DataFrame
        (df_tables). If a column is present in both the Excel schema and the table, it is considered a valid object_set column.

        Additionally, if the 'description' column is not marked as an object_set column in the schema but is present in the table,
        it is also included in the list of valid object_set columns.

        Parameters:
            df_table_fields_data_definition (pd.DataFrame): A pandas DataFrame representing the Excel schema with column information.
            df_tables (pd.DataFrame): A pandas DataFrame representing the table for which valid object_set columns are to be determined.

        Returns:
            list: A list of column names from the Excel schema DataFrame that are marked as 'OBJECT_SET' and exist in the table DataFrame,
                including the 'description' column if present in the table but not explicitly marked as an object_set column in the schema.
        """
        tracer, logger = LoggerSingleton.instance(
            NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
        ).initialize_logging_and_tracing()

        with tracer.start_as_current_span("fetch_valid_object_set_fields"):
            # Column that stores flag indicating if column contains object_set
            column_name_flagging_object_set = "field_type_alation"
            logger.info(
                f"column_name_flagging_object_set: {column_name_flagging_object_set}"
            )

            if (
                column_name_flagging_object_set
                in df_table_fields_data_definition.columns
            ):
                # object_set columns
                df_object_set_fields_excel_schema = df_table_fields_data_definition[
                    df_table_fields_data_definition[column_name_flagging_object_set]
                    == "OBJECT_SET"
                ]
                object_set_columns = df_object_set_fields_excel_schema[
                    "field_name"
                ].tolist()
            else:
                # Assuming you have a DataFrame named 'df_table_fields_data_definition'
                # To list all columns of the DataFrame 'df_table_fields_data_definition'
                column_list = df_table_fields_data_definition.columns.tolist()
                logger.info(str(column_list))
                logger.warning(
                    f"No {column_name_flagging_object_set} column in Excel schema file"
                )
                object_set_columns = []

            # Get a list of columns that exist in both df_tables and object_set_columns
            table_column_names = df_tables.columns.tolist()
            valid_object_set_columns = [
                col for col in object_set_columns if col in table_column_names
            ]

            return valid_object_set_columns

    def fetch_editable_fields(
        self, df_tables, df_table_fields_data_definition, data_product_id, environment
    ):
        """
        Retrieve a list of valid editable columns from the Excel schema DataFrame based on the provided table DataFrame.

        Parameters:
            df_table_fields_data_definition (pd.DataFrame): A pandas DataFrame representing the Excel schema with column information.
            df_tables (pd.DataFrame): A pandas DataFrame representing the table for which valid editable columns are to be determined.

        Returns:
            list: A list of column names from the Excel schema DataFrame that are marked as 'allow-edits' and exist in the table DataFrame.
        """
        tracer, logger = LoggerSingleton.instance(
            NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
        ).initialize_logging_and_tracing()

        with tracer.start_as_current_span("fetch_editable_fields"):
            # Column that stores flag indicating if column contains HTML
            column_name_flagging_editable = "excel_read_only"
            logger.info(
                f"column_name_flagging_editable: {column_name_flagging_editable}"
            )

            if column_name_flagging_editable in df_table_fields_data_definition.columns:
                # html columns
                df_editable_fields_excel_schema = df_table_fields_data_definition[
                    df_table_fields_data_definition[column_name_flagging_editable]
                    == "allow-edits"
                ]
                editable_columns = df_editable_fields_excel_schema[
                    "field_name"
                ].tolist()
            else:
                # Assuming you have a DataFrame named 'df_table_fields_data_definition'
                # To list all columns of the DataFrame 'df_table_fields_data_definition'
                column_list = df_table_fields_data_definition.columns.tolist()
                logger.info(str(column_list))
                logger.warning(
                    f"No {column_name_flagging_editable} column in Excel schema file"
                )
                editable_columns = []

            # Get a list of columns that exist in both df_tables and l
            table_column_names = df_tables.columns.tolist()
            editable_fields = [
                col for col in editable_columns if col in table_column_names
            ]

            valid_required_fields = self.fetch_required_fields(
                df_tables, df_table_fields_data_definition
            )

            # Filter the common elements between editable_fields and valid_required_fields
            editable_fields = [
                field for field in editable_fields if field in valid_required_fields
            ]

            return editable_fields

    def fetch_html_fields(
        self, df_table_fields_data_definition, df_tables, data_product_id, environment
    ):
        """
        Retrieve a list of valid HTML columns from the Excel schema DataFrame based on the provided table DataFrame.

        This function extracts column names from the Excel schema DataFrame (df_table_fields_data_definition) that are marked with
        'RICH_TEXT' as the field type ('field_type_alation'). It then checks if these columns exist in the table DataFrame
        (df_tables). If a column is present in both the Excel schema and the table, it is considered a valid HTML column.

        Additionally, if the 'description' column is not marked as an HTML column in the schema but is present in the table,
        it is also included in the list of valid HTML columns.

        Parameters:
            df_table_fields_data_definition (pd.DataFrame): A pandas DataFrame representing the Excel schema with column information.
            df_tables (pd.DataFrame): A pandas DataFrame representing the table for which valid HTML columns are to be determined.

        Returns:
            list: A list of column names from the Excel schema DataFrame that are marked as 'RICH_TEXT' and exist in the table DataFrame,
                including the 'description' column if present in the table but not explicitly marked as an HTML column in the schema.
        """
        tracer, logger = LoggerSingleton.instance(
            NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
        ).initialize_logging_and_tracing()

        with tracer.start_as_current_span("fetch_html_fields"):
            # Column that stores flag indicating if column contains HTML
            column_name_flagging_html = "field_type_alation"
            logger.info(f"column_name_flagging_html: {column_name_flagging_html}")

            if column_name_flagging_html in df_table_fields_data_definition.columns:
                # HTML columns
                df_html_fields_excel_schema = df_table_fields_data_definition[
                    df_table_fields_data_definition[column_name_flagging_html]
                    == "RICH_TEXT"
                ]
                html_columns = df_html_fields_excel_schema["field_name"].tolist()
            else:
                # Assuming you have a DataFrame named 'df_table_fields_data_definition'
                # To list all columns of the DataFrame 'df_table_fields_data_definition'
                column_list = df_table_fields_data_definition.columns.tolist()
                logger.info(str(column_list))
                logger.warning(
                    f"No {column_name_flagging_html} column in Excel schema file"
                )
                html_columns = []

            # Get a list of columns that exist in both df_tables and html_columns
            table_column_names = df_tables.columns.tolist()
            valid_html_columns = [
                col for col in html_columns if col in table_column_names
            ]

            if "description" not in valid_html_columns:
                valid_html_columns.append("description")

            return valid_html_columns

    def fetch_valueset(self, valueset_name, data_product_id, environment):
        """
        Fetches the valueset data from the specified data product and environment.

        Args:
            valueset_name (str): The name of the valueset to fetch.
            data_product_id (str): The ID of the data product.
            environment (str): The environment to fetch the valueset from.

        Returns:
            tuple: A tuple containing the DataFrame of the valueset fields and the path of the data definition file.
        """

        tracer, logger = LoggerSingleton.instance(
            NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
        ).initialize_logging_and_tracing()

        with tracer.start_as_current_span("fetch_valueset_" + valueset_name):
            # Change the current working directory to the project root directory
            os.chdir(project_root)
            # Get the file utility object
            obj_file = cdc_env_file.EnvironmentFile()

            # Get the manifest file
            data_definition_file = self.data_definition_file_path
            directory = os.path.dirname(data_definition_file) + "/"
            directory = obj_file.convert_to_current_os_dir(
                directory, data_product_id, environment
            )
            data_definition_file_valuesets = (
                directory + "excel_data_defintion_for_valuesets.xlsx"
            )
            running_local = config.get("running_local")
            file_exists = obj_file.file_exists(
                running_local,
                data_definition_file_valuesets,
                data_product_id,
                environment,
            )
            logger.info(f"file_exists: {file_exists}")
            df_fields_excel_table = pd.read_excel(
                data_definition_file_valuesets, valueset_name
            )
            return df_fields_excel_table, data_definition_file

    def fetch_schema_tables(
        self,
        edc_alation_api_token,
        edc_alation_base_url,
        alation_datasource_id,
        alation_schema_id,
        schema_results,
        data_product_id,
        environment,
    ):
        """
        Fetches tables associated with a specific schema from Alation using the given details.

        This function communicates with Alation's integration API to gather tables linked to the provided schema (alation_schema_id)
        within the mentioned datasource (alation_datasource_id). It requires authentication and configuration details to access the Alation API.

        Parameters:
            edc_alation_api_token (str): The API token to authenticate with Alation.
            edc_alation_base_url (str): The base URL of the Alation instance.
            alation_datasource_id (int): The ID of the datasource in Alation containing the target schema.
            alation_schema_id (int): The ID of the schema in Alation from which tables need to be retrieved.
            schema_results: Results from a previous query or API call related to the schema. This is used to further refine the data extraction.

        Returns:
            tuple: A tuple containing a pandas DataFrame and a dictionary.
                - pandas.DataFrame: Contains the tables linked to the given schema. The DataFrame is structured such that each row represents
                  a table, and columns denote various table attributes, including any custom fields if present.
                - dict: Maps table names to their respective details.

        Note:
            This function requires the 'requests' and 'pandas' libraries for API communications and data processing, respectively.

        Raises:
            requests.exceptions.RequestException: If any error occurs during the Alation API call.
            json.JSONDecodeError: If there's an issue decoding the JSON response.
            ValueError: If an invalid table processing object is encountered.

        Example:
            api_token = "your_api_token"
            base_url = 'https://your_alation_instance.com'
            datasource_id = 123
            schema_id = 456
            schema_results_data = {...}  # some previous results or API response
            df_tables, tables_dict = fetch_schema_tables(api_token, base_url, datasource_id, schema_id, schema_results_data)
        """
        tracer, logger = LoggerSingleton.instance(
            NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
        ).initialize_logging_and_tracing()

        with tracer.start_as_current_span("fetch_schema_tables"):
            try:
                schema_result_json = schema_results.json()
                schema_custom_fields = schema_result_json[0].get("custom_fields")
                schema_steward_list = None
                if schema_custom_fields is not None:
                    schema_steward_list = [
                        item["value"]
                        for item in schema_custom_fields
                        if item["field_name"] == "Steward"
                    ]
                    # if list of 1 set to first value
                    if len(schema_steward_list) == 1 and isinstance(
                        schema_steward_list[0], list
                    ):
                        schema_steward_list = schema_steward_list[0]

                    if schema_steward_list:
                        logger.info(f"schema_steward_list: {str(schema_steward_list)}")
                    else:
                        logger.info(f"schema_steward_list not found")

                # setting the base_url so that all we need to do is swap API endpoints
                # Set the headers for the request
                headers = {"accept": "application/json", "Token": edc_alation_api_token}

                limit = 500
                skip = 0

                # Create a dictionary to hold the parameters
                params = {}
                params["limit"] = limit
                params["skip"] = skip
                params["schema_id"] = alation_schema_id
                params["ds_id"] = alation_datasource_id

                # make the API call

                obj_environment_http = cdc_env_http.EnvironmentHttp()
                api_url = f"{edc_alation_base_url}/integration/v2/table/"
                tables_result = obj_environment_http.get(
                    api_url, headers=headers, params=params, timeout=REQUEST_TIMEOUT
                )

                # convert the response to a python dict.
                tables_result_json = tables_result.json()
                expanded_json = []
                for existing_table_item in tables_result_json:
                    new_item = existing_table_item.copy()  # start with existing fields

                    table_steward_list = None  # Initialize the variable here
                    for custom_field in new_item["custom_fields"]:
                        # handle stewards
                        if custom_field["field_name"] == "Steward":
                            table_steward_list = custom_field["value"]

                            # Create a list of unique otype and oid combinations from table_steward_list
                            combinations = {
                                (item["otype"], item["oid"])
                                for item in schema_steward_list + table_steward_list
                            }

                            # Add items from schema_steward_list to table_steward_list if not present
                            for combined_item in combinations:
                                search_otype = combined_item[0]
                                search_oid = combined_item[1]
                                found_table_items = [
                                    table_item
                                    for table_item in table_steward_list
                                    if table_item.get("otype") == search_otype
                                    and table_item.get("oid") == search_oid
                                ]

                                if not found_table_items:
                                    for (
                                        schema_item
                                    ) in (
                                        schema_steward_list
                                    ):  # corrected to schema_steward_list
                                        item_copy = schema_item.copy()
                                        item_copy["is_inherited"] = "inherited"
                                        table_steward_list.append(item_copy)
                                else:
                                    # The item exists in table_steward_list, set is_inherited to empty string
                                    found_table_items[0]["is_inherited"] = ""

                            # Modify 'Steward' field_name to 'Steward_Initial'
                            custom_field["field_name"] = "Steward_Initial"

                    # Add new 'Steward' attribute with value "merged" if table_steward_list is not None
                    if table_steward_list is not None:
                        new_item["custom_fields"].append(
                            {"field_name": "Steward", "value": table_steward_list}
                        )

                    # Promote custom fields to the table level
                    for field in existing_table_item["custom_fields"]:
                        # add custom fields
                        new_item[field["field_name"]] = field["value"]

                    expanded_json.append(new_item)

                # Convert to dataframe
                df_tables = json_normalize(expanded_json)

                # Create dictionary legacy functions
                tables_dict = {}
                for table_to_process in tables_result_json:
                    # Assuming table_to_process is the object causing the error
                    if isinstance(table_to_process, dict):
                        table_name = table_to_process.get("name")
                        if table_name:
                            tables_dict[table_name] = table_to_process
                    else:
                        # Handle the case when table_to_process is not a dictionary
                        error_msg = (
                            f"Invalid table_to_process object: {table_to_process}"
                        )
                        raise ValueError(error_msg)

                return df_tables, tables_dict

            except json.JSONDecodeError as err:
                error_msg = f"JSON Decode occurred: {err}"
                exc_info = sys.exc_info()
                LoggerSingleton.instance(
                    NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
                ).error_with_exception(error_msg, exc_info)
                raise
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

    def fetch_schema_tables_extended(
        self,
        edc_alation_api_token,
        edc_alation_base_url,
        alation_datasource_id,
        alation_schema_id,
        schema_results,
        data_product_id,
        environment,
    ):
        """
        Fetches tables for a specified schema from Alation, processes and matches them with a predefined Excel schema.

        This function retrieves tables related to a specified schema from Alation for further Excel processing.
        It starts by fetching the schema tables, then gets the expected table structure from an Excel structure file.
        The function processes and matches the data with the predefined Excel schema, ensuring that the columns are
        in the desired order. The data is then parsed, cleaned, and prepared for output, handling various data types
        like HTML and JSON. The final dataframe is printed, showcasing the tables sorted based on the Excel schema's order.

        Args:
            edc_alation_api_token (str): API token for the EDC Alation integration.
            edc_alation_base_url (str): Base URL for the EDC Alation.
            alation_datasource_id (int): The Alation ID of the datasource to fetch tables from.
            alation_schema_id (int): The Alation ID of the schema to fetch tables from.
            schema_results: Results obtained for the schema. (Expected type needs to be provided)

        Returns:
            tuple: Contains:
                - DataFrame: Processed dataframe containing the tables.
                - List: Columns that are suggested to be hidden.
                - DataFrame: Dataframe representing the field definitions from Excel.

        Raises:
            AssertionError: An error occurs if the status code from the token endpoint is not 200.
            ValueError: Errors that arise from parsing non-HTML content.
            Exception: General exceptions are logged with their error messages.

        Note:
            The function utilizes the BeautifulSoup library to handle and parse HTML content and json library for JSON content.
        """

        tracer, logger = LoggerSingleton.instance(
            NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
        ).initialize_logging_and_tracing()

        with tracer.start_as_current_span("fetch_schema_tables_extended"):
            write_to_debug_excel = False

            #############################
            # Get Raw data from API
            #############################

            # Get db tables from Alation for the specfied db schema
            df_tables, tables_dict = self.fetch_schema_tables(
                edc_alation_api_token,
                edc_alation_base_url,
                alation_datasource_id,
                alation_schema_id,
                schema_results,
            )

            # Save to excel for debugging
            # Define an Excel writer object
            if write_to_debug_excel:
                with pd.ExcelWriter(
                    "debug_df_tables.xlsx", engine="openpyxl"
                ) as writer:
                    # Save the entire DataFrame to the first sheet
                    df_tables.to_excel(writer, sheet_name="df_tables", index=False)

                    # Save only the columns (as a list) to the second sheet
                    pd.DataFrame(df_tables.columns, columns=["Column Names"]).to_excel(
                        writer, sheet_name="columns", index=False
                    )

            #############################
            # Get Expected data from data definition file
            #############################

            # Get expected table structure from Excel structure file
            (
                df_table_fields_data_definition,
                excel_data_definition_file,
            ) = self.fetch_table_definitions()

            if write_to_debug_excel:
                # Save to excel for debugging
                df_tables.to_excel(
                    "debug_df_table_fields_data_definition.xlsx", engine="openpyxl"
                )

            # Get ordered columns
            df_ordered_columns = df_table_fields_data_definition[
                df_table_fields_data_definition["excel_column_order"] > 0
            ]

            # Create a list of column names from df_table_fields_data_definition in the order specified by excel_column_order
            ordered_columns = df_ordered_columns.sort_values("excel_column_order")[
                "field_name"
            ].tolist()

            # Save to excel for debugging
            df_ordered_columns = pd.DataFrame(
                ordered_columns, columns=["ordered_columns"]
            )

            if write_to_debug_excel:
                df_ordered_columns.to_excel(
                    "debug_df_ordered_columns.xlsx", engine="openpyxl"
                )

            # Get a list of columns that exist in both df_tables and ordered_columns
            table_column_names = df_tables.columns.tolist()

            # Get the intersection of columns_expected and columns_present to preserve valid column order
            columns_undesired = [
                col for col in table_column_names if col not in ordered_columns
            ]

            # Get the list of columns not in valid_columns and append them at the end
            columns_desired = [
                col for col in ordered_columns if col not in table_column_names
            ]

            # Add columns_desired with NaN values
            for col in columns_desired:
                df_tables[col] = np.nan

            # Reorder the DataFrame columns using the desired order
            df_tables_enriched = df_tables[ordered_columns + columns_undesired]

            if write_to_debug_excel:
                # Define an Excel writer object
                with pd.ExcelWriter(
                    "debug_df_tables_enriched.xlsx", engine="openpyxl"
                ) as writer:
                    # Save the entire DataFrame to the first sheet
                    df_tables_enriched.to_excel(
                        writer, sheet_name="df_tables_enriched", index=False
                    )

                    # Save only the columns (as a list) to the second sheet
                    pd.DataFrame(
                        df_tables_enriched.columns, columns=["Column Names"]
                    ).to_excel(writer, sheet_name="columns", index=False)

            # Get valid object_set columns from expected table structure
            visible_fields = self.fetch_visible_fields(
                df_table_fields_data_definition, df_tables_enriched
            )

            extended_table_column_names = df_tables_enriched.columns.tolist()

            # Create a list of columns to hide from df_tables
            hidden_fields = [
                col for col in extended_table_column_names if col not in visible_fields
            ]

            if write_to_debug_excel:
                # Save to excel for debugging
                df_hidden_fields = pd.DataFrame(
                    hidden_fields, columns=["hidden_fields"]
                )
                df_hidden_fields.to_excel(
                    "debug_df_hidden_fields.xlsx", engine="openpyxl"
                )

            #############################
            # Handle HTML and JSON data
            #############################

            # Get valid object_set columns from expected table structure
            valid_object_set_columns = self.fetch_valid_object_set_fields(
                df_table_fields_data_definition, df_tables_enriched
            )

            # Save to excel for debugging
            if write_to_debug_excel:
                df_valid_object_set_columns = pd.DataFrame(
                    valid_object_set_columns, columns=["valid_object_set_columns"]
                )
                df_valid_object_set_columns.to_excel(
                    "debug_df_valid_object_set_columns.xlsx", engine="openpyxl"
                )

            # get users lookup table / valueset table
            df_users, data_definition_file = self.fetch_valueset("User")

            # Convert valid object_set columns
            for column in valid_object_set_columns:
                # for each row in the column
                for idx in df_tables_enriched.index:
                    # Get the value at the current cell
                    cell_value = df_tables_enriched.loc[idx, column]
                    try:
                        # Try to parse it as HTML
                        if cell_value is None:
                            cell_value = ""

                        if not isinstance(cell_value, (list, np.ndarray)):
                            if pd.isna(cell_value):
                                cell_value = ""

                        if isinstance(cell_value, str):
                            cell_value = self.wrap_in_brackets(cell_value)
                            # Parse the JSON string into a Python dictionary
                            parsed_data = json.loads(cell_value)
                        else:
                            parsed_data = cell_value

                        if column == "Steward":
                            # Create a dataframe from the list of dictionaries
                            df_stewards = pd.DataFrame(parsed_data)

                            # Perform left join on 'oid' (from df_stewards) and 'user_id' (from df_users)
                            merged_df = df_stewards.merge(
                                df_users, left_on="oid", right_on="user_id", how="left"
                            )

                            # Drop the redundant 'oid' column from df_users
                            merged_df.drop(columns="user_id", inplace=True)

                            # Create the comma-delimited list in the desired format
                            user_list = [
                                f"{row['user_full_name']} ({row['user_email']}:{row['oid']})"
                                for _, row in merged_df.iterrows()
                            ]

                            # Join the list elements with commas
                            comma_delimited_list = ", ".join(user_list)

                            # Replace the cell value with the parsed HTML
                            # This assumes that you want the first table, as pd.read_html returns a list of tables

                        df_tables_enriched.loc[idx, column] = comma_delimited_list

                    except Exception as ex:
                        error_msg = f"Error: {str(ex)}"
                        exc_info = sys.exc_info()
                        logger_singleton.error_with_exception(error_msg, exc_info)
                        pass

            # Get valid html columns from expected table structure
            valid_html_columns = self.fetch_html_fields(
                df_table_fields_data_definition, df_tables_enriched
            )

            # Convert valid html columns
            for column in valid_html_columns:
                # for each row in the column
                for idx in df_tables_enriched.index:
                    # Get the value at the current cell
                    cell_value = df_tables_enriched.loc[idx, column]
                    try:
                        # Try to parse it as HTML
                        if cell_value is None:
                            cell_value = ""

                        if pd.isna(cell_value):
                            cell_value = ""

                        soup = BeautifulSoup(cell_value, "html.parser")

                        # Check if 'html' and 'body' tags exist
                        if not soup.html:
                            soup = BeautifulSoup(
                                "<html><body>" + str(soup) + "</body></html>",
                                "html.parser",
                            )

                        # Extract text from the HTML document
                        text = soup.get_text()

                        # Replace the cell value with the parsed HTML
                        # This assumes that you want the first table, as pd.read_html returns a list of tables
                        df_tables_enriched.loc[idx, column] = text
                    except ValueError:
                        # pd.read_html throws a ValueError if it can't parse the input as HTML
                        # If this happens, we'll just leave the cell value as it is
                        pass

            # Set the option to display all columns
            pd.set_option("display.max_columns", None)
            df_tables_formatted = df_tables_enriched.fillna("")

            # Define an Excel writer object
            if write_to_debug_excel:
                with pd.ExcelWriter(
                    "debug_df_tables_formatted.xlsx", engine="openpyxl"
                ) as writer:
                    # Save the entire DataFrame to the first sheet
                    df_tables_formatted.to_excel(
                        writer, sheet_name="df_tables_formatted", index=False
                    )

                    # Save only the columns (as a list) to the second sheet
                    pd.DataFrame(
                        df_tables_formatted.columns, columns=["Column Names"]
                    ).to_excel(writer, sheet_name="columns", index=False)

            df_tables_formatted = df_tables_formatted.sort_values(by="name")
            logger.info(f"df_tables_formatted: {df_tables_formatted}")
            return df_tables_formatted, hidden_fields, df_table_fields_data_definition

    def format_description(self, table_json):
        """
        Formats the description for the table.

        Args:
            table_json (dict): The JSON data representing the table.

        Returns:
            str: The formatted description string.

        Raises:
            Exception: If an error occurs while formatting the description.

        """

        tracer, logger = LoggerSingleton.instance(
            NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
        ).initialize_logging_and_tracing()

        with tracer.start_as_current_span("format_description"):
            try:
                description = table_json.get("description")
                if self.extra_description_fields:
                    description += "<br><table><tr><th>Field</th><th>Value</th></tr>"
                    for key in self.extra_description_fields:
                        description += (
                            "<tr><td>"
                            + key
                            + "</td><td>"
                            + self.extra_description_fields[key]
                            + "</td></tr>"
                        )
                    description += "</table>"
                return description
            except Exception as ex:
                error_msg = "Error: %s", ex
                exc_info = sys.exc_info()
                LoggerSingleton.instance(
                    NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
                ).error_with_exception(error_msg, exc_info)
                raise

    def get_alation_data(self):
        """
        Retrieves the title and description from the instance.

        This function checks the 'title' and 'description' attributes of the instance and returns a dictionary that includes
        'title' and 'description' keys, each with their respective values, only if the values are not None.
        It includes keys whose values are empty strings.

        Returns:
            dict: A dictionary with 'title' and 'description' keys. The dictionary will not include keys whose values are None.
            If both 'title' and 'description' are None, an empty dictionary is returned.
        """
        return {
            k: v
            for k, v in {"title": self.title, "description": self.description}.items()
            if v is not None
        }

    def get_table_extra_description_columns(self, table_json):
        extra_description_fields = {}
        if "extraDescriptionFields" in table_json:
            optional_description_fields = table_json["extraDescriptionFields"]
            print("Extra description fields: ", optional_description_fields)
            for key in optional_description_fields:
                extra_description_fields[key] = optional_description_fields[key]
        return extra_description_fields

    @staticmethod
    def update_table_structure(
        edc_alation_api_token,
        edc_alation_base_url,
        alation_datasource_id,
        schema_name,
        table,
        force_submit,
        obj_custom_fields_endpoint,
        editable_fields,
        table_name,
        date_fields,
        data_product_id,
        environment,
    ):
        """
        Updates the structure of a table in Alation.

        This method updates the table information, applies tags to the table, and
        updates the columns of the table. It uses Alation's custom fields API
        endpoint for updating the table and columns and applies tags using Alation's
        tags API endpoint.

        Parameters:
        alation_datasource_id (int): The ID of the Alation data source where the table resides.
        schema_name (str): The name of the schema where the table resides.
        edc_alation_edc_alation_edc_alation_api_access_token (str): The API access token for Alation.
        edc_alation_base_url (str): The base URL for Alation's API.
        unposted_table (Table): The table object that contains the updated structure.

        Returns:
        int: HTTP status code of the operation. 200 indicates success.
        str: Status message of the operation. "OK" indicates success.
        """

        tracer, logger = LoggerSingleton.instance(
            NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
        ).initialize_logging_and_tracing()
        with tracer.start_as_current_span("upload_schema_manifest"):
            try:
                if table_name is None:
                    raise ValueError("table_name cannot be None.")

                id_finder_endpoint = IdFinder(
                    edc_alation_api_token, edc_alation_base_url
                )
                tags_endpoint = Tags(edc_alation_api_token, edc_alation_base_url)

                if (
                    schema_name == "object_name_is_missing"
                    or schema_name == "object name is missing"
                ):
                    raise ValueError("Invalid schema_name value.")

                # encode the schema
                if "." in schema_name and ENCODE_PERIOD:
                    encoded_schema_name = f'"{schema_name}"'
                else:
                    encoded_schema_name = schema_name

                # encode the table
                special_chars = set("!\"#$%&\\'()*+,-./:;<=>?@[\\]^_`{}~")

                if any(char in special_chars for char in table_name) and ENCODE_PERIOD:
                    encoded_table_name = f'"{table_name}"'
                else:
                    encoded_table_name = table_name

                key = f"{encoded_schema_name}.{encoded_table_name}"
                # Update the table
                # Should only be one - ensure force_submit
                # Todo: Implement schema authorization
                response_content = obj_custom_fields_endpoint.update(
                    edc_alation_api_token,
                    edc_alation_base_url,
                    "table",
                    alation_datasource_id,
                    key,
                    table,
                    force_submit=force_submit,
                    editable_fields=editable_fields,
                    date_fields=date_fields,
                )

                last_result = response_content
                logger.info(f"response_content: {response_content}")

                # Update the tags
                # Encode ignoring ENCODE_PERIOD
                # encode the schema
                if "." in schema_name:
                    encoded_schema_name = f'"{schema_name}"'
                else:
                    encoded_schema_name = schema_name

                if "." in table_name:
                    encoded_table_name = f'"{table_name}"'
                else:
                    encoded_table_name = table_name

                table_key = f"{alation_datasource_id}.{encoded_schema_name}.{encoded_table_name}"

                if isinstance(table, Table):
                    if table.tags is not None:
                        table_id = id_finder_endpoint.find("table", table_key)
                        for table_tag in table.tags:
                            tags_endpoint.apply("table", table_id, table_tag)

                    from cdh_lava_core.alation_service.db_column import Column

                    # Update the columns to convert string to objects if necessary
                    columns_dict = table.columns
                else:
                    columns_dict = table

                # # Update the columns
                # if columns_dict is not None:

                #     # Using ThreadPoolExecutor
                #     num_threads = min(NUM_THREADS_MAX, len(columns_dict))

                #     if '.' in schema_name and ENCODE_PERIOD:
                #         encoded_schema_name = f"\"{schema_name}\""
                #     else:
                #         encoded_schema_name = schema_name

                #     special_chars = set('!"#$%&\'()*+,-./:;<=>?@[\]^_`{}~')

                #     if any(char in special_chars for char in table_name) and ENCODE_PERIOD:
                #         encoded_table_name = f"\"{table_name}\""
                #     else:
                #         encoded_table_name = table_name

                #     with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
                #         last_future_result = ""
                #         futures = []
                #         total_items = len(columns_dict.items())
                #         special_chars = set(
                #             '!"#$%&\\\'()*+,-./:;<=>?@[\\]^_`{}~')

                #         for idx, (key, value) in enumerate(columns_dict.items()):
                #             # Set force_submit to True on the last item
                #             force_submit = (idx == total_items - 1)
                #             if any(char in special_chars for char in key) and ENCODE_PERIOD:
                #                 encoded_column_name = f"\"{key}\""
                #             else:
                #                 encoded_column_name = key

                #             future = executor.submit(obj_custom_fields_endpoint.update, edc_alation_api_token, edc_alation_base_url, "attribute",
                #                                      alation_datasource_id,
                #                                      f"{encoded_schema_name}.{encoded_table_name}.{encoded_column_name}",
                #                                      value, force_submit=force_submit, editable_fields=editable_fields)
                #             futures.append(future)

                #         # Wait for all futures to complete
                #         concurrent.futures.wait(futures)

                #         # Retrieve the result of the last future
                #         if futures:
                #             last_future_result = futures[-1].result()
                #         else:
                #             last_future_result = "No return value from last update call"

                #         last_result = str(last_result) + \
                #             str(last_future_result)

                # else:
                #     warning_msg = f"No columns supplied to update for table: {table_name}"
                #     logger.warning(warning_msg)
                #     last_result = str(last_result) + warning_msg

                return last_result

            except Exception as ex:
                error_msg = (f"Error: {str(ex)}",)
                exc_info = sys.exc_info()
                LoggerSingleton.instance(
                    NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
                ).error_with_exception(error_msg, exc_info)
                raise

    @staticmethod
    def wrap_in_brackets(text):
        """
        Wrap a given string in brackets if they are not already present.

        Parameters:
            text (str): The input string to be wrapped in brackets.

        Returns:
            str: The input string wrapped in brackets, or the original string if it already has brackets.

        Example:
            # Test cases
            text1 = "Hello, world!"
            text2 = "(Welcome to the party)"
            text3 = "Python is awesome"

            print(wrap_in_brackets(text1))  # Output: "(Hello, world!)"
            print(wrap_in_brackets(text2))  # Output: "(Welcome to the party)"
            print(wrap_in_brackets(text3))  # Output: "(Python is awesome)"

        Note:
            This method checks if the input string starts with an opening bracket '(' and ends with a closing bracket ')'.
            If the brackets are not present, the method wraps the string in brackets using string formatting (f'({text})').
            If the string is already wrapped in brackets, the method returns the original string as it is.
        """
        if text.startswith("[") and text.endswith("]"):
            return text  # The string is already wrapped in brackets, return as it is
        else:
            return f"[{text}]"  # Wrap the string in brackets and return
