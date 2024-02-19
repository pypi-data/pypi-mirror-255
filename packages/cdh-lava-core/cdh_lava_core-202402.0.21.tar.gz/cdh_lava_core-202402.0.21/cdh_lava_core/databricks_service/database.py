import sys, os
import json
import requests

OS_NAME = os.name
sys.path.append("../..")

if OS_NAME.lower() == "nt":
    print("environment_logging: windows")
    sys.path.append(os.path.dirname(os.path.abspath(__file__ + "\\..")))
    sys.path.append(os.path.dirname(os.path.abspath(__file__ + "\\..\\..")))
    sys.path.append(os.path.dirname(os.path.abspath(__file__ + "\\..\\..\\..")))
else:
    print("environment_logging: non windows")
    sys.path.append(os.path.dirname(os.path.abspath(__file__ + "/..")))
    sys.path.append(os.path.dirname(os.path.abspath(__file__ + "/../..")))
    sys.path.append(os.path.dirname(os.path.abspath(__file__ + "/../../..")))

from pyspark.sql import SparkSession, DataFrame

from cdh_lava_core.cdc_log_service.environment_logging import LoggerSingleton

# Get the currently running file name
NAMESPACE_NAME = os.path.basename(os.path.dirname(__file__))
# Get the parent folder name of the running file
SERVICE_NAME = os.path.basename(__file__)


class Database:
    @classmethod
    def setup_databricks_database(cls, config: dict, spark: SparkSession) -> str:
        """Takes in config dictionary, spark object, returns configured spark object

        Args:
            config (dict): global config dictionary
            spark (SparkSession): spark session

        Returns:
            str: folder_database_path
        """

        data_product_id = config["data_product_id"]
        environment = config["environment"]

        tracer, logger = LoggerSingleton.instance(
            NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
        ).initialize_logging_and_tracing()

        with tracer.start_as_current_span("setup_databricks_database"):
            try:
                cdh_database_name = config["cdh_database_name"]
                catalog_name, database_name = cls.parse_database_name(cdh_database_name)
                running_local = config["running_local"]

                if catalog_name is not None:
                    # Check if the database exists
                    sql_statement = (
                        f"show databases in {catalog_name} like '{database_name}'"
                    )
                else:
                    # Check if the database exists with specific location
                    sql_statement = f"show databases like '{database_name}'"

                logger.info(sql_statement)
                databases = spark.sql(sql_statement)

                # Check if the database exists in the result
                if (
                    databases.filter(databases.databaseName == database_name).count()
                    == 0
                ):
                    logger.info(f"Database {database_name} does not exist.")
                    # Handle the scenario where the database does not exist
                    # (e.g., log an error, create the database with necessary permissions, etc.)
                else:
                    logger.info(f"Database {database_name} already exists.")

                # cdh_databricks_owner_group = config["cdh_databricks_owner_group"]
                # sql_statement = f"alter schema {cdh_database_name} owner to `{cdh_databricks_owner_group}`;"
                # print(sql_statement)
                # spark.sql(sql_statement)

                sql_statement = f"Describe database {cdh_database_name}"
                df_db_schema = spark.sql(sql_statement)

                if running_local is True:
                    df_db_schema.show(truncate=False)

                df_db_schema = df_db_schema.filter(
                    df_db_schema.database_description_item == "Location"
                )
                rdd_row = df_db_schema.first()

                if rdd_row is not None:
                    folder_database_path = rdd_row["database_description_value"]
                else:
                    folder_database_path = "missing dataframe value error"

                return folder_database_path

            except Exception as ex:
                error_msg = "Error: %s", ex
                exc_info = sys.exc_info()
                LoggerSingleton.instance(
                    NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
                ).error_with_exception(error_msg, exc_info)
                raise

    @staticmethod
    def parse_database_name(cdh_database_name) -> str:
        """
        Parses the CDH database name and returns the schema name and dataset name.

        Args:
            cdh_database_name (str): The CDH database name to be parsed.

        Returns:
            str: The schema name and dataset name separated by a dot (e.g., "schema.dataset").
                 If the CDH database name is not in the correct format, None is returned for both schema name and dataset name.
        """
        database_name_list = cdh_database_name.split(".")
        if len(database_name_list) == 1:
            catalog_name = None
            database_name = database_name_list[0]
        elif len(database_name_list) == 2:
            catalog_name = database_name_list[0]
            database_name = database_name_list[1]
        elif len(database_name_list) > 2:
            catalog_name = database_name_list[0]
            database_name = database_name_list[1]
        else:
            catalog_name = None
            database_name = None
        return catalog_name, database_name
