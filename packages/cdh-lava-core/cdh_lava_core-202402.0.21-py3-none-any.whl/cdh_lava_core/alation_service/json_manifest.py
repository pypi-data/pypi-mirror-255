"""
This module provides a class called ManifestJson, which is used to handle a manifest JSON file and perform operations on its data.

Module Contents:
- ManifestJson: A class representing a manifest JSON file and containing methods for data manipulation and validation.

This module also imports and uses the following external modules:
- jsonschema: A Python library to validate JSON data against a JSON Schema.
- json: The built-in JSON module in Python for JSON data manipulation.
- sys: The built-in sys module for system-specific functions and parameters.
- os: The built-in os module for operating system-related functions.

This module also imports the following class objects from the 'cdh_lava_core.cdc_log_service' module:
- environment_tracing: A class to handle environment tracing configuration.
- environment_logging: A class to handle environment logging configuration.

Important Note:
- The ManifestJson class is designed to work with the specific structure of a manifest JSON file defined by a JSON schema.
- The data_definition_file_path should point to a JSON schema file used for validation.
- The 'Table' class from the 'cdh_lava_core.alation_service.table' module is used for representing tables in the 'ManifestJson' class.
"""

import sys
import os
import json
import jsonschema
from jsonschema import validate


from cdh_lava_core.cdc_log_service.environment_logging import LoggerSingleton


# Get the currently running file name
NAMESPACE_NAME = os.path.basename(os.path.dirname(__file__))
# Get the parent folder name of the running file
SERVICE_NAME = os.path.basename(__file__)
SUBMITTING_USER = "TODO: Get submitting user from Alation"


