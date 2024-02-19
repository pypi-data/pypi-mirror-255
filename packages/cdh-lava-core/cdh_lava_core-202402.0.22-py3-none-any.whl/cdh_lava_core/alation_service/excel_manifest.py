import os
import sys
from pathlib import Path
import pandas as pd
import numpy as np
import xlsxwriter
import xlsxwriter.utility
from datetime import datetime, timedelta, date

from cdh_lava_core.cdc_log_service.environment_logging import LoggerSingleton

from cdh_lava_core.alation_service import (
    db_table as alation_table,
    db_schema as alation_schema,
)

from cdh_lava_core.cdc_tech_environment_service import environment_file as cdc_env_file
from cdh_lava_core.alation_service.token import TokenEndpoint

# Get the currently running file name
NAMESPACE_NAME = os.path.basename(os.path.dirname(__file__))
# Get the parent folder name of the running file
SERVICE_NAME = os.path.basename(__file__)
TIMEOUT_ONE_MIN = 60  # or set to whatever value you want
ENVIRONMENT = "dev"


# Get the absolute path of the current script
current_script_path = os.path.abspath(__file__)

# Get the project root directory by going up one or more levels
project_root = os.path.dirname(os.path.dirname(current_script_path))

# Change the current working directory to the project root directory
os.chdir(project_root)
REPOSITORY_PATH_DEFAULT = str(Path(os.getcwd()))


