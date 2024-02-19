# Databricks notebook source
# mandatory parameters and names. The orchestrator will always pass these
dbutils.widgets.text("data_source", "")
dbutils.widgets.text("delivery_date", "")
dbutils.widgets.text("request_id", "")
dbutils.widgets.text("workflow_id", "ISOLATED")
dbutils.widgets.text("storage_account_name", "")
# optional parameters. Add as many as needed for execution of notebook.
dbutils.widgets.text("database_name", "")
dbutils.widgets.text("source_location", "")
dbutils.widgets.dropdown(
    name="delivery_type", defaultValue="full", choices=["full", "incremental"]
)
dbutils.widgets.text("adlsContainerName", "cdh")
dbutils.widgets.dropdown(name="reload_flag", defaultValue="Y", choices=["Y", "N"])
dbutils.widgets.dropdown(
    name="pipeline_run_type",
    defaultValue="current",
    choices=["current", "history", "both"],
)
dbutils.widgets.text("source_file_format", "parquet")
dbutils.widgets.dropdown(
    name="drift_manage_type", defaultValue="audit", choices=["audit", "apply"]
)

# COMMAND ----------

data_source = dbutils.widgets.get("data_source")
delivery_date = dbutils.widgets.get("delivery_date")
request_id = dbutils.widgets.get("request_id")
workflow_id = dbutils.widgets.get("workflow_id")
database_name = dbutils.widgets.get("database_name")
source_location = dbutils.widgets.get("source_location")
delivery_type = dbutils.widgets.get("delivery_type")
adlsAccountName = dbutils.widgets.get("storage_account_name")
adlsContainerName = dbutils.widgets.get("adlsContainerName")
# adlsFolderName = dbutils.widgets.get('adlsFolderName')
reload_flag = dbutils.widgets.get("reload_flag")
pipeline_run_type = dbutils.widgets.get("pipeline_run_type")
source_file_format = dbutils.widgets.get("source_file_format")
drift_manage_type = dbutils.widgets.get("drift_manage_type")


# COMMAND ----------

from multiprocessing.pool import ThreadPool
from concurrent.futures import ThreadPoolExecutor
import multiprocessing as mp
from pyspark.sql.functions import *
import cdc_azure.databricks.etl.shared.cdh_helper as cdh_helper
import cdc_azure.databricks.etl.shared.data_load_helper as data_load_helper
import os
import json
import base64
import requests
import datetime

# COMMAND ----------

base_path = (
    "abfss://" + adlsContainerName + "@" + adlsAccountName + ".dfs.core.windows.net"
)
log_retention = "0 day"
deleted_file_retention = "0 day"

# COMMAND ----------


def load_delivery_control_table():
    start_time = datetime.datetime.now()
    # path = base_path + "/" + data_source + "/" + delivery_folder_name
    path = base_path + "/" + source_location
    path = path[0 : len(path) - 1] if path[len(path) - 1] == "/" else path
    partition_column = "cdh_data_date"
    cdh_data_mgmt_db = "cdh_engineering"
    schema_control = cdh_data_mgmt_db + "." + "cdm_schema_control"
    partition_control = cdh_data_mgmt_db + "." + "cdm_partition_control"
    delivery_control = cdh_data_mgmt_db + "." + "cdm_delivery_control"
    print("reload_flag:", reload_flag)
    print("delivery_type:", delivery_type)
    print("pipeline_run_type:", pipeline_run_type)

    paths = []
    paths_files = {}
    paths_size = {}
    # path = base_path + "/" + data_source + "/" + delivery_folder_name
    files = list(cdh_helper.get_file_info_in_directory(path))
    for file in files:
        if file.name.endswith(source_file_format):
            a = file.path.split("/")
            p = path + "/" + a[len(path.split("/"))]
            partition_cols = []
            for partition in a[len(path.split("/")) + 1 : len(a) - 1]:
                partition_cols.append(partition.split("=")[0])
            partitions = ",".join(partition_cols)
            if (p + "|" + partitions) not in paths:
                paths.append(p + "|" + partitions)
            if (p + "|" + partitions) not in paths_files:
                paths_files[(p + "|" + partitions)] = [file.path]
                paths_size[(p + "|" + partitions)] = file.size
            else:
                paths_files[(p + "|" + partitions)].append(file.path)
                paths_size[(p + "|" + partitions)] = (
                    paths_size[(p + "|" + partitions)] + file.size
                )
    if len(paths) > 0:
        data_load_helper.insert_delivery_control(
            data_source,
            database_name,
            reload_flag,
            delivery_date,
            delivery_control,
            delivery_type,
            paths,
            paths_files,
            paths_size,
            pipeline_run_type,
        )
    else:
        print("No valid data to process.")
    end_time = datetime.datetime.now()
    time_taken = end_time - start_time
    print("Time taken to complete Delivery Control Load: ", time_taken)
    # delivery_control_df = spark.sql("SELECT * from " + delivery_control +" where dataset_name = '"+data_source+"'  and data_delivery_date='"+delivery_date+"'")