class ManifestJson:
    """
    Represents a ManifestJson object with data extracted from a manifest JSON file and a schema file.

    The `ManifestJson` class provides methods to initialize the object with the schema file path, set Alation data,
    retrieve tables and columns data, validate JSON data against a given schema, and more.

    Attributes:
        data_definition_file_path (str): The path to the schema JSON file.
        title (str): The title extracted from the manifest JSON.
        alationDatasourceID (str): The Alation datasource ID extracted from the manifest JSON.
        alationSchemaID (str): The Alation schema ID extracted from the manifest JSON.
        submitting_user (str): The submitting user associated with the manifest.
        description (str): The description extracted from the manifest JSON.
        releasedate (str): The release date extracted from the manifest JSON.
        homepageUrl (str): The homepage URL extracted from the manifest JSON.
        identifier (str): The identifier extracted from the manifest JSON.
        dataformat (str): The data format extracted from the manifest JSON.
        language (str): The language extracted from the manifest JSON.
        size (str): The size extracted from the manifest JSON.
        updateFrequency (str): The update frequency extracted from the manifest JSON.
        temporalResolution (str): The temporal resolution extracted from the manifest JSON.
        license (str): The license extracted from the manifest JSON.
        tags (list): The list of tags extracted from the manifest JSON.
        geographicCoverage (str): The geographic coverage extracted from the manifest JSON.
        referencedBy (str): The reference information extracted from the manifest JSON.
        references (str): The references extracted from the manifest JSON.
        citation (str): The citation extracted from the manifest JSON.
        reference (str): The reference extracted from the manifest JSON.
        temporalApplicability (dict): The temporal applicability extracted from the manifest JSON.
        tables (dict): A dictionary mapping table names to their respective table objects.
        pii (dict): The personally identifiable information extracted from the manifest JSON.
        manifest_template_properties (dict): The manifest template properties extracted from the schema JSON.
        extra_description_fields (dict): Additional description fields extracted from the manifest JSON.

    Methods:
        __init__(self, data_definition_file_path): Initializes a ManifestJson object with the provided data_definition_file_path.
        set_alation_data(self, manifest_json): Sets Alation data using the provided manifest and data_definition_file_path.
        get_tables_data(self): Retrieves the tables data from the current instance.
        get_columns_data(self): Retrieves the columns data for each table in the current instance.
        format_description(self): Formats the description to include any additional description fields.
        fetch_schema_data(self): Retrieves Alation schema data from the ManifestJson object.
        validate_json(self, json_data, schema): Validates JSON data against a given schema.
        print_manifest(manifest_object): Print the key-value pairs of a dictionary in a user-friendly format.
        get_submitting_user_from_manifest_file(self, manifest_file_path): Retrieves the submitting user from a manifest JSON file.
        validate_manifest(self, manifest_file, data_definition_file_path): Validates a manifest JSON file against a JSON schema.
        get_manifest_expected_fields(self): Reads the manifest JSON file and extracts expected fields for schema, table, and column objects.

    """

    def __init__(self, data_definition_file_path):
        """
        Initializes a ManifestJson object with the provided data_definition_file_path.

        Args:
            data_definition_file_path (str): The path to the schema JSON file.

        Raises:
            Exception: If an error occurs during initialization.

        """
        tracer, logger = LoggerSingleton.instance(
            NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
        ).initialize_logging_and_tracing()

        with tracer.start_as_current_span("__init__"):
            try:
                logger.info("Start Field by field:")
                self.data_definition_file_path = data_definition_file_path
                self.title = ""
                self.alationDatasourceID = ""
                self.alationSchemaID = ""
                self.submitting_user = SUBMITTING_USER
                self.description = ""
                self.releasedate = ""
                self.homepageUrl = ""
                self.identifier = ""
                self.dataformat = ""
                self.language = ""
                self.size = ""
                self.updateFrequency = ""
                self.temporalResolution = ""
                self.license = ""
                self.tags = []
                self.geographicCoverage = ""
                self.referencedBy = ""
                self.references = ""
                self.citation = ""
                self.reference = ""
                self.temporalApplicability = {}
                self.tables = {}
                self.pii = {}
                self.manifest_template_properties = {}
                self.extra_description_fields = {}

            except Exception as ex:
                error_msg = "Error: %s", ex
                exc_info = sys.exc_info()
                LoggerSingleton.instance(
                    NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
                ).error_with_exception(error_msg, exc_info)
                raise

    def set_alation_data(self, manifest_json):
        """
        Set Alation data using the provided manifest and data_definition_file_path.
        """

        tracer, logger = LoggerSingleton.instance(
            NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
        ).initialize_logging_and_tracing()

        with tracer.start_as_current_span("set_alation_data"):
            try:
                logger.info("Start Field by field:")
                excel_data_definition_file = open(
                    self.data_definition_file_path, encoding="utf-8"
                )
                schemaContents = json.load(excel_data_definition_file)
                self.manifest_template_properties = schemaContents["properties"].keys()
                self.manifest_template_table_properties = schemaContents["$defs"][
                    "table"
                ]["properties"].keys()
                self.manifest_template_column_properties = schemaContents["$defs"][
                    "column"
                ]["properties"].keys()
                # extraDescriptionFields is an optional field
                self.extra_description_fields = {}
                if "extraDescriptionFields" in manifest_json:
                    optional_description_fields = manifest_json[
                        "extraDescriptionFields"
                    ]
                    print("Extra description fields: ", optional_description_fields)
                    for key in optional_description_fields:
                        self.extra_description_fields[key] = (
                            optional_description_fields[key]
                        )
                # Required fields
                self.alationDatasourceID = manifest_json["alationDatasourceID"]
                self.alationSchemaID = manifest_json["alationSchemaID"]
                self.identifier = manifest_json["identifier"]
                self.title = manifest_json["title"]
                self.description = manifest_json["description"]
                self.releasedate = manifest_json["releaseDate"]
                self.pii = manifest_json["pii"]
                self.tags = manifest_json["tags"]
                self.submitting_user = SUBMITTING_USER
                # self.dataformat  = manifest['format']
                # self.language    = manifest['language']
                # self.size        = manifest['size']
                # self.temporalResolution = manifest['temporalResolution']
                # self.updateFrequency    = manifest['updateFrequency']
                # self.conformToStandard  = manifest['conformToStandard']
                # Non Required fields : Default Blank
                # self.tables = list(map(lambda t: Table(t), manifest['tables']))
                self.homepageUrl = manifest_json.get("homepageUrl", "")
                self.license = manifest_json.get("license", "")
                self.referencedBy = manifest_json.get("referencedBy", "")
                self.citation = manifest_json.get("citation", "")
                self.reference = manifest_json.get("reference", "")
                self.geographicCoverage = manifest_json.get("geographicCoverage", "")
                self.temporalApplicability = manifest_json.get(
                    "temporalApplicability", ""
                )
                # import here to avoid reference conflicts
                from cdh_lava_core.alation_service.db_table import Table

                self.tables = {
                    table.name: table
                    for table in map(
                        lambda t: Table(t, self.data_definition_file_path),
                        manifest_json["tables"],
                    )
                }

                return 200, "Success"
            except Exception as ex:
                error_msg = "Error: %s", ex
                exc_info = sys.exc_info()
                LoggerSingleton.instance(
                    NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
                ).error_with_exception(error_msg, exc_info)
                raise

    def get_tables_data(self):
        """
        Retrieves the tables data from the current instance.

        Returns:
            dict: A dictionary containing the tables data.

        Example:
            >>> instance = MyClass()
            >>> tables_data = instance.get_tables_data()
            >>> print(tables_data)
            {'table1': [...], 'table2': [...], ...}
        """

        tracer, logger = LoggerSingleton.instance(
            NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
        ).initialize_logging_and_tracing()

        with tracer.start_as_current_span("get_tables_data"):
            return self.tables

    def get_columns_data(self):
        """
        Retrieves the columns data for each table in the current instance.

        Returns:
            dict: A dictionary mapping table names to their respective column data.

        Example:
            >>> instance = MyClass()
            >>> columns_data = instance.get_columns_data()
            >>> print(columns_data)
            {'table1': ['column1', 'column2', ...], 'table2': ['column3', 'column4', ...], ...}
        """

        tracer, logger = LoggerSingleton.instance(
            NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
        ).initialize_logging_and_tracing()

        with tracer.start_as_current_span("get_columns_data"):
            columndata = {}
            for table_data in self.tables:
                columndata[table_data] = table_data.columns
            return columndata

    def format_description(self):
        description = self.description
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

    def fetch_schema_data(self):
        """
        Retrieves Alation schema data from the ManifestJson object.

        Returns:
            dict: A dictionary containing Alation schema data extracted from the ManifestJson.

        Raises:
            Exception: If an error occurs while retrieving the Alation data.

        """

        tracer, logger = LoggerSingleton.instance(
            NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
        ).initialize_logging_and_tracing()

        with tracer.start_as_current_span("fetch_schema_data"):
            try:
                data = {}
                data["submitting_user"] = SUBMITTING_USER
                data["title"] = self.title
                data["description"] = self.format_description()
                # data['Release Date']    = self.releasedate
                data["Homepage URL"] = self.homepageUrl
                data["Identifier"] = self.identifier
                # data['Format']          = self.dataformat
                data["License"] = self.license
                # arrays
                # data['tags']            = self.tags
                # data['Language']        = self.language
                data["Is Referenced By"] = self.referencedBy
                data["Geographic Coverage"] = self.geographicCoverage
                data["Temporal Applicability"] = self.temporalApplicability
                data["References"] = self.references
                # self.alationdata = json.dumps(data)
                return data
            except Exception as ex:
                error_msg = "Error: %s", ex
                exc_info = sys.exc_info()
                LoggerSingleton.instance(
                    NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
                ).error_with_exception(error_msg, exc_info)
                raise

    def validate_json(self, json_data, schema):
        """
        Validates JSON data against a given schema.

        Args:
            json_data (dict): The JSON data to be validated.
            schema (dict): The JSON schema to validate against.

        Returns:
            bool: True if the JSON data is valid according to the schema.

        Raises:
            jsonschema.exceptions.ValidationError: If the JSON data fails validation against the schema.
            Exception: If an error occurs during validation.
        """

        tracer, logger = LoggerSingleton.instance(
            NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
        ).initialize_logging_and_tracing()

        with tracer.start_as_current_span("validate_json"):
            try:
                validate(instance=json_data, schema=schema)
                logger.info("Validation complete")
            except jsonschema.exceptions.ValidationError as ex:
                error_msg = "Error: %s", ex
                exc_info = sys.exc_info()
                LoggerSingleton.instance(
                    NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
                ).error_with_exception(error_msg, exc_info)
                raise
            return True

    @staticmethod
    def print_manifest(manifest_object):
        """
        Print the key-value pairs of a dictionary in a user-friendly format.

        This function takes a dictionary (manifest_object) as input and prints its key-value pairs in a formatted way.
        Each key-value pair is printed on a separate line, where the key and value are separated by a colon.
        The keys are printed as strings, and the values are printed using their respective string representations.

        Args:
            manifest_object (dict): The dictionary to be printed.

        Returns:
            None: This function does not return anything. It directly prints the key-value pairs.

        Example:
            >>> my_dict = {'name': 'John', 'age': 30, 'city': 'New York'}
            >>> print_manifest(my_dict)
            name: John
            age: 30
            city: New York
        """
        for (
            item_k,
            item_v,
        ) in manifest_object.items():
            print("{0}: {1}".format(item_k, item_v))

    def get_submitting_user_from_manifest_file(self, manifest_file_path):
        """
        Retrieves the submitting user from a manifest JSON file.

        Args:
            manifest_file_path (str): The path to the manifest JSON file.

        Returns:
            str: The submitting user extracted from the manifest.

        Raises:
            Exception: If an error occurs while retrieving the submitting user.

        """

        tracer, logger = LoggerSingleton.instance(
            NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
        ).initialize_logging_and_tracing()

        with tracer.start_as_current_span("get_submitting_user_from_manifest_file"):
            try:
                data_definition_file_path = open(
                    self.data_definition_file_path, encoding="utf-8"
                )
                logger.info(f"data_definition_file_path: {data_definition_file_path}")
                manifest_file = open(manifest_file_path, encoding="utf-8")
                manifest_file_json = json.load(manifest_file)
                submitting_user = manifest_file_json.get(
                    "submitting_user", SUBMITTING_USER
                )
                return submitting_user
            except Exception as ex:
                error_msg = "Error: %s", ex
                exc_info = sys.exc_info()
                LoggerSingleton.instance(
                    NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
                ).error_with_exception(error_msg, exc_info)
                raise

    def validate_manifest(self, manifest_file, data_definition_file_path):
        """
        Validates a manifest JSON file against a JSON schema.

        This method validates the provided manifest JSON file against the given JSON schema file.
        It reads both the manifest and schema files, loads them as JSON data, and then performs validation using the jsonschema library.

        Args:
            manifest_file (str): The path to the manifest JSON file for validation.
            data_definition_file_path (str): The path to the JSON schema file used for validation.

        Returns:
            tuple: A tuple containing an HTTP status code (200 if successful) and a success message.

        Raises:
            jsonschema.exceptions.ValidationError: If the manifest JSON data fails validation against the schema.
            FileNotFoundError: If the specified schema file or manifest file does not exist.
            json.JSONDecodeError: If the schema file or manifest file contains invalid JSON data.

        Important Note:
            - The data_definition_file_path should point to a valid JSON schema file.
            - The method uses the `jsonschema` library to validate the manifest JSON against the provided schema.

        Example:
            >>> my_manifest_file = "path/to/my_manifest.json"
            >>> my_excel_data_definition_file = "path/to/my_schema.json"
            >>> manifest_validator = ManifestJson()
            >>> http_status_code, message = manifest_validator.validate_manifest(my_manifest_file, my_excel_data_definition_file)
            >>> print(f"Validation status: {http_status_code}")
            >>> print(message)
            Validation status: 200
            Success
        """

        tracer, logger = LoggerSingleton.instance(
            NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
        ).initialize_logging_and_tracing()

        with tracer.start_as_current_span("validate_manifest"):
            try:
                excel_data_definition_file = open(
                    data_definition_file_path, "r", encoding="utf-8"
                )
                excel_data_definition_file_json = json.load(excel_data_definition_file)
                manifest_file = open(manifest_file, "r", encoding="utf-8")
                manifest_json = json.load(manifest_file)

                self.validate_json(manifest_json, excel_data_definition_file_json)
                logger.info("ManifestJson schema is valid")
                message = self.set_alation_data(manifest_json)
                return message
            except Exception as ex:
                error_msg = "Error: %s", ex
                exc_info = sys.exc_info()
                LoggerSingleton.instance(
                    NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
                ).error_with_exception(error_msg, exc_info)
                raise

    def get_manifest_expected_fields(self):
        """
        Reads the manifest JSON file and extracts expected fields for schema, table, and column objects.

        Returns:
            tuple: A tuple containing dictionaries of expected fields for schema, table, and column objects.

        Raises:
            FileNotFoundError: If the specified schema file does not exist.
            JSONDecodeError: If the schema file is not a valid JSON.

        """

        tracer, logger = LoggerSingleton.instance(
            NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
        ).initialize_logging_and_tracing()

        with tracer.start_as_current_span("get_manifest_expected_fields"):
            try:
                data_definition_file_path = open(
                    self.data_definition_file_path, encoding="utf-8"
                )
                schema = json.load(data_definition_file_path)
                schema_fields = {}
                table_fields = {}
                column_fields = {}
                for prop_field in schema["properties"]:
                    # do not add properties blank_field_examples for tables, columns, this info will be extracted from alation obj strucutre
                    if prop_field not in ["tables", "columns"]:
                        schema_fields[prop_field] = schema["properties"][
                            prop_field
                        ].get("blank_field_examples")
                for prop_field in schema["$defs"]["table"]["properties"]:
                    # do not add properties blank_field_examples for tables, columns, this info will be extracted from alation obj strucutre
                    if prop_field not in ["columns"]:
                        table_fields[prop_field] = schema["$defs"]["table"][
                            "properties"
                        ][prop_field]["blank_field_examples"]
                for prop_field in schema["$defs"]["column"]["properties"]:
                    column_fields[prop_field] = schema["$defs"]["column"]["properties"][
                        prop_field
                    ]["blank_field_examples"]

                table_required_fields = schema["$defs"]["table"]["required"]

                return schema_fields, table_fields, column_fields, table_required_fields

            except Exception as ex:
                error_msg = "Error: %s", ex
                exc_info = sys.exc_info()
                LoggerSingleton.instance(
                    NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
                ).error_with_exception(error_msg, exc_info)
                raise