class ManifestExcel:
    """
    This class encapsulates the functionalities to generate Excel file data for a given Alation schema ID and
    configuration, and to create an Excel file using the data generated.

    The class includes the following methods:
    - convert_dict_to_csv: A static method that takes a dictionary as input and converts it to a string
      representation in the CSV format.
    - generate_excel_file_data: A class method that generates data for an Excel file given a Alation schema ID
      and configuration. It uses data from Alation and builds DataFrames to represent the schema and table data.
      It returns a tuple containing the DataFrame containing the schema data, the DataFrame containing the
      table data, and the filename of the generated Excel file.
    - create_excel_from_data: A class method that generates an Excel file using DataFrame objects and
      saves it.

    This class is typically used in scenarios where data from an Alation schema needs to be exported as an Excel file
    for further analysis or manipulation. The Excel file created includes two sheets, namely 'Instructions'
    and 'Tables', which hold the schema and table data respectively.

    Note:
    - The generate_excel_data method assumes the existence of an `alation_schema` module with a `Schema` class.
    - This method relies on external logging and tracing modules (`logger_singleton` and `tracer_singleton`) that
      are not provided here.
    - The configuration dictionary (`config`) is expected to contain specific keys such as 'repository_path',
      'environment', 'edc_alation_user_id', 'edc_alation_base_url', etc.
    - The methods make use of the `pd.DataFrame` function from the `pandas` library to create DataFrames.
    - The create_excel_from_data method uses the xlsxwriter library to create and manipulate the Excel file.
    - The get_column_letter function is assumed to be imported from the openpyxl.utils module.
    """

    @staticmethod
    def convert_dict_to_csv(dictionary):
        """
        Convert a dictionary to a CSV string.

        Args:
            dictionary (dict): The dictionary to be converted.

        Returns:
            str: The CSV string representation of the dictionary.

        Raises:
            None

        """
        return "UNSUPPORTED LIST"

        if isinstance(dictionary, dict):
            csv_rows = []
            for key, value in dictionary.items():
                csv_row = f"{key}:{value}"
                csv_rows.append(csv_row)
            csv_data = ",".join(csv_rows)
            return csv_data
        else:
            return None

    @classmethod
    def generate_excel_file_data(
        cls, alation_schema_id, config, json_data_definition_file_path
    ):
        """
        Generate Excel file data for the given Alation schema ID and configuration.

        Args:
            alation_schema_id (int): The ID of the Alation schema.
            config (dict): A dictionary containing the configuration settings.

        Returns:
            tuple: A tuple containing the following elements:
                - df_schema (pandas.DataFrame): The DataFrame containing the schema data.
                - df_tables (pandas.DataFrame): The DataFrame containing the table data.
                - manifest_excel_file (str): The file name of the generated Excel file.

        Raises:
            Exception: If there is an error during the generation process.

        This method generates Excel file data for the specified Alation schema ID and configuration settings.
        It retrieves the necessary data from Alation using the provided credentials and builds DataFrames
        to represent the schema and table data.

        The method returns a tuple containing the following elements:
        - df_schema: The DataFrame containing the schema data with columns 'type', 'field_name', and 'value'.
        - df_tables: The DataFrame containing the table data with columns based on the dictionary keys.
        - manifest_excel_file: The file name of the generated Excel file.

        Note:
        - This method assumes the existence of an `alation_schema` module with a `Schema` class.
        - The method relies on external logging and tracing modules (`logger_singleton` and `tracer_singleton`) that are not provided here.
        - The configuration dictionary (`config`) is expected to contain specific keys such as 'repository_path', 'environment', 'edc_alation_user_id', 'edc_alation_base_url', etc.
        - The method makes use of the `pd.DataFrame` function from the `pandas` library to create DataFrames.
        """

        from cdh_lava_core.alation_service import db_schema as alation_schema

        schema = alation_schema.Schema()

        tracer, logger = LoggerSingleton.instance(
            NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
        ).initialize_logging_and_tracing()

        schema_id = alation_schema_id
        schema_name = None
        alation_datasource_id = None
        edc_alation_api_token = None
        schema_result = None
        datasource_result = None
        with tracer.start_as_current_span("generate_excel_file_data"):
            try:
                # Get Parameters
                repository_path = config.get("repository_path")
                environment = config.get("environment")
                alation_user_id = config.get("edc_alation_user_id")
                edc_alation_base_url = config.get("edc_alation_base_url")
                token_endpoint = TokenEndpoint(edc_alation_base_url)
                (
                    status_code,
                    edc_alation_api_token,
                    api_refresh_token,
                ) = token_endpoint.get_api_token_from_config(config)

                print(
                    f"edc_alation_api_token_length: {str(len(edc_alation_api_token))}"
                )
                print(f"api_refresh_token_length: {str(len(api_refresh_token))}")
                assert status_code == 200

                # Get Datasource and Schema Results
                schema_result, datasource_result = schema.fetch_schema(
                    edc_alation_api_token, edc_alation_base_url, schema_id
                )

                schema_result_json = schema_result.json()
                alation_datasource_id = schema_result_json[0].get("ds_id")

            except Exception as ex_generic:
                error_msg = (str(ex_generic),)
                exc_info = sys.exc_info()
                LoggerSingleton.instance(
                    NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
                ).error_with_exception(error_msg, exc_info)
                raise

            try:
                ##########################################################
                # Get Schema Data Frame
                ##########################################################

                schema_result_json = schema_result.json()
                schema_name = schema_result_json[0].get("name")

                datasource_title = datasource_result.get("title")

                # Create schema result dictionary
                simple_dict = {
                    i: (k, v)
                    for i, (k, v) in enumerate(schema_result.json()[0].items())
                    if not isinstance(v, list) and not isinstance(v, dict)
                }
                custom_dict = schema_result.json()[0]["custom_fields"]

                # Get Excel File Name using schema name
                manifest_excel_file = schema.get_excel_manifest_file_path(
                    "download",
                    repository_path,
                    datasource_title,
                    schema_name,
                    environment,
                    alation_user_id,
                )

                #  Create schema result data frame
                df_schema_standard = pd.DataFrame.from_dict(
                    simple_dict, orient="index", columns=["field_name", "value"]
                )

                # Add column 'type' to the DataFrame for standard fields
                df_schema_standard = df_schema_standard.assign(type="standard")

                # Create custom fields DataFrame
                df_schema_custom = pd.DataFrame(custom_dict)

                # Add column 'type' to the DataFrame for custom fields
                df_schema_custom = df_schema_custom.assign(type="custom")

                # Select columns 'type', 'field_name', and 'value' from each DataFrame
                df_custom_selected = df_schema_custom[["type", "field_name", "value"]]
                df_standard_selected = df_schema_standard[
                    ["type", "field_name", "value"]
                ]

                # Concatenate the two selected DataFrames
                concatenated_df = pd.concat([df_custom_selected, df_standard_selected])

                # Sort the concatenated DataFrame based on 'type' and 'field_name'
                df_schema = concatenated_df.sort_values(
                    ["type", "field_name"], ascending=[False, True]
                )

                # Loop through each column and
                for column in df_schema.columns:
                    # convert numeric values to 0
                    if np.issubdtype(df_schema[column].dtype, np.number):
                        df_schema[column].fillna(0, inplace=True)
                    # convert dictionary objects to string
                    if df_schema[column].dtype == "object":
                        df_schema[column] = df_schema[column].apply(
                            lambda x: cls.convert_dict_to_csv(x)
                            if isinstance(x, dict)
                            else x
                        )
                        df_schema[column] = df_schema[column].astype(str)

                ##########################################################
                # Get Tables Data Frame
                ##########################################################

                # Initialize table object
                table = alation_table.Table(None, json_data_definition_file_path)

                # Get tables
                (
                    df_tables,
                    hidden_fields,
                    df_table_fields_data_definition,
                ) = table.fetch_schema_tables_extended(
                    edc_alation_api_token,
                    edc_alation_base_url,
                    alation_datasource_id,
                    alation_schema_id,
                    schema_result,
                )

                ##########################################################
                # Get Columns Data Frame
                ##########################################################

                # Select all tables if
                alation_table_id = -1

                # Get table columns
                (
                    df_columns,
                    df_column_fields_data_definition,
                ) = table.fetch_table_columns_extended(
                    edc_alation_api_token,
                    edc_alation_base_url,
                    alation_datasource_id,
                    alation_schema_id,
                    alation_table_id,
                    schema_result,
                )

                # Return DataFrames
                return (
                    df_schema,
                    df_tables,
                    manifest_excel_file,
                    df_table_fields_data_definition,
                    df_columns,
                    df_column_fields_data_definition,
                )

            except Exception as ex:
                error_msg = ("Error: {str(ex)}",)
                exc_info = sys.exc_info()
                LoggerSingleton.instance(
                    NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
                ).error_with_exception(error_msg, exc_info)
                raise

    @classmethod
    def read_manifest_excel_file_tables_worksheet(cls, manifest_excel_file):
        tracer, logger = LoggerSingleton.instance(
            NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
        ).initialize_logging_and_tracing()

        with tracer.start_as_current_span("read_excel_file_data_for_tables"):
            worksheet_name = "Tables"
            # Read the Excel file into a dataframe, starting from cell E7
            # Skip the first 6 rows to start from E7
            df_tables = pd.read_excel(
                manifest_excel_file, sheet_name=worksheet_name, skiprows=6
            )

            # Drop the first column
            df_tables.drop(df_tables.columns[0], axis=1, inplace=True)

            # Rename columns containing "(Read-Only)" and remove the "(Read-Only)" part
            df_tables.columns = df_tables.columns.str.replace(
                r"\s*\(Read-Only\)\s*", "", regex=True
            )

            logger.info(f"df_tables length: {len(df_tables.columns)}")

            # Now, 'df_tables' contains the data from the Excel file starting from cell E7
            return df_tables

    @classmethod
    def create_excel_from_data(
        cls,
        config,
        df_tables,
        manifest_excel_file,
        df_table_fields_data_definition,
        df_columns,
        df_column_fields_data_definition,
    ):
        """
        Generate an Excel file using the given DataFrame objects and save it.

        Args:
            df_schema (pandas.DataFrame): The DataFrame containing schema data.
            df_tables (pandas.DataFrame): The DataFrame containing table data.
            manifest_excel_file (str): The file path to save the generated Excel file.

        Returns:
            str: The file path of the generated Excel file.

        Raises:
            None

        This method takes two DataFrame objects, `df_schema` and `df_tables`, and a file path `manifest_excel_file`.
        It generates an Excel file using the data from the DataFrames and saves it to the specified file path.

        The schema data is written to the "Instructions" sheet, and the table data is written to the "Tables" sheet.
        The columns in both sheets are auto-fitted to accommodate the data.

        The method returns the file path of the generated Excel file once it is saved.

        Note:
        - This method uses the xlsxwriter library to create and manipulate the Excel file.
        - The get_column_letter function is assumed to be imported from the openpyxl.utils module.
        """

        tracer, logger = LoggerSingleton.instance(
            NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
        ).initialize_logging_and_tracing()

        with tracer.start_as_current_span("create_excel_from_data"):
            # Create a new xlsxwriter Workbook object
            workbook = xlsxwriter.Workbook(
                manifest_excel_file, {"nan_inf_to_errors": True}
            )

            # Initialize Header Length
            headers = ["Schema attribute", "% Complete", "Last Updated", "Review By"]

            # ws_schema = workbook.add_worksheet('Instructions')

            # # Write df_schema to the "Instructions" sheet
            # for row_num, row in enumerate(df_schema.values.tolist(), start=0):
            #     for col_num, value in enumerate(row):
            #         if isinstance(value, dict):
            #             value = cls.convert_dict_to_csv(value)

            #         ws_schema.write(row_num, col_num, value)

            ##########################################################
            #  File Paths
            ##########################################################
            obj_file = cdc_env_file.EnvironmentFile()
            app_dir = os.path.dirname(manifest_excel_file)
            parent_dir = os.path.dirname(app_dir)
            data_definition_path = parent_dir + "/" + ENVIRONMENT + "_data_definitions/"
            # Convert 'data_definition_path' to the current OS directory format
            data_definition_path = obj_file.convert_to_current_os_dir(
                data_definition_path
            )

            # Join the directory path and the filename using 'os.path.join()'
            environment = config.get("environment")
            repository_path = config.get("repository_path")

            schema = alation_schema.Schema()

            json_data_definition_file = schema.get_json_data_definition_file_path(
                repository_path, environment
            )

            ##########################################################
            # Create Tables Worksheet
            ##########################################################
            ws_table_list = workbook.add_worksheet("Tables")

            ##########################################################
            # Create Valueset Dataframes
            ##########################################################

            table = alation_table.Table(None, json_data_definition_file)

            df_status, excel_data_definition_file = table.fetch_valueset(
                "Status of Dataset"
            )
            df_access_level, excel_data_definition_file = table.fetch_valueset(
                "Access Level"
            )
            df_format, excel_data_definition_file = table.fetch_valueset("Format")
            df_language, excel_data_definition_file = table.fetch_valueset("Language")
            df_steward, excel_data_definition_file = table.fetch_valueset("steward")
            df_update_frequency, excel_data_definition_file = table.fetch_valueset(
                "update_frequency"
            )

            logger.info(f"excel_data_definition_file: {excel_data_definition_file}")

            ##########################################################
            # Create Valueset Worksheets
            ##########################################################

            cls.create_valueset_worksheets(
                workbook,
                df_status,
                df_access_level,
                df_format,
                df_steward,
                df_language,
                df_update_frequency,
            )

            ##########################################################
            # Update Tables Worksheet
            ##########################################################

            list_worksheet = ws_table_list
            df_list = df_tables
            df_fields_data_definition = df_table_fields_data_definition

            row_init = 6  # As indexing starts from 0, 7th row corresponds to index 6
            col_init = 1  # As indexing starts from 0, 2nd column corresponds to index 1
            header_col_init = 5

            cls.create_worksheet_table(
                list_worksheet,
                df_list,
                json_data_definition_file,
                workbook,
                df_fields_data_definition,
                df_status,
                df_access_level,
                df_format,
                df_steward,
                df_language,
                df_update_frequency,
                col_init,
                row_init,
                header_col_init,
                "Table",
            )

            ##########################################################
            # Columns Worksheet
            ##########################################################

            # Worksheets
            ws_columns_list = workbook.add_worksheet("Columns")

            list_worksheet = ws_columns_list
            df_list = df_columns
            df_fields_data_definition = df_column_fields_data_definition

            row_init = 6  # As indexing starts from 0, 7th row corresponds to index 6
            col_init = 1  # As indexing starts from 0, 2nd column corresponds to index 1
            header_col_init = 5

            cls.create_worksheet_table(
                list_worksheet,
                df_list,
                json_data_definition_file,
                workbook,
                df_fields_data_definition,
                df_status,
                df_access_level,
                df_format,
                df_steward,
                df_language,
                df_update_frequency,
                col_init,
                row_init,
                header_col_init,
                "Columns",
            )

            # Close the workbook
            workbook.close()

            return manifest_excel_file

    @staticmethod
    def create_excel_formats(workbook):
        """
        Generate Excel formats for styling purposes using a given workbook.

        Parameters:
            workbook (xlsxwriter.Workbook): The workbook where the formats will be added.

        This method provides various formats that can be applied to cells in an Excel worksheet:
        1. `editable_format`: A format for cells that are intended to be edited.
           Features bold text, a blue background, and white font color.
        2. `readonly_format`: A format for cells that are intended to be read-only.
           Features bold and italic text with a light font color, white background, and a black border.
        3. `date_format`: A format specifically for date cells. Aligns text to the left and formats dates as "yyyy-mm-dd".
        4. `header_text_format`: A default text format for headers. Features bold text in a specific font, size, and color with a bottom border.

        Returns:
            tuple: A tuple containing the Excel formats in the order: (editable_format, readonly_format, date_format, header_text_format).

        Example:
            >>> workbook = xlsxwriter.Workbook('sample.xlsx')
            >>> editable, readonly, date_format, header = YourClassName.create_excel_formats(workbook)
            >>> type(editable)
            <class 'xlsxwriter.format.Format'>
        """

        tracer, logger = LoggerSingleton.instance(
            NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
        ).initialize_logging_and_tracing()

        with tracer.start_as_current_span("create_excel_from_data"):
            # Create a format object with bold property
            editable_format = workbook.add_format(
                {"bold": True, "bg_color": "#4472c4", "font_color": "white"}
            )

            # Create a format object with readonly property
            readonly_format = workbook.add_format(
                {
                    "bold": True,
                    "italic": True,  # Make the text italic
                    "bg_color": "white",
                    "font_color": "#7f7f95",
                    "border": 1,
                    "border_color": "black",
                }
            )

            # Define the date format for "yyyy-mm-dd".
            date_format = workbook.add_format({"num_format": "yyyy-mm-dd"})
            date_format.set_align("left")

            # Create a format with default text setttings for font, size, color and bottom border
            header_text_format = workbook.add_format(
                {
                    "font_name": "Calibri",
                    "bold": True,
                    "font_size": 15,
                    "font_color": "44546A",  # font color
                    "bottom": 2,  # enable bottom border
                    "bottom_color": "4472C4",  # set bottom border color
                }
            )

            return editable_format, readonly_format, date_format, header_text_format

    @classmethod
    def create_valueset_worksheets(
        cls,
        workbook,
        df_status,
        df_access_level,
        df_format,
        df_steward,
        df_language,
        df_update_frequency,
    ):
        tracer, logger = LoggerSingleton.instance(
            NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
        ).initialize_logging_and_tracing()

        with tracer.start_as_current_span("create_valueset_worksheets"):
            # Create valueset reference sheets in the workbook

            # Valueset reference: status_of_dataset
            ws_vs_status = workbook.add_worksheet("status_of_dataset")
            cls.write_dataframe_to_excel(
                workbook, df_status, ws_vs_status, 0, 0, "status_of_dataset"
            )

            # Valueset reference: access_level
            ws_vs_access_level = workbook.add_worksheet("access_level")
            cls.write_dataframe_to_excel(
                workbook, df_access_level, ws_vs_access_level, 0, 0, "access_level"
            )

            # Valueset reference: format
            ws_vs_format = workbook.add_worksheet("format")
            cls.write_dataframe_to_excel(
                workbook, df_format, ws_vs_format, 0, 0, "format"
            )

            # Valueset reference: steward
            ws_vs_steward = workbook.add_worksheet("steward")
            cls.write_dataframe_to_excel(
                workbook, df_steward, ws_vs_steward, 0, 0, "steward"
            )

            # Valueset reference: language
            ws_vs_language = workbook.add_worksheet("language")
            cls.write_dataframe_to_excel(
                workbook, df_language, ws_vs_language, 0, 0, "language"
            )

            # Valueset reference: update_frequency
            ws_vs_update_frequency = workbook.add_worksheet("update_frequency")
            cls.write_dataframe_to_excel(
                workbook,
                df_update_frequency,
                ws_vs_update_frequency,
                0,
                0,
                "update_frequency",
            )

            # Hide worksheets
            ws_vs_status.hide()
            ws_vs_access_level.hide()
            ws_vs_format.hide()
            ws_vs_steward.hide()
            ws_vs_language.hide()
            ws_vs_update_frequency.hide()

            return (
                ws_vs_status,
                ws_vs_access_level,
                ws_vs_format,
                ws_vs_steward,
                ws_vs_language,
                ws_vs_update_frequency,
            )

    @classmethod
    def create_worksheet_table_validation_options(
        cls,
        headers,
        list_worksheet,
        df_list,
        df_status,
        df_access_level,
        df_format,
        df_steward,
        df_language,
        df_update_frequency,
        col_init,
        row_init,
        date_fields,
    ):
        """
        Add validation options to specific columns in an Excel worksheet based on provided dataframes.

        This method applies data validation options to columns of an Excel worksheet based on various criteria
        defined in the provided dataframes. It sets specific valuesets (lists) for certain columns and date
        validation for date columns.

        Parameters:
            headers (list): List of column headers for the main worksheet.
            list_worksheet (xlsxwriter.Worksheet): The worksheet to apply the validation on.
            df_list (pandas.DataFrame): Main dataframe with data.
            df_status (pandas.DataFrame): Dataframe containing status valueset data.
            df_access_level (pandas.DataFrame): Dataframe containing access level valueset data.
            df_format (pandas.DataFrame): Dataframe containing format valueset data.
            df_steward (pandas.DataFrame): Dataframe containing steward valueset data.
            df_language (pandas.DataFrame): Dataframe containing language valueset data.
            df_update_frequency (pandas.DataFrame): Dataframe containing update frequency valueset data.
            col_init (int): Column number where the data starts in the worksheet.
            row_init (int): Row number where the data starts in the worksheet.

        Returns:
            dict: A dictionary indicating the success status of the method.

        Example:
            >>> result = YourClassName.create_worksheet_table_validation_options(headers, list_worksheet, df_list, df_status, df_access_level, df_format, df_steward, df_language, df_update_frequency, col_init, row_init, df_fields_data_definition)
            >>> print(result)
            {"Message": "Success"}
        """

        tracer, logger = LoggerSingleton.instance(
            NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
        ).initialize_logging_and_tracing()

        with tracer.start_as_current_span("create_worksheet_table_validation_options"):
            # Get Status Valueset Data
            sheet_name_status_of_dataset = "status_of_dataset"
            cell_range_formula_status_of_dataset = cls.get_excel_range(
                df_status, 1, 0, sheet_name_status_of_dataset
            )

            options_status_of_dataset = {
                "validate": "list",
                "source": cell_range_formula_status_of_dataset,
            }

            # Apply Status Valueset Validation
            status_of_dataset_col_num = [
                i
                for i, header in enumerate(headers)
                if header.lower().replace(" ", "_") == "status_of_dataset"
            ]
            if (
                status_of_dataset_col_num
            ):  # If the "status_of_dataset" column is present
                # Adjust column number with col_init
                status_of_dataset_col_num = status_of_dataset_col_num[0] + col_init
                # Apply data validation to the cells in the 'status_of_dataset' column
                list_worksheet.data_validation(
                    f"{xlsxwriter.utility.xl_rowcol_to_cell(row_init + 1, status_of_dataset_col_num)}:{xlsxwriter.utility.xl_rowcol_to_cell(row_init + len(df_list), status_of_dataset_col_num)}",
                    options_status_of_dataset,
                )

            # Get Access Level Valueset Data
            sheet_name_access_level = "access_level"
            cell_range_formula_access_level = cls.get_excel_range(
                df_access_level, 1, 0, sheet_name_access_level
            )

            options_access_level = {
                "validate": "list",
                "source": cell_range_formula_access_level,
            }

            # Apply Access Level Valueset Validation
            access_level_col_num = [
                i
                for i, header in enumerate(headers)
                if header.lower().replace(" ", "_") == "access_level"
            ]
            if access_level_col_num:  # If the "access_level" column is present
                # Adjust column number with col_init
                access_level_col_num = access_level_col_num[0] + col_init
                # Apply data validation to the cells in the 'access_level' column
                list_worksheet.data_validation(
                    f"{xlsxwriter.utility.xl_rowcol_to_cell(row_init + 1, access_level_col_num)}:{xlsxwriter.utility.xl_rowcol_to_cell(row_init + len(df_list), access_level_col_num)}",
                    options_access_level,
                )

            # Get Format Valueset Data
            sheet_name_format = "format"
            cell_range_formula_format = cls.get_excel_range(
                df_format, 1, 0, sheet_name_format
            )

            options_format = {"validate": "list", "source": cell_range_formula_format}

            # Apply Format Valueset Validation
            format_col_num = [
                i
                for i, header in enumerate(headers)
                if header.lower().replace(" ", "_") == "format"
            ]
            if format_col_num:  # If the "format" column is present
                # Adjust column number with col_init
                format_col_num = format_col_num[0] + col_init
                # Apply data validation to the cells in the 'format' column
                list_worksheet.data_validation(
                    f"{xlsxwriter.utility.xl_rowcol_to_cell(row_init + 1, format_col_num)}:{xlsxwriter.utility.xl_rowcol_to_cell(row_init + len(df_list), format_col_num)}",
                    options_format,
                )

            # After writing headers to the worksheet
            # Get the range in the desired language.
            sheet_name_language = "language"
            cell_range_formula_language = cls.get_excel_range(
                df_language, 1, 0, sheet_name_language
            )

            options_language = {
                "validate": "list",
                "source": cell_range_formula_language,
            }
            # Validate language
            language_col_num = [
                i
                for i, header in enumerate(headers)
                if header.lower().replace(" ", "_") == "language"
            ]
            if language_col_num:  # If the "language" column is present
                # Adjust column number with col_init
                language_col_num = language_col_num[0] + col_init
                # Apply data validation to the cells in the 'language' column
                list_worksheet.data_validation(
                    f"{xlsxwriter.utility.xl_rowcol_to_cell(row_init + 1, language_col_num)}:{xlsxwriter.utility.xl_rowcol_to_cell(row_init + len(df_list), language_col_num)}",
                    options_language,
                )

            # Define the date validation rule. In this example, we restrict dates to be within 2022-01-01 and 2022-12-31.
            # Get today's date
            current_date = date.today()

            # Calculate the start_date as 20 years ago from the current date
            start_date = current_date - timedelta(days=365 * 20)

            # Calculate the end_date as one year from the current date
            end_date = current_date + timedelta(days=365)

            # Format the start_date as 'yyyy-mm-dd'
            start_date_formatted = start_date.strftime("%Y-%m-%d")

            # Format the end_date as 'yyyy-mm-dd'
            end_date_formatted = end_date.strftime("%Y-%m-%d")

            options_date_standard = {
                "validate": "date",
                "criteria": "between",
                "minimum": start_date,
                "maximum": end_date,
                "error_message": "Enter a date between {} and {}.".format(
                    start_date_formatted, end_date_formatted
                ),
                "input_message": "Enter a date between {} and {}.".format(
                    start_date_formatted, end_date_formatted
                ),
            }

            # List to store the column numbers of all date columns
            date_col_numbers = [
                i for i, header in enumerate(headers) if header in date_fields
            ]

            # Loop through each date column and apply data validation
            for date_col_num in date_col_numbers:
                # Adjust column number with col_init
                date_col_num = date_col_num + col_init
                # Apply data validation to the cells in the 'language' column
                list_worksheet.data_validation(
                    f"{xlsxwriter.utility.xl_rowcol_to_cell(row_init + 1, date_col_num)}:{xlsxwriter.utility.xl_rowcol_to_cell(row_init + len(df_list), date_col_num)}",
                    options_date_standard,
                )

            return {"Message": "Success"}

    @classmethod
    def create_worksheet_table(
        cls,
        list_worksheet,
        df_list,
        json_data_definition_file,
        workbook,
        df_fields_data_definition,
        df_status,
        df_access_level,
        df_format,
        df_steward,
        df_language,
        df_update_frequency,
        col_init,
        row_init,
        header_col_init,
        header_name,
    ):
        """
        Create a worksheet table in an Excel workbook based on provided dataframes and configurations.

        This method structures and styles an Excel worksheet using the provided dataframes.
        It sets up column widths, applies specific formats based on criteria, adds data validations,
        and writes headers and data from the dataframe. Additionally, it interacts with the Alation Table
        API to fetch specific fields for table configuration.

        Parameters:
            list_worksheet (xlsxwriter.Worksheet): Target worksheet to write data to.
            df_list (pandas.DataFrame): Dataframe containing the main data to be written to the worksheet.
            json_data_definition_file (str): Path to the JSON file defining data criteria.
            workbook (xlsxwriter.Workbook): Workbook containing the list_worksheet.
            df_fields_data_definition (pandas.DataFrame): Dataframe defining the fields' data properties.
            df_status, df_access_level, df_format, df_steward, df_language, df_update_frequency (pandas.DataFrame): Dataframes containing specific valuesets for data validation.
            col_init (int): Initial column number where the data starts.
            row_init (int): Initial row number where the data starts.
            header_col_init (int): Initial column number for headers.

        Returns:
            None: This method performs actions in-place and does not return a value.

        Example:
            >>> workbook = xlsxwriter.Workbook('sample.xlsx')
            >>> worksheet = workbook.add_worksheet('Data')
            >>> YourClassName.create_worksheet_table(worksheet, df, "data_definition.json", workbook, df_fields, df_status, df_access, df_format, df_steward, df_lang, df_freq, 0, 0, 0)
        """

        tracer, logger = LoggerSingleton.instance(
            NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
        ).initialize_logging_and_tracing()

        with tracer.start_as_current_span("create_excel_from_data"):
            write_to_debug_excel = False

            # Set up formats
            (
                editable_format,
                readonly_format,
                date_format,
                header_text_format,
            ) = cls.create_excel_formats(workbook)

            # Set the width of the first column to approximately 40 pixels.
            # Excel's column width unit is approximately 1/6 of a character
            list_worksheet.set_column(0, 0, 24 / 6)

            # Write '{header_name} Updates' in cell G2
            list_worksheet.write("E2", f"{header_name} Updates", header_text_format)

            # Get the headers from the DataFrame and write them to the worksheet first
            headers = df_list.columns.tolist()

            # Save to excel for debugging
            df_header_columns = pd.DataFrame(headers, columns=["headers"])

            if write_to_debug_excel:
                file_name = f"debug_df_{header_name}_header_columns.xlsx"
                logger.info(f"file_name: {file_name}")
                df_header_columns.to_excel(file_name, engine="openpyxl")

            # Initialize list to store max length of each column
            max_length = [len(header) for header in headers]

            # Apply the bottom border line to the entire row
            for i in range(len(max_length) - (header_col_init - 3)):
                list_worksheet.write(1, i + header_col_init, " ", header_text_format)

            table = alation_table.Table(None, json_data_definition_file)

            editable_fields = table.fetch_editable_fields(
                df_list, df_fields_data_definition
            )

            date_fields = table.fetch_date_fields(df_list, df_fields_data_definition)

            visible_fields = table.fetch_visible_fields(
                df_list, df_fields_data_definition
            )

            hidden_fields = [col for col in headers if col not in visible_fields]

            list_worksheet.write(
                "E3",
                "Instructions: Items in grey are Read-Only.  Update the fields in blue.",
            )
            list_worksheet.write("E4", "Dropdowns should contain picklist validation.")

            # List to store the column numbers of date columns
            date_col_numbers = []

            # Write headers to the worksheet
            for header_num, header in enumerate(headers):
                # Check if the header is in date_fields
                if header in date_fields:
                    date_col_numbers.append(header_num)

                if header in editable_fields:
                    col_number = header_num + col_init
                    list_worksheet.write(row_init, col_number, header, editable_format)
                else:
                    list_worksheet.write(
                        row_init,
                        header_num + col_init,
                        header + " (Read-Only)",
                        readonly_format,
                    )

            # Get the number of columns in the DataFrame
            num_of_columns = len(df_list.columns)

            # Log the number of columns
            logger.info(f"Number of columns in df_list {num_of_columns}")

            # Now iterate over the rows and write them to the worksheet, starting from the second row (index 1)
            for row_num, row in enumerate(df_list.itertuples(index=False), start=1):
                for col_num, value in enumerate(row):
                    # Check if value is a dictionary
                    if isinstance(value, dict):
                        value = cls.convert_dict_to_csv(value)
                    # Check if value is a list
                    elif isinstance(value, list):  # check if value is a list
                        # convert list to string
                        value = ", ".join(map(str, value))

                    if col_num in date_col_numbers:
                        # Convert the date to the desired format
                        list_worksheet.write(
                            row_num + row_init, col_num + col_init, value, date_format
                        )
                    else:
                        # Write the value to the worksheet
                        list_worksheet.write(
                            row_num + row_init, col_num + col_init, value
                        )

                    # Update max_length of column width if necessary
                    cell_length = len(str(value))
                    if cell_length > max_length[col_num]:
                        max_length[col_num] = cell_length

            status_json = cls.create_worksheet_table_validation_options(
                headers,
                list_worksheet,
                df_list,
                df_status,
                df_access_level,
                df_format,
                df_steward,
                df_language,
                df_update_frequency,
                col_init,
                row_init,
                date_fields,
            )

            # Log Status
            logger.info(f"status_json: {status_json}")

            # Now set the column widths based on the max length of the data in each column
            for i, width in enumerate(max_length):
                list_worksheet.set_column(i + col_init, i + col_init, width)

            # Hide non required columns
            for header_num, header in enumerate(headers):
                if header in hidden_fields:
                    col_number = header_num + col_init
                    cls.hide_column_by_number(list_worksheet, col_number)

    @staticmethod
    def hide_column_by_number(worksheet, column_number):
        """
        Hide a specific column in an XlsxWriter worksheet.

        Parameters:
            worksheet (Worksheet): The XlsxWriter worksheet object where the column should be hidden.
            column_number (int): The zero-based index of the column to be hidden.

        Returns:
            None

        Note:
            This method uses the XlsxWriter's 'set_column()' method to set the width of the specified column to zero,
            effectively hiding it from view. The 'hidden' parameter is set to True in the 'set_column()' method
            to hide the column without deleting its data.

        Example:
            # Create a new Excel workbook and add a worksheet.
            workbook = xlsxwriter.Workbook('hidden_fields.xlsx')
            worksheet = workbook.add_worksheet()

            # Example data - write some data to columns A, B, and C.
            worksheet.write('A1', 'Column A')
            worksheet.write('B1', 'Column B')
            worksheet.write('C1', 'Column C')

            # Hide the second column (column B) by its number (index 1).
            hide_column_by_number(worksheet, 1)

            # Save the workbook.
            workbook.close()
        """
        worksheet.set_column(column_number, column_number, None, None, {"hidden": True})

    @classmethod
    def write_dataframe_to_excel(
        cls, workbook, df_to_write, worksheet, start_row, start_col, sheet_name
    ):
        """
        Write a pandas DataFrame to an Excel worksheet using XlsxWriter.

        This function creates column headers in the worksheet using the DataFrame's column names
        and then populates the worksheet with data from the DataFrame. The DataFrame's index is ignored.
        Each row from the DataFrame is written to a new row in the worksheet, starting from
        the first row after the headers.

        Args:
            workbook (xlsxwriter.workbook.Workbook): The workbook object where the worksheet resides.
            df_to_write (pandas.DataFrame): The DataFrame to write to the Excel worksheet.
            worksheet (xlsxwriter.worksheet.Worksheet): The worksheet object to write to. This should
                                                    be a valid Worksheet object created from
                                                    an XlsxWriter Workbook.
            sheet_name (str, optional): The name of the sheet in the workbook to write to.
                                        Defaults to 'Sheet1'.

        Returns:
            str: A string "Ok" is returned after successful execution of the function.

        Raises:
            Any exceptions raised during execution will be propagated to the caller.

        Usage:
            ```python
            import xlsxwriter
            import pandas as pd

            workbook = xlsxwriter.Workbook('filename.xlsx')
            worksheet = workbook.add_worksheet('Sheet1')
            df = pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6]})
            write_dataframe_to_excel(workbook, df, worksheet, 'Sheet1')
            workbook.close()
            ```

        Note:
            This function also tries to mix functionality from openpyxl. Ensure you have the right libraries
            and dependencies installed and that they are compatible with each other.
        """

        tracer, logger = LoggerSingleton.instance(
            NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
        ).initialize_logging_and_tracing()

        with tracer.start_as_current_span(f"write_dataframe_to_excel: {sheet_name}"):
            # Get the column names from the DataFrame
            columns = df_to_write.columns.tolist()

            # Write the column headers to the worksheet
            for idx, column in enumerate(columns):
                worksheet.write(start_row, idx + start_col, column)

            logger.info(f"Writing DataFrame to Excel worksheet {sheet_name}")
            # Iterate over the DataFrame rows and write each row to the worksheet
            for row_idx, row in df_to_write.iterrows():
                for col_idx, value in enumerate(row):
                    # row_idx+1 because we have headers
                    worksheet.write(row_idx + start_row + 1, col_idx + start_col, value)

            # Get the range in the desired format.
            cell_range = cls.get_excel_range(
                df_to_write, start_row + 1, start_col, sheet_name
            )
            logger.info(f"cell_range:{cell_range}")

            named_range_name = f"{sheet_name}_range"

            # Define a named range for the DataFrame range
            workbook.define_name(named_range_name, cell_range)

            return "Ok"

    @classmethod
    def get_excel_range(
        cls, df_to_write: pd.DataFrame, start_row, start_col, sheet_name
    ):
        """
        Creates a fixed Excel cell range from a given DataFrame and starting cell.

        This function creates a copy of the DataFrame and uses the 'start' and 'end' formulas to calculate
        the starting and ending cell positions in Excel notation. It then forms a range and makes it fixed
        to prevent the range from shifting.

        Parameters:
        df_to_write (pd.DataFrame): The DataFrame to be written to Excel.
        start_row (int): The starting row index for the DataFrame.
        start_col (int): The starting column index for the DataFrame.
        sheet_name (str): The name of the Excel sheet where the DataFrame will be written.

        Returns:
        cell_range (str): A fixed Excel cell range in the format "=$SheetName!$A$1:$B$2".

        Note:
        This function depends on the 'evaluate_range_formula' method to get the start and end cell references
        and the 'make_range_fixed' method to create a fixed cell range. Ensure these methods are properly implemented.
        """

        # Create a copy of the DataFrame
        df_copy = df_to_write.copy()

        start_row, start_col = cls.evaluate_range_formula(
            df_copy, "start", start_row, start_col
        )
        end_row, end_col = cls.evaluate_range_formula(
            df_copy, "end", start_row, start_col
        )

        start_cell = xlsxwriter.utility.xl_rowcol_to_cell(start_row, start_col)
        end_cell = xlsxwriter.utility.xl_rowcol_to_cell(end_row, end_col)

        cell_range = f"{start_cell}:{end_cell}"

        cell_range_formula = f"={sheet_name}!{cell_range}"

        cell_range = cls.make_range_fixed(cell_range_formula)

        return cell_range

    @staticmethod
    def evaluate_range_formula(
        df_copy: pd.DataFrame, formula: str, start_row, start_col
    ):
        """
        Evaluates a given formula and returns the row and column numbers based on the formula.

        This function is used to compute the starting and ending cell references within a DataFrame.
        The starting and ending positions are computed based on a provided formula.
        Currently, it supports only two formulas: 'start' and 'end'.

        Parameters:
        df_copy (pd.DataFrame): The DataFrame on which the cell reference formulas will be evaluated.
        formula (str): A string that determines how the function behaves. Currently supports 'start' and 'end'.
        start_row (int): The row number from which to start the evaluation.
        start_col (int): The column number from which to start the evaluation.

        Returns:
        row (int): The evaluated row number based on the given formula.
        col (int): The evaluated column number based on the given formula.

        Note:
        This function is a placeholder. Depending on the complexity and nature of the formulas you are using,
        you may need to implement a more sophisticated version of this function.
        """
        if formula == "start":
            row = start_row
            col = start_col
        if formula == "end":
            row = start_row + (len(df_copy.index) - 1)
            col = start_col + (len(df_copy.columns) - 1)

        return row, col

    @staticmethod
    def make_range_fixed(range_string):
        """
        Converts a regular Excel cell range into a fixed cell range.

        This function takes a cell range in the format "SheetName!A1:B2" and converts it to a fixed cell range
        in the format "SheetName!$A$1:$B$2". Fixed cell ranges don't shift when copied to other cells in Excel.

        Parameters:
        range_string (str): The Excel cell range to be made fixed. Should be in the format "SheetName!A1:B2".

        Returns:
        fixed_range (str): The fixed Excel cell range. Will be in the format "SheetName!$A$1:$B$2".

        Example:
        >>> make_range_fixed("Sheet1!A1:B2")
        "Sheet1!$A$1:$B$2"
        """
        sheet, range_part = range_string.split("!")
        start, end = range_part.split(":")
        start_col, start_row = "".join(filter(str.isalpha, start)), "".join(
            filter(str.isdigit, start)
        )
        end_col, end_row = "".join(filter(str.isalpha, end)), "".join(
            filter(str.isdigit, end)
        )
        fixed_range = f"{sheet}!${start_col}${start_row}:${end_col}${end_row}"
        return fixed_range
