"""Module to conditionally execute load logic for bronze datasets based on project metadata
   including creating Databricks database and/or tables.
"""

# core
import sys  # don't remove required for error handling
import os

# libraries and execution
from importlib import util
import pathlib


# LAVA
from cdh_lava_core.databricks_service import dataset_convert as dbx_ds_convert
from cdh_lava_core.databricks_service import dataset_crud as dbx_ds_crud
from cdh_lava_core.databricks_service import dataset_core as dbx_ds_core
from cdh_lava_core.az_storage_service.az_storage_file import AzStorageFile


current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.join(current_dir, os.pardir)  # Moves up one directory
grandparent_dir = os.path.join(parent_dir, os.pardir)  # Moves up another directory
sys.path.insert(0, grandparent_dir)  # Adds the grandparent directory to sys.path

# types
from datetime import datetime

OS_NAME = os.name
sys.path.append("..")

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

# spark
from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.functions import lit, concat_ws, to_date, lpad, expr
from pyspark.sql.types import StringType

pyspark_pandas_loader = util.find_spec("pyspark.pandas")
pyspark_pandas_found = pyspark_pandas_loader is not None

if pyspark_pandas_found:
    os.environ["PYARROW_IGNORE_TIMEZONE"] = "1"
    import pyspark.pandas as pd

    # bug - pyspark version will not read local files in the repo
    # import pandas as pd
else:
    import pandas as pd


# Get the currently running file name
NAMESPACE_NAME = os.path.basename(os.path.dirname(__file__))
# Get the parent folder name of the running file
SERVICE_NAME = os.path.basename(__file__)

from cdh_lava_core.cdc_log_service.environment_logging import LoggerSingleton