# COMMAND ----------

process_json = []


def get_tables_to_process():
    cdh_engineering_db = "cdh_engineering"
    delivery_control = cdh_engineering_db + "." + "cdm_delivery_control"
    rows = (
        spark.sql(
            f"SELECT delivery_control_id, dataset_name,database_name,table_name,delivery_type,created_date,file_count,file_size,delivery_path,data_delivery_date,business_partitions, '{workflow_id}' as workflow_id,'{request_id}' as request_id,'{log_retention}' as log_retention,'{deleted_file_retention}' as deleted_file_retention,'{source_file_format}' as source_file_format,'{drift_manage_type}' as drift_manage_type FROM {delivery_control} where dataset_name= '{data_source}' and database_name= '{database_name}' and data_delivery_date='{delivery_date}' and cdh_process_start_date is null and cdh_process_end_date is null "
        )
        .toJSON()
        .collect()
    )
    # print(len(rows))
    for row in rows:
        process_json.append(json.loads(row))


# COMMAND ----------

workflow_outputs = []
delivery_controls = []
delivery_controls_failed = []


def call_workflow(process_json):
    print(process_json)
    print("\n")
    # nb_output = dbutils.notebook.run("convert_to_delta_and_update_target_per_table", 36000, process_json)
    nb_output = json.loads(
        dbutils.notebook.run(
            "convert_to_delta_and_update_target_per_table", 36000, process_json
        )
    )
    if "success" in nb_output:
        delivery_controls.append(nb_output["delivery_control"])
    else:
        delivery_controls_failed.append(nb_output["delivery_control"])
    # table_output = json.loads(nb_output)
    print(nb_output)
    print("Failed:", delivery_controls_failed)

    if "delivery_control" in nb_output:
        nb_output["delivery_control"] = {}

    workflow_outputs.append(nb_output)


def process():
    start_process_time = datetime.datetime.now()
    if len(process_json) > 0:
        print("Number of Process to run:", len(process_json))
        length = mp.cpu_count()
        first_json = process_json[0]
        process_json.remove(first_json)
        result = []
        with ThreadPoolExecutor(max_workers=length) as exe:
            exe.submit(call_workflow, first_json)
            result = exe.map(call_workflow, process_json)
    end_process_time = datetime.datetime.now()
    c = end_process_time - start_process_time
    print("Time Taken to Complete: ", c)


# COMMAND ----------

from delta.tables import *

cdh_data_mgmt_db = "cdh_engineering"
schema_control = cdh_data_mgmt_db + "." + "cdm_schema_control"
partition_control = cdh_data_mgmt_db + "." + "cdm_partition_control"
delivery_control = cdh_data_mgmt_db + "." + "cdm_delivery_control"


try:
    load_delivery_control_table()
    get_tables_to_process()
    process()
    dfUpdates = spark.read.json(spark.sparkContext.parallelize(delivery_controls))
    # display(dfUpdates)
    if len(dfUpdates.columns) > 0:
        deltaTableDelivery = DeltaTable.forName(spark, delivery_control)
        deltaTableDelivery.alias("delivery_control").merge(
            dfUpdates.alias("updates"),
            "delivery_control.delivery_control_id = updates.delivery_control_id and delivery_control.database_name = updates.database_name and delivery_control.dataset_name = updates.dataset_name and   delivery_control.table_name = updates.table_name and delivery_control.delivery_type == updates.delivery_type and delivery_control.data_delivery_date == updates.data_delivery_date",
        ).whenMatchedUpdate(
            set={
                "delivery_control_id": "updates.delivery_control_id",
                "database_name": "updates.database_name",
                "dataset_name": "updates.dataset_name",
                "table_name": "updates.table_name",
                "delivery_type": "updates.delivery_type",
                "data_delivery_date": "updates.data_delivery_date",
                "cdh_process_start_date": "updates.cdh_process_start_date",
                "cdh_process_end_date": "updates.cdh_process_end_date",
                "source_count": "updates.source_count",
                "target_count": "updates.target_count",
            }
        ).execute()

    status_success = True
    for out in workflow_outputs:
        if out["success"] == False:
            status_success = False

    cdh_helper.publish_event_status(
        status_success=status_success,
        data_source=data_source,
        workflow_id=workflow_id,
        request_id=request_id,
        outputs={"workflow_outputs": workflow_outputs},
    )
except Exception as ex:
    print(ex)
    ex_formatted = cdh_helper.exception_to_string(ex)
    print(ex_formatted)
    cdh_helper.publish_event_status(
        status_success=False,
        data_source=data_source,
        workflow_id=workflow_id,
        request_id=request_id,
        outputs=[{"error": str(ex), "workflow_outputs": workflow_outputs}],
    )
