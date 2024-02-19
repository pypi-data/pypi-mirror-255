import sys
import os

from cdh_lava_core.cdc_log_service.environment_logging import LoggerSingleton

NAMESPACE_NAME = os.path.basename(os.path.dirname(__file__))
SERVICE_NAME = os.path.basename(__file__)


class Column:
    """Represents a column in a database table.

    Args:
        name (str): The name of the column.
        data_type (str): The data type of the column.
        nullable (bool, optional): Indicates if the column is nullable. Defaults to True.
        primary_key (bool, optional): Indicates if the column is a primary key. Defaults to False.
        default (Any, optional): The default value of the column. Defaults to None.

    Attributes:
        name (str): The name of the column.
        data_type (str): The data type of the column.
        nullable (bool): Indicates if the column is nullable.
        primary_key (bool): Indicates if the column is a primary key.
        default (Any): The default value of the column.

    """

    def __init__(
        self, column_json, data_definition_file_path, data_product_id, environment
    ):
        """
        Initializes a new instance of the DbColumn class.

        Args:
            column_json (dict): The JSON representation of the column.
            data_definition_file_path (str): The file path of the data definition file.
            data_product_id (int): The ID of the data product.
            environment (str): The environment in which the column exists.
        """
        self.data_definition_file_path = data_definition_file_path
        self.name = column_json["name"]
        self.title = column_json["title"]
        self.extra_description_fields = self.get_column_extra_description_fields(
            column_json, data_product_id, environment
        )
        self.description = self.format_description(column_json)
        tags = column_json.get("tags")
        if tags is not None:
            self.tags = tags
        else:
            self.tags = []

    def format_description(self, column_json):
        """
        Formats the description of a column.

        Args:
            column_json (dict): The JSON representation of the column.

        Returns:
            str: The formatted description of the column.
        """
        description = column_json["description"]
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

    @staticmethod
    def get_column_name(
        schema_name, table_name, column, data_product_id: str, environment: str
    ):
        """
        Construct and return the full column name, including schema, table and column names.

        Args:
            schema_name (str): The name of the schema.
            table_name (str): The table object. Must have a 'name' attribute representing the name of the table.
            column (object): The column object. Must have a 'name' attribute representing the name of the column.

        Returns:
            str: The full column name in the format "schema_name.table.name.column.name".
        """

        tracer, logger = LoggerSingleton.instance(
            NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
        ).initialize_logging_and_tracing()

        with tracer.start_as_current_span("get_column_name"):
            try:
                column_name = getattr(column, "name", column)
                full_column_name = f"{schema_name}.{table_name}.{column_name}"
                logger.info("Full column name: %s", full_column_name)
                return full_column_name
            except Exception as ex:
                error_msg = "Error: %s", ex
                exc_info = sys.exc_info()
                LoggerSingleton.instance(
                    NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
                ).error_with_exception(error_msg, exc_info)
                raise

    def get_column_extra_description_fields(
        self, column_json, data_product_id: str, environment: str
    ):
        """
        Extracts the extra description fields from the provided column JSON data.

        This function checks if the 'extraDescriptionFields' key exists in the 'column_json'. If present,
        the key-value pairs from 'extraDescriptionFields' are extracted and returned as a new dictionary.
        If 'extraDescriptionFields' does not exist, an empty dictionary is returned.

        Args:
            column_json (dict): The JSON data for a column, potentially containing 'extraDescriptionFields'
                                as a key with another dictionary as its value.

        Returns:
            dict: A dictionary containing the extra description fields from 'column_json'.
                Returns an empty dictionary if 'extraDescriptionFields' is not present in 'column_json'.
        """

        tracer, logger = LoggerSingleton.instance(
            NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
        ).initialize_logging_and_tracing()

        extra_description_fields = {}
        if "extraDescriptionFields" in column_json:
            optional_description_fields = column_json["extraDescriptionFields"]
            print("Extra description fields: ", optional_description_fields)
            for key in optional_description_fields:
                extra_description_fields[key] = optional_description_fields[key]

        logger.info("Extra description fields: %s", extra_description_fields)
        return extra_description_fields

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
