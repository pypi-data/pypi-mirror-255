# Databricks notebook source
# mandatory parameters and names. The orchestrator will always pass these
dbutils.widgets.text("data_source", "")
dbutils.widgets.text("delivery_date", "")
dbutils.widgets.text("request_id", "")
dbutils.widgets.text("workflow_id", "")
dbutils.widgets.text("storage_account_name", "")


# where are we reading the files from
dbutils.widgets.text("source_folder", "")
# where are we reading the files from
dbutils.widgets.text("expected_data_file_type", "")

dbutils.widgets.text("manifest_file", "")


# COMMAND ----------

data_source = dbutils.widgets.get("data_source")
delivery_date = dbutils.widgets.get("delivery_date")
request_id = dbutils.widgets.get("request_id")
workflow_id = dbutils.widgets.get("workflow_id")
storage_account_name = dbutils.widgets.get("storage_account_name")
source_folder = dbutils.widgets.get("source_folder")

expected_data_file_type = dbutils.widgets.get("expected_data_file_type")
manifest_file = dbutils.widgets.get("manifest_file")

control_file = ""
is_manifest_present = manifest_file != "" and manifest_file is not None

if is_manifest_present == False:
    print(
        "\n WARNING: Manifest file not present. System will not validate for presence of manifest file. \n"
    )

# COMMAND ----------


def insert_raw_delivery_info(
    dataset, delivery_date, delivery_path, file_count, file_size
):
    table_name = "cdh_engineering.cdm_ingest"
    time_now = datetime.now(tz=timezone.utc)
    file_size_mb = file_size / 1000000
    sql = f"DELETE FROM {table_name} where workflow_id= '{workflow_id}' and dataset_name='{data_source}'"

    spark.sql(sql)
    sql = f"INSERT INTO {table_name} (workflow_id, dataset_name, delivery_date,delivery_path,  file_count,file_size_mb, created_time  ) VALUES ('{workflow_id}', '{dataset}', '{delivery_date}', '{delivery_path}',{file_count},{file_size_mb},'{time_now}');"

    print(sql)
    spark.sql(sql)


# COMMAND ----------

source_folder_location = (
    "abfss://"
    + "cdh"
    + "@"
    + storage_account_name
    + ".dfs.core.windows.net/"
    + source_folder
)


def process():
    files = list(cdh_helper.get_file_info_in_directory(path=source_folder_location))
    file_type_count_map = {}

    status = "Succeeded"
    status_message = ""
    zero_byte_file_present = False
    manifest_file_present = False
    file_count = 0
    file_size = 0

    for file in files:
        file_name_with_extension = os.path.basename(file.name)
        file_count = file_count + 1
        file_size = file_size + file.size

        if file_name_with_extension != "":
            file_extension = file_name_with_extension.split(".")[-1]
            if file_extension in file_type_count_map.keys():
                file_type_count_map[file_extension]["count"] = (
                    int(file_type_count_map[file_extension]["count"]) + 1
                )
                file_type_count_map[file_extension]["size"] = (
                    int(file_type_count_map[file_extension]["size"]) + file.size
                )
            else:
                file_type_count_map[file_extension] = {}
                file_type_count_map[file_extension]["count"] = 1
                file_type_count_map[file_extension]["size"] = file.size

            if (
                file_extension.casefold() == expected_data_file_type.casefold()
                and file.size == 0
            ):
                zero_byte_file_present = True

            if file_name_with_extension.casefold() == manifest_file.casefold():
                manifest_file_present = True

    print(f"file_type_count_map : {file_type_count_map}")

    if (
        expected_data_file_type in file_type_count_map
        and file_type_count_map[expected_data_file_type]["count"] > 0
    ):
        print(f"expected file type present.")
    else:
        status_message = f"No files with extension {expected_data_file_type} present"
        status = "Rejected"

    if zero_byte_file_present:
        print(
            f"One or more files with extension {expected_data_file_type} are 0 bytes in size"
        )
        status_message = f"One or more files with extension {expected_data_file_type} are 0 bytes in size"
        status = "Failed"

    if manifest_file_present == False and is_manifest_present == True:
        print(f"Unable to find manifest files {manifest_file} for level 1 checks")
        status_message = (
            f"Unable to find manifest files {manifest_file} for level 1 checks"
        )
        status = "Failed"

    insert_raw_delivery_info(
        dataset=data_source,
        delivery_date=delivery_date,
        delivery_path=source_folder_location,
        file_count=file_count,
        file_size=file_size,
    )

    return (status, status_message)


# COMMAND ----------

from pyspark.sql.functions import *
import os
from datetime import datetime, timezone
from multiprocessing.pool import ThreadPool
import multiprocessing as mp
import cdc_azure.databricks.etl.shared.cdh_helper as cdh_helper

try:
    status, status_message = process()
    cdh_helper.publish_event_status_with_custom_status(
        status=status,
        data_source=data_source,
        workflow_id=workflow_id,
        request_id=request_id,
        outputs=[{"message": status_message}],
    )
except Exception as ex:
    if "java.io.FileNotFoundException" in str(ex):
        status_message = (
            f"{source_folder} does not exist which indicates no files were downloaded"
        )
        publish_event_status_with_custom_status(
            status="Rejected",
            data_source=data_source,
            workflow_id=workflow_id,
            request_id=request_id,
            outputs=[{"message": status_message}],
        )
    else:
        print(ex)
        ex_formatted = cdh_helper.exception_to_string(ex)
        print(ex_formatted)
        cdh_helper.publish_event_status(
            status_success=False,
            data_source=data_source,
            workflow_id=workflow_id,
            request_id=request_id,
            outputs=[{"error": str(ex)}],
        )