class DataSetMetaData:
    """
    Class to conditionally execute load logic for bronze datasets based on
    project metadata including creating Databricks database and/or tables.
    """

    @classmethod
    def save_dataset(
        cls,
        config,
        spark,
        dbutils,
        bronze_sps_config_columns_df,
        config_dataset,
        data_product_id: str,
        environment: str,
    ):
        """Saves dataframe as a parquet dataset in databricks

        Args:
            config (_type_): config dictionary for environment
            spark (_type_): spark object
            dbutils (_type_): _dbutils object
            bronze_sps_config_columns_df (_type_): dataframe with column configuration
            config_dataset (_type_): config dictionary for dataset

        Returns:
            Success: True if dataset saves sucessfully
        """

        tracer, logger = LoggerSingleton.instance(
            NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
        ).initialize_logging_and_tracing()

        with tracer.start_as_current_span("save_dataset"):
            try:
                obj_ds_core = dbx_ds_core.DataSetCore()
                obj_ds_crud = dbx_ds_crud.DataSetCrud()
                obj_ds_convert = dbx_ds_convert.DataSetConvert()
                obj_environment_file = AzStorageFile()

                # Environment Variables
                environment = config["environment"]
                first_row_is_header = True
                delimiter = ","
                ingesttimestamp = datetime.now()
                tenant_id = config["az_sub_tenant_id"]
                client_id = config["az_sub_client_id"]
                client_secret = config["client_secret"]

                running_local = (
                    "dbutils" in locals() or "dbutils" in globals()
                ) is not True
                if running_local is True:
                    spark = SparkSession.builder.appName(
                        "cdc_data_ecosystem"
                    ).getOrCreate()

                yyyy_param = config["yyyy"]
                if yyyy_param is None:
                    yyyy_param = ""
                mm_param = config["mm"]
                if mm_param is None:
                    mm_param = ""
                dd_param = config["dd"]
                if dd_param is None:
                    dd_param = ""

                # Dataset Variables
                # TODO Dataset Unused variables
                data_product_id = config["data_product_id"]
                is_required_for_synapse = config_dataset["is_required_for_synapse"]
                is_required_for_power_bi = config_dataset["is_required_for_power_bi"]
                folder_name = config_dataset["folder_name"]
                transmission_period = config_dataset["transmission_period"]
                optimize_type = config_dataset["optimize_type"]
                optimize_columns = config_dataset["optimize_columns"]
                is_refreshed = config_dataset["is_refreshed"]
                is_active = config_dataset["is_active"]
                logger.info(f"is_active: {str(is_active)}")
                if is_active is False:
                    return
                dataset_name = config_dataset["dataset_name"]
                logger.info(
                    f"-----------Begin Save Dataset: {dataset_name}-------------"
                )

                row_id_keys = config_dataset["row_id_keys"]
                if row_id_keys is None:
                    row_id_keys = ""

                incremental = config_dataset["incremental"]
                encoding = config_dataset["encoding"]
                file_format = config_dataset["file_format"]
                column_ordinal_sort = config_dataset["column_ordinal_sort"]
                source_abbreviation = config_dataset["source_abbreviation"]
                partition_by = config_dataset["partition_by"]
                file_name = config_dataset["file_name"]
                dataset_file_path = config_dataset["dataset_file_path"]
                ingress_file_path = config_dataset["ingress_file_path"]
                source_json_path = config_dataset["source_json_path"]
                source_dataset_name = config_dataset["source_dataset_name"]
                is_using_dataset_folder_path_override = config_dataset[
                    "is_using_dataset_folder_path_override"
                ]
                full_dataset_name = config_dataset["full_dataset_name"]

                if "pii_columns" in config_dataset:
                    pii_columns = config_dataset["pii_columns"]
                else:
                    pii_columns = ""

                delimiter = ","
                file_format = file_format.strip()
                file_format = file_format.lower()
                if file_format == "delta":
                    file_format = "parquet_delta"

                ingesttimestamp = datetime.now()

                ingress_file_exists = obj_environment_file.file_exists(
                    running_local,
                    ingress_file_path,
                    data_product_id,
                    environment,
                    dbutils,
                    client_id,
                    client_secret,
                    tenant_id,
                )
                if ingress_file_exists is False and file_format != "delta_sql":
                    logger.error(f"ERROR: could not find file: {ingress_file_path}")

                if encoding != "UNICODE":
                    encoding = "UTF-8"
                logger.info("encoding: " + encoding)

                is_using_standard_column_names = config[
                    "is_using_standard_column_names"
                ]
                logger.info(
                    f"is_using_standard_column_names:{is_using_standard_column_names}"
                )
                is_using_standard_column_names = (
                    is_using_standard_column_names.strip().lower()
                )

                # CSV, TSV, OR USV
                if file_format == "csv" or file_format == "tsv" or file_format == "usv":
                    if file_format == "tsv":
                        delimiter = "\t"

                    if file_format == "usv":
                        delimiter = "\u0001"
                        # delimiter = '\u241F'

                    logger.info("delimiter: " + delimiter)
                    unsorted_df = obj_ds_convert.convert_csv_tsv_usv_to_dataframe(
                        spark,
                        ingress_file_path,
                        first_row_is_header,
                        delimiter,
                        encoding,
                        data_product_id,
                        environment,
                    )

                # PARQUET
                elif file_format == "parquet":
                    logger.info(
                        "attempting to load dataframe for - parquet:"
                        + ingress_file_path
                    )
                    unsorted_df = (
                        spark.read.format("parquet")
                        .option("treatEmptyValuesAsNulls", "true")
                        .load(
                            ingress_file_path, forceLowercaseNames=True, inferLong=True
                        )
                    )

                # PARQUET_DELTA
                elif file_format == "parquet_delta":
                    logger.info("attempting to load dataframe for - ")
                    logger.info(f"delta ingress_file_path: {ingress_file_path}")

                    unsorted_df = (
                        spark.read.format("delta")
                        .option("treatEmptyValuesAsNulls", "true")
                        .load(ingress_file_path)
                    )

                # DELTA_SQL
                elif file_format == "delta_sql":
                    logger.info(
                        f"attempting to load dataframe for dataset_name:{dataset_name}"
                    )
                    logger.info(f"file_name:{file_name}")

                    file_name = file_name.replace("{{environment}}", environment)
                    unsorted_df = spark.sql(file_name)

                # XPT
                elif file_format == "xpt":
                    logger.info(
                        f"attempting to load dataframe for dataset_name:{dataset_name}"
                    )
                    logger.info(f"file_name:{file_name}")
                    # unsorted_df = obj_ds_convert.convert_xpt_to_dataframe(spark, ingress_file_path, tenant_id, client_id
                    # client_secret)
                    (
                        schema_df,
                        unsorted_df,
                    ) = obj_ds_convert.convert_sas_mount_to_dataframe_with_schema(
                        spark,
                        source_abbreviation,
                        file_name,
                        tenant_id,
                        client_id,
                        client_secret,
                        data_product_id,
                        environment,
                    )
                # SAS7BDAT
                elif file_format == "sas7bdat":
                    logger.info(
                        f"attempting to load dataframe for dataset_name:{dataset_name}"
                    )
                    logger.info(f"file_name:{file_name}")
                    unsorted_df = obj_ds_convert.convert_sas_to_dataframe(
                        spark,
                        ingress_file_path,
                        tenant_id,
                        client_id,
                        client_secret,
                        data_product_id,
                        environment,
                    )

                    # unsorted_df = (spark.read
                    #                    .format("com.github.saurfang.sas.spark")
                    #                    .option("forceLowercaseNames", True)
                    #                    .option("inferLong", True)
                    #                    .option("inferDecimal", True)
                    #                    .option("inferInteger", True)
                    #                    .option("inferSchema", True)
                    #                    .load(ingress_file_path, forceLowercaseNames=True, inferLong=True,
                    #                          inferDecimal=True, inferInteger=True))

                # JSON
                elif file_format == "json":
                    unsorted_df = obj_ds_convert.convert_json_to_dataframe(
                        spark,
                        ingress_file_path,
                        encoding,
                        source_json_path,
                        source_dataset_name,
                        dataset_name,
                        data_product_id,
                        environment,
                    )

                # XLSX
                elif file_format == "xlsx":
                    sheet_name = config_dataset["sheet_name"]
                    skip_rows = config_dataset["column_header_skip_rows"]
                    unsorted_df = obj_ds_convert.convert_xlsx_to_dataframe(
                        spark,
                        ingress_file_path,
                        sheet_name,
                        tenant_id,
                        client_id,
                        client_secret,
                        skip_rows,
                        data_product_id,
                        environment,
                    )
                else:
                    logger.info(f"Unsupported file_format:{file_format}")
                    unsorted_df = None

                logger.info(
                    f"loaded dataframe for ingress_file_path: {ingress_file_path}"
                )
                if unsorted_df is not None:
                    if unsorted_df.count() > 0:
                        is_empty = False
                    else:
                        is_empty = True
                else:
                    is_empty = True

                if unsorted_df is not None and is_empty is False:
                    unsorted_df = unsorted_df.withColumn(
                        "__meta_ingress_file_path", lit(ingress_file_path)
                    )

                    logger.info("Adding custom columns")
                    sorted_df = cls.add_custom_columns(
                        unsorted_df,
                        column_ordinal_sort,
                        bronze_sps_config_columns_df,
                        config_dataset,
                        config,
                        data_product_id,
                        environment,
                    )

                    # convert column names to lower case if requested
                    if is_using_standard_column_names == "force_lowercase":
                        for col_orig in sorted_df.columns:
                            sorted_df = sorted_df.withColumnRenamed(
                                col_orig, col_orig.lower()
                            )

                    if pii_columns != "":
                        sorted_df = obj_ds_core.encrpyt_pii_columns(
                            pii_columns,
                            is_using_standard_column_names,
                            sorted_df,
                            data_product_id,
                            environment,
                        )

                    if file_format == "parquet_delta":
                        logger.info(
                            f"attempting to add reference for {full_dataset_name}"
                        )
                        logger.info(
                            f"to existing parquet in deltalake in format: {file_format}"
                        )
                        logger.info(f" for dataset_file_path: {dataset_file_path} ")

                    # Begin Save to Delta Lake
                    print(f"---Begin Save Dataset for: {dataset_name}--")
                    if ingress_file_path is not None:
                        parquet_exists = False
                        # parquet_delta external - create an externally linked table to existing parquet file - don't save
                        if (file_format == "parquet_delta") and (
                            dataset_file_path != "" or dataset_file_path == ""
                        ):
                            parquet_exists = True

                        if parquet_exists is True and sorted_df is not None:
                            sorted_df.createOrReplaceTempView("dataset_sorted_df")

                            obj_ds_crud.upsert(
                                spark,
                                config,
                                dbutils,
                                sorted_df,
                                full_dataset_name,
                                dataset_file_path,
                                is_using_dataset_folder_path_override,
                                file_format,
                                ingress_file_path,
                                False,
                                partition_by,
                                incremental,
                                data_product_id,
                                environment,
                            )

                        # create/update internally managed table - save to delta lake
                        else:
                            if sorted_df is not None and sorted_df.count() > 0:
                                sorted_df = obj_ds_core.add_row_id_to_dataframe(
                                    sorted_df,
                                    row_id_keys,
                                    yyyy_param,
                                    mm_param,
                                    dd_param,
                                    data_product_id,
                                    environment,
                                )
                                logger.info(
                                    f"attempting to update deltalake for {full_dataset_name}"
                                )
                                logger.info(
                                    f"with merged data in format: {file_format} for "
                                )
                                logger.info(f"ingress_file_path: {ingress_file_path}")
                                sorted_df = sorted_df.withColumn(
                                    "meta_dd", sorted_df["meta_dd"].cast(StringType())
                                )
                                sorted_df = sorted_df.withColumn(
                                    "meta_ingesttimestamp", lit(ingesttimestamp)
                                )
                                sorted_df.createOrReplaceTempView("dataset_sorted_df")

                                # incremental update - add/update existing table based on row_id
                                if incremental == "incremental":
                                    logger.info(
                                        f"incremental:{incremental} display sorted_df for: {dataset_name}"
                                    )
                                    logger.info(
                                        f"Load from: {ingress_file_path} for: {dataset_file_path} with "
                                    )
                                    logger.info(f"count: {str(sorted_df.count())}")
                                    if row_id_keys is None:
                                        row_id_keys = ""
                                    row_id_keys = row_id_keys.strip()
                                    row_id_keys_list = row_id_keys.split(",")
                                    if (
                                        len(row_id_keys_list) > 0
                                        and len(row_id_keys) > 0
                                    ):
                                        sql_expr = row_id_keys
                                        sql_expr = sql_expr.replace(
                                            "{yyyy}", yyyy_param
                                        )
                                        sql_expr = sql_expr.replace("{mm}", mm_param)
                                        sql_expr = sql_expr.replace("{dd}", dd_param)
                                    else:
                                        sql_expr = "uuid()"

                                    sql_expr = "concat_ws('-'," + sql_expr + ")"
                                else:
                                    sql_expr = "uuid()"
                                    sql_expr = "concat_ws('-'," + sql_expr + ")"

                                logger.info(f"row_id formula: sql_expr: {sql_expr}")
                                sorted_df = sorted_df.withColumn(
                                    "row_id", expr(sql_expr)
                                )
                                logger.info(
                                    f"attempting to update deltalake for {full_dataset_name} "
                                )
                                logger.info(
                                    f"with merged data in format: {file_format} for "
                                )
                                logger.info(f"ingress_file_path: {ingress_file_path}")

                                logger.info(
                                    f"refresh sorted_df.count: {sorted_df.count()}"
                                )
                                obj_ds_crud.upsert(
                                    spark,
                                    config,
                                    dbutils,
                                    sorted_df,
                                    full_dataset_name,
                                    dataset_file_path,
                                    is_using_dataset_folder_path_override,
                                    file_format,
                                    ingress_file_path,
                                    False,
                                    partition_by,
                                    incremental,
                                    data_product_id,
                                    environment,
                                )
                                logger.info("updated deltalake with merged data")
                                logger.info(f"in format: {file_format}")
                                logger.info(f"for: {ingress_file_path}")
                            else:
                                sorted_df.createOrReplaceTempView("dataset_sorted_df")

                                logger.info(
                                    f"Error: sorted_df is None for dataset_name:{dataset_name}: for "
                                )
                                logger.info(
                                    f"ingress_file_path: {ingress_file_path}: for dataset_file_path: {dataset_file_path}"
                                )

                            # save metadata to delta lake with detailed quality and performance metrics
                            logger.info(
                                f"---Begin Save Dataset Meta-Data for: {dataset_name}--"
                            )

                            obj_ds_crud = dbx_ds_crud.DataSetCrud()
                            if sorted_df is None:
                                logger.error("Error: sorted_df is None")
                            else:
                                schema_df = None
                                logger.info(
                                    "sorted_df.count: " + str(sorted_df.count())
                                )
                                logger.info(
                                    "running obj_ds_crud.get_export_dataset_or_view_schema_config"
                                )
                                config_schema = obj_ds_crud.get_export_dataset_or_view_schema_config(
                                    config,
                                    config_dataset,
                                    spark,
                                    sorted_df,
                                    "dataset",
                                    data_product_id,
                                    environment,
                                )
                                schema_dataset_df = config_schema["schema_dataset_df"]
                                schema_column_df = config_schema["schema_column_df"]

                                logger.info(
                                    "running obj_ds_crud.upsert for schema_dataset_df"
                                )
                                obj_ds_crud.upsert(
                                    spark,
                                    config,
                                    dbutils,
                                    schema_dataset_df,
                                    config_schema["schema_full_dataset_name"],
                                    config_schema["schema_dataset_file_path"],
                                    config_schema[
                                        "is_using_dataset_folder_path_override"
                                    ],
                                    "parquet_delta",
                                    ingress_file_path,
                                    False,
                                    config_schema["partitioned_by"],
                                    "incremental",
                                    data_product_id,
                                    environment,
                                )

                                obj_ds_crud.upsert(
                                    spark,
                                    config,
                                    dbutils,
                                    schema_column_df,
                                    config_schema["schema_full_dataset_name"],
                                    config_schema["schema_dataset_file_path"],
                                    config_schema[
                                        "is_using_dataset_folder_path_override"
                                    ],
                                    "parquet_delta",
                                    ingress_file_path,
                                    False,
                                    config_schema["partitioned_by"],
                                    "incremental",
                                    data_product_id,
                                    environment,
                                )
                    else:
                        ingress_file_path = ""
                        logger.info("Ingress_file_path is missing")

                return True

            except Exception as ex:
                error_msg = "Error: %s", ex
                exc_info = sys.exc_info()
                LoggerSingleton.instance(
                    NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
                ).error_with_exception(error_msg, exc_info)
                raise

    @staticmethod
    def file_exists(
        config: dict, path: str, dbutils, data_product_id: str, environment: str
    ) -> bool:
        """Takes in path, dbutils object, returns whether file exists at provided path

        Args:
            config: config dictionary
            path (str): path to file
            dbutils (object): databricks dbutils

        Returns:
            bool: True/False indication if file exists
        """

        tracer, logger = LoggerSingleton.instance(
            NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
        ).initialize_logging_and_tracing()

        with tracer.start_as_current_span("save_dataset"):
            try:
                running_local = config["running_local"]

                if running_local is True:
                    b_exists = os.path.exists(path)
                else:
                    try:
                        path = path.replace("/dbfs", "")
                        if dbutils is not None:
                            dbutils.fs.ls(path)
                            b_exists = True
                        else:
                            b_exists = False
                    except Exception as exception_result:
                        if "java.io.FileNotFoundException" in str(exception_result):
                            logger.error(exception_result)
                            b_exists = False
                        else:
                            b_exists = False
                            raise

                return b_exists

            except Exception as ex:
                error_msg = "Error: %s", ex
                exc_info = sys.exc_info()
                LoggerSingleton.instance(
                    NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
                ).error_with_exception(error_msg, exc_info)
                raise

    @classmethod
    def add_custom_columns(
        cls,
        unsorted_df: DataFrame,
        column_ordinal_sort: str,
        bronze_sps_config_columns_df: DataFrame,
        config_dataset: dict,
        config: dict,
        data_product_id: str,
        environment: str,
    ) -> DataFrame:
        """Add custom columns to a dataframe based on configuration

        Args:
            unsorted_df (DataFrame): initial dataframe that will hold the new column
            column_ordinal_sort (str): ordinal sort number of column
            bronze_sps_config_columns_df (DataFrame): columns configuration dataframe
            config_dataset (dict): dataset configuration dictionary
            config (dict): envrionment configuration dictionary

        Returns:
            DataFrame: DataFrame with custom columns added based on configuration
        """

        tracer, logger = LoggerSingleton.instance(
            NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
        ).initialize_logging_and_tracing()

        with tracer.start_as_current_span("add_custom_columns"):
            try:
                obj_ds_core = dbx_ds_core.DataSetCore()

                data_product_id = config["data_product_id"]
                yyyy_param = config["yyyy"]
                mm_param = config["mm"]
                dd_param = config["dd"]
                ingesttimestamp = datetime.now()
                dataset_name = config_dataset["dataset_name"]
                source_abbreviation = config_dataset["source_abbreviation"]
                filter_clause = config_dataset["filter_clause"]
                transmission_period = config_dataset["transmission_period"]

                if column_ordinal_sort.strip().lower() == "alpha":
                    sorted_df = unsorted_df.select(sorted(unsorted_df.columns))
                else:
                    sorted_df = unsorted_df

                column_count = 0
                custom_function = ""

                if bronze_sps_config_columns_df is not None:
                    column_count = bronze_sps_config_columns_df.count()

                    if column_count == 0:
                        logger.info(
                            f"No column configurations found for dataset: {dataset_name}"
                        )
                    else:
                        dataset_name_full = dataset_name.replace(
                            "{source_abbreviation}", source_abbreviation
                        )
                        filter_clause = f"data_product_id = '{data_product_id}' and dataset_name = '{dataset_name_full}'"
                        logger.info(f"filter_clause:{filter_clause}")
                        df_config_columns_filtered = (
                            bronze_sps_config_columns_df.filter(filter_clause)
                        )
                        logger.info(
                            f"evaluating columns in dataset:{dataset_name} for project: {data_product_id}"
                        )
                        df_config_columns_filtered = df_config_columns_filtered.sort(
                            "column_batch_group"
                        )

                        data_collect = df_config_columns_filtered.collect()
                        i_row = 1
                        for row in data_collect:
                            custom_function = row["custom_function"]
                            column_count = column_count + 1
                            column_name = row["column_name"]
                            column_name_new = row["column_name_new"]
                            column_name = obj_ds_core.scrub_object_name(
                                column_name, data_product_id, environment
                            )
                            column_name_new = obj_ds_core.scrub_object_name(
                                column_name_new, data_product_id, environment
                            )
                            logger.info(
                                f"evaluating column:{str(column_count)} column_name:{column_name}"
                            )

                            date_format = row["date_format"]
                            function = row["function"]
                            if function is None:
                                function = "missing"

                            function = function.strip()
                            function = function.lower()

                            logger.info(
                                f"column_name:{column_name} function:{function}"
                            )

                            if function == "concat_ws":
                                custom_function = str(row["custom_function"])
                                custom_function = custom_function.strip()
                                custom_function = custom_function.replace("\n", "")
                                if custom_function is None:
                                    arg_list = [""]
                                else:
                                    arg_list = [custom_function]

                                logger.info(
                                    f"adding column: {column_name} concat_ws with arg_list: {str(arg_list)}"
                                )
                                sorted_df = sorted_df.withColumn(
                                    column_name, concat_ws("-", *arg_list)
                                )

                            if function == "custom":
                                custom_function = str(row["custom_function"])
                                custom_function = custom_function.strip()

                                if custom_function is None:
                                    custom_function = ""

                                logger.info(f"custom_function: {custom_function}")
                                logger.info(
                                    f"adding column: {column_name} custom_function: {str(custom_function)}"
                                )
                                sorted_df = sorted_df.withColumn(
                                    column_name, expr(custom_function)
                                )

                            if function == "to_date":
                                msg_add = f"adding column: {column_name} , {date_format} , { function} "
                                logger.info(msg_add)
                                sorted_df = sorted_df.withColumn(
                                    column_name, to_date(column_name, date_format)
                                )

                            if function == "withcolumnrenamed":
                                logger.info(
                                    f"rename column: {column_name} to column_name_new {column_name_new}"
                                )
                                sorted_df = sorted_df.withColumnRenamed(
                                    column_name, column_name_new
                                )
                                column_metadata = (
                                    sorted_df.select("*")
                                    .schema[column_name_new]
                                    .metadata
                                )
                                logger.info("column_metadata:", column_metadata)
                                sorted_df = sorted_df.withMetadata(
                                    column_name_new,
                                    {
                                        "ingress_column_name": column_name,
                                        "comment": column_name,
                                    },
                                )
                            i_row = i_row + 1

                if "year" in sorted_df.columns:
                    sorted_df = sorted_df.withColumn(
                        "year", sorted_df["year"].cast(StringType())
                    )

                if "Year" in sorted_df.columns:
                    sorted_df = sorted_df.withColumn(
                        "Year", sorted_df["Year"].cast(StringType())
                    )

                if "transmission_period" not in sorted_df.columns:
                    sorted_df = sorted_df.withColumn(
                        "transmission_period", lit(transmission_period)
                    )

                if "meta_yyyy" not in sorted_df.columns:
                    sorted_df = sorted_df.withColumn("meta_yyyy", lit(yyyy_param))
                else:
                    sorted_df = sorted_df.withColumn(
                        "meta_yyyy", sorted_df["meta_yyyy"].cast(StringType())
                    )

                if "meta_mm" not in sorted_df.columns:
                    sorted_df = sorted_df.withColumn("meta_mm", lit(mm_param))
                else:
                    sorted_df = sorted_df.withColumn(
                        "meta_mm",
                        lpad(sorted_df["meta_mm"].cast(StringType()), 2, "0"),
                    )

                if "meta_dd" not in sorted_df.columns:
                    sorted_df = sorted_df.withColumn("meta_dd", lit(dd_param))
                else:
                    sorted_df = sorted_df.withColumn(
                        "meta_dd", sorted_df["meta_dd"].cast(StringType())
                    )
                sorted_df = sorted_df.withColumn(
                    "meta_ingesttimestamp", lit(ingesttimestamp)
                )

                return sorted_df

            except Exception as ex:
                error_msg = "Error: %s", ex
                exc_info = sys.exc_info()
                LoggerSingleton.instance(
                    NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
                ).error_with_exception(error_msg, exc_info)
                raise

    @staticmethod
    def only_numerics(seq):
        """Take a sequence and return only the numeric items.

        Args:
            seq (any): Any type of object. Only strings are converted.

        Returns:
            any: If seq is type str, returns a string of only numbers.
        """

        seq_type = type(seq)
        if seq_type is str:
            result = seq_type().join(filter(seq_type.isdigit, seq))
        else:
            result = seq
        return result

    @classmethod
    def get_configuration_for_dataset(
        cls, config, dataset_metadata, data_product_id, environment
    ):
        """Retrieves configuration dictionary for dataset based on business rule configuration

        Args:
            config (dict): The configuration dictionary containing various parameters.
            dataset_metadata (dict): The metadata dictionary for the dataset.

        Returns:
            dict: The configuration dictionary for the dataset.
        """

        tracer, logger = LoggerSingleton.instance(
            NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
        ).initialize_logging_and_tracing()

        with tracer.start_as_current_span("get_configuration_for_dataset"):
            try:
                obj_ds_core = dbx_ds_core.DataSetCore()
                row = dataset_metadata
                data_product_id_individual = config["data_product_id_individual"]
                data_product_id = config["data_product_id"]
                environment = config["environment"]
                yyyy_param = config["yyyy"]
                mm_param = config["mm"]
                dd_param = config["dd"]
                ingress_folder = config["cdh_folder_ingress"]
                cdh_folder_database = config["cdh_folder_database"]
                cdh_folder_config = config["cdh_folder_config"]

                source_abbreviation = row["source_abbreviation"]
                if source_abbreviation is None:
                    source_abbreviation = ""
                else:
                    source_abbreviation = row["source_abbreviation"].lower().strip()
                config_dataset = {"source_abbreviation": source_abbreviation}
                config_dataset["filter_clause"] = ""  # populate this potentially later
                source_json_path = row["source_json_path"]
                if source_json_path is None:
                    source_json_path = ""
                else:
                    source_json_path = row["source_json_path"]
                config_dataset["source_json_path"] = source_json_path

                source_dataset_name = row["source_dataset_name"]
                if source_dataset_name is None:
                    source_dataset_name = ""
                else:
                    source_dataset_name = row["source_dataset_name"]

                config_dataset["source_dataset_name"] = source_dataset_name
                dataset_name = row["dataset_name"]
                if dataset_name is None:
                    dataset_name = ""
                else:
                    dataset_name = (
                        row["dataset_name"]
                        .lower()
                        .strip()
                        .replace("{source_abbreviation}", source_abbreviation)
                    )

                dataset_name = obj_ds_core.scrub_object_name(
                    dataset_name, data_product_id, environment
                )
                config_dataset["dataset_name"] = dataset_name

                print(
                    f"---------------Starting Load of {dataset_name} -----------------"
                )
                row_id_keys = row["row_id_keys"]
                if row_id_keys is None:
                    row_id_keys = ""
                else:
                    row_id_keys = row_id_keys.replace('"', "'")
                config_dataset["row_id_keys"] = row_id_keys

                file_name = row["file_name"]
                config_dataset["file_name"] = file_name

                incremental = row["incremental"]
                if incremental is None:
                    incremental = "incremental"
                else:
                    incremental = incremental.lower().strip()

                config_dataset["incremental"] = incremental

                encoding = row["encoding"]
                if encoding is None:
                    encoding = "UTF-8"
                else:
                    is_string = isinstance(encoding, str)
                    if is_string:
                        encoding = row["encoding"].upper().strip()
                    else:
                        encoding = "UTF-8"
                        print("Error encoding:{str(encoding)} is not a string")

                config_dataset["encoding"] = encoding

                database_name = config["cdh_database_name"]

                full_dataset_name = database_name + "." + dataset_name
                config_dataset["full_dataset_name"] = full_dataset_name

                frequency = row["frequency"]
                if frequency is None:
                    frequency = "daily"
                else:
                    frequency = row["frequency"].lower().strip()
                config_dataset["frequency"] = frequency

                if frequency == "monthly":
                    transmission_period = mm_param + "_" + yyyy_param
                    dd_param = "NA"
                else:
                    transmission_period = yyyy_param + "_" + mm_param + "_" + dd_param
                config_dataset["transmission_period"] = transmission_period

                optimize_type = row["optimize_type"]
                if optimize_type is not None:
                    optimize_type = row["optimize_type"].lower().strip()
                config_dataset["optimize_type"] = optimize_type

                optimize_columns = row["optimize_columns"]
                if optimize_columns is not None:
                    optimize_columns = row["optimize_columns"].lower().strip()
                config_dataset["optimize_columns"] = optimize_columns

                pii_columns = row["pii_columns"]
                if pii_columns is not None:
                    pii_columns = pii_columns.lower().strip()
                    # pii_columns = pii_columns.replace("'", "")

                partition_by = row["partition_by"]
                if partition_by is not None:
                    if len(partition_by.strip()) == 0:
                        partition_by = None
                    elif partition_by.strip().lower() == "unspecified":
                        partition_by = None
                    elif partition_by == "none":
                        partition_by = None

                config_dataset["partition_by"] = partition_by

                file_format = row["format"].lower()
                config_dataset["file_format"] = file_format

                entity = row["entity"]
                if entity is None:
                    entity = ""
                config_dataset["entity"] = entity

                sheet_name = row["sheet_name"]
                if sheet_name is None:
                    sheet_name = ""
                config_dataset["sheet_name"] = sheet_name

                column_header_skip_rows = row["column_header_skip_rows"]
                if column_header_skip_rows is None:
                    column_header_skip_rows = 0
                else:
                    column_header_skip_rows = int(
                        cls.only_numerics(column_header_skip_rows)
                    )
                config_dataset["column_header_skip_rows"] = column_header_skip_rows

                folder_name_source = row["folder_name_source"]
                if folder_name_source is None:
                    folder_name_source = "default_rule"
                if folder_name_source.strip() == "":
                    folder_name_source = ""

                if folder_name_source == "use_folder_name_column":
                    is_using_dataset_folder_path_override = True
                else:
                    is_using_dataset_folder_path_override = False

                config_dataset["folder_name"] = row["folder_name"]

                config_dataset[
                    "is_using_dataset_folder_path_override"
                ] = is_using_dataset_folder_path_override

                is_refreshed = row["is_refreshed"]

                remove_columns_with_no_metadata = row["remove_columns_with_no_metadata"]
                if (
                    remove_columns_with_no_metadata is None
                    or remove_columns_with_no_metadata == ""
                ):
                    remove_columns_with_no_metadata = False
                if (
                    remove_columns_with_no_metadata == "False"
                    or remove_columns_with_no_metadata == "false"
                ):
                    remove_columns_with_no_metadata = False
                if remove_columns_with_no_metadata == "FALSE":
                    remove_columns_with_no_metadata = False

                if remove_columns_with_no_metadata is not False:
                    remove_columns_with_no_metadata = True

                config_dataset["remove_columns_with_no_metadata"] = is_refreshed

                config_dataset["is_refreshed"] = is_refreshed

                is_required_for_power_bi = row["is_required_for_power_bi"]
                config_dataset["is_required_for_power_bi"] = is_required_for_power_bi

                is_required_for_synapse = row["is_required_for_synapse"]
                config_dataset["is_required_for_synapse"] = is_required_for_synapse

                column_ordinal_sort = row["column_ordinal_sort"]
                if column_ordinal_sort is None:
                    column_ordinal_sort = "alpha"
                column_ordinal_sort = column_ordinal_sort.lower().strip()
                config_dataset["column_ordinal_sort"] = column_ordinal_sort

                ingress_file_name = row["file_name"]
                ingress_file_name = ingress_file_name.replace(
                    "{transmission_period}", transmission_period
                )
                ingress_file_name = ingress_file_name.replace(
                    "{source_abbreviation}", source_abbreviation
                )
                if ingress_file_name.startswith("/"):
                    ingress_file_name = ingress_file_name[1:]
                config_dataset["ingress_file_name"] = ingress_file_name

                incremental = incremental.strip().lower()
                if (
                    incremental == "incremental"
                    or incremental == "none"
                    or incremental == "incremental_with_purge"
                ):
                    is_incremental = True
                else:
                    is_incremental = False
                config_dataset["is_incremental"] = is_incremental

                is_active = row["is_active"]
                if isinstance(is_active, str):
                    logger.info(f"is_active is string: {is_active}")
                    is_active = is_active.strip().lower()
                    if is_active == "false":
                        is_active = False
                    else:
                        is_active = True
                else:
                    logger.info("is_active is not string")
                    if is_active is None:
                        is_active = False
                    elif is_active is False:
                        is_active = False
                    else:
                        is_active = True
                    logger.info("is_active is now: " + str(is_active))

                config_dataset["is_active"] = is_active

                folder_file_ingress_path_override = row["folder_name"]
                if folder_file_ingress_path_override is None:
                    folder_file_ingress_path_override = ""
                else:
                    folder_file_ingress_path_override = (
                        folder_file_ingress_path_override.strip()
                    )

                data_product_id = config["data_product_id"]
                data_product_id_root = config["data_product_id_root"]
                folder_file_ingress_path_override = row["folder_name"]
                if folder_file_ingress_path_override is not None:
                    folder_file_ingress_path_override = (
                        folder_file_ingress_path_override.replace(
                            "{data_product_id_individual}", data_product_id_individual
                        )
                    )
                    folder_file_ingress_path_override = (
                        folder_file_ingress_path_override.replace(
                            "{data_product_id_root}", data_product_id_root
                        )
                    )
                    folder_file_ingress_path_override = (
                        folder_file_ingress_path_override.replace(
                            "{data_product_id}", data_product_id
                        )
                    )
                    folder_file_ingress_path_override = (
                        folder_file_ingress_path_override.replace(
                            "{ingress_folder}", ingress_folder
                        )
                    )
                    folder_file_ingress_path_override = (
                        folder_file_ingress_path_override.replace("{entity}", entity)
                    )
                    folder_file_ingress_path_override = (
                        folder_file_ingress_path_override.replace(
                            "{source_abbreviation}", source_abbreviation
                        )
                    )
                    folder_file_ingress_path_override = (
                        folder_file_ingress_path_override.replace(
                            "{environment}", environment
                        )
                    )

                    folder_file_ingress_path_override = (
                        folder_file_ingress_path_override.replace(
                            "{cdh_folder_config}", cdh_folder_config
                        )
                    )

                # Pull from external place - reference parquet
                if folder_file_ingress_path_override is None:
                    folder_file_ingress_path_override = ""

                logger.info(
                    f"folder_file_ingress_path_override:{folder_file_ingress_path_override}"
                )
                logger.info(f"ingress_file_name:{ingress_file_name}")

                if (
                    file_format == "parquet_delta"
                    and folder_file_ingress_path_override != ""
                ):
                    ingress_file_path = (
                        folder_file_ingress_path_override.rstrip("/")
                        + "/"
                        + ingress_file_name
                    )
                    dataset_file_path = ingress_file_path
                elif (
                    file_format == "sas7bdat"
                    and folder_file_ingress_path_override != ""
                ):
                    dataset_file_path = cdh_folder_database + "/" + dataset_name
                    dataset_file_path = dataset_file_path.replace("dbfs:", "")
                    ingress_file_path = (
                        folder_file_ingress_path_override.rstrip("/")
                        + "/"
                        + ingress_file_name
                    )
                else:
                    # Build folder name
                    dataset_file_path = cdh_folder_database + "/" + dataset_name
                    dataset_file_path = dataset_file_path.replace("dbfs:", "")
                    if is_using_dataset_folder_path_override is True:
                        ingress_file_path = (
                            folder_file_ingress_path_override + ingress_file_name
                        )
                    else:
                        ingress_file_path = (
                            ingress_folder.rstrip("/") + "/" + source_abbreviation
                        )
                        ingress_file_path = ingress_file_path + "/" + ingress_file_name

                config_dataset["dataset_file_path"] = dataset_file_path

                ingress_file_path = ingress_file_path.strip()

                config_dataset["ingress_file_path"] = ingress_file_path

                # logging
                logger.info(config_dataset)
                return config_dataset

            except Exception as ex:
                error_msg = "Error: %s", ex
                exc_info = sys.exc_info()
                LoggerSingleton.instance(
                    NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
                ).error_with_exception(error_msg, exc_info)
                raise

    @classmethod
    def copy_ingress_file(
        cls, config, config_dataset, data_product_id, environment
    ) -> str:
        """copy ingress file to the azure

        Args:
            config (_type_): config dictionary for environment
            dbutils (_type_): _dbutils object
            config_dataset (_type_): config dictionary for dataset

        Returns:
            Copy ingress file status
        """

        tracer, logger = LoggerSingleton.instance(
            NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
        ).initialize_logging_and_tracing()

        with tracer.start_as_current_span("copy_ingress_file"):
            try:
                obj_environment_file = AzStorageFile()
                ingress_file_path = config_dataset["ingress_file_path"]
                ingress_file_name = config_dataset["ingress_file_name"]
                ingress_file_path = config_dataset["ingress_file_path"]
                dest_file_path = pathlib.Path(ingress_file_path)
                dest_path = str(dest_file_path.parent)
                dest_path = dest_path.replace("abfss:/", "abfss://")
                print(f"dest_path:{dest_path}")
                dest_path = obj_environment_file.convert_abfss_to_https_path(
                    dest_path, data_product_id, environment
                )
                print(f"dest_path_converted:{dest_path}")
                src_url = config_dataset["source_dataset_name"]
                print(f"src_url:{src_url}")
                result = obj_environment_file.copy_url_to_blob(
                    config,
                    src_url,
                    dest_path,
                    ingress_file_name,
                    data_product_id,
                    environment,
                )

                logger.info(f"result:{result}")
                return result

            except Exception as ex:
                error_msg = "Error: %s", ex
                exc_info = sys.exc_info()
                LoggerSingleton.instance(
                    NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
                ).error_with_exception(error_msg, exc_info)
                raise
