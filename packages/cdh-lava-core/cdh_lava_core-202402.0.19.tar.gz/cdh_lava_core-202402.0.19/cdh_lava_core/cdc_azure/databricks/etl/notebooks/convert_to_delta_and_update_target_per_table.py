# Databricks notebook source
dbutils.widgets.text("dataset_name", "")
dbutils.widgets.text("database_name", "")
dbutils.widgets.text("table_name", "")
dbutils.widgets.text("delivery_type", "")
dbutils.widgets.text("delivery_path", "")
dbutils.widgets.text("data_delivery_date", "")
dbutils.widgets.text("business_partitions", "")
dbutils.widgets.text("created_date", "")
dbutils.widgets.text("file_size", "")
dbutils.widgets.text("file_count", "")
dbutils.widgets.text("workflow_id", "")
dbutils.widgets.text("request_id", "")
dbutils.widgets.text("delivery_control_id", "")
dbutils.widgets.text("deleted_file_retention", "")
dbutils.widgets.text("log_retention", "")
dbutils.widgets.text("source_file_format", "")
dbutils.widgets.text("drift_manage_type", "")


# COMMAND ----------

data_source = dbutils.widgets.get("dataset_name")
workflow_id = dbutils.widgets.get("workflow_id")
request_id = dbutils.widgets.get("request_id")
delivery_date = dbutils.widgets.get("data_delivery_date")
delivery_type = dbutils.widgets.get("delivery_type")
database_name = dbutils.widgets.get("database_name")
table_name = dbutils.widgets.get("table_name")
path = dbutils.widgets.get("delivery_path")
partitions = dbutils.widgets.get("business_partitions")
created_date = dbutils.widgets.get("created_date")
file_size = dbutils.widgets.get("file_size")
file_count = dbutils.widgets.get("file_count")
delivery_control_id = dbutils.widgets.get("delivery_control_id")
deleted_file_retention = dbutils.widgets.get("deleted_file_retention")
log_retention = dbutils.widgets.get("log_retention")
source_file_format = dbutils.widgets.get("source_file_format")
drift_manage_type = dbutils.widgets.get("drift_manage_type")

# COMMAND ----------

# context = dbutils.notebook.entry_point.getDbutils().notebook().getContext().currentRunId
# print(context)

# COMMAND ----------

print("database:", database_name)
print("table_name:", table_name)

# Logs Table
logs_json = {}
process_logs_table = "cdh_engineering.cdm_process_logs"
logs_json["dataset_name"] = data_source
logs_json["database_name"] = database_name
logs_json["table_name"] = table_name
logs_json["delivery_control_id"] = delivery_control_id
logs_json["workflow_id"] = workflow_id
logs_json["request_id"] = request_id
# Logs Table

busines_partitions = partitions
write_mode = "append"
schema_option = "mergeSchema"
if delivery_type == "full":
    write_mode = "overwrite"
    schema_option = "overwriteSchema"
cdh_data_mgmt_db = "cdh_engineering"
schema_control = cdh_data_mgmt_db + "." + "cdm_schema_control"
partition_control = cdh_data_mgmt_db + "." + "cdm_partition_control"
delivery_control = cdh_data_mgmt_db + "." + "cdm_delivery_control"

partition_column = "data_delivery_date"

# COMMAND ----------

# MAGIC %sql
# MAGIC SET delta.retentionDurationCheck.enabled = false;
# MAGIC SET delta.autoOptimize.autoCompact = true;
# MAGIC SET delta.autoOptimize.optimizeWrite = true;

# COMMAND ----------

import os
from pyspark.sql.functions import *


def get_database_table_location(database_name: str, table_name: str):
    db = spark.sql(f"DESCRIBE SCHEMA {database_name}")
    # location = db.collect()[2]['database_description_value']
    location = db.filter(col("database_description_item") == "Location").collect()[0][1]
    table_location = os.path.join(location, table_name)
    print("Table_location", table_location)
    return table_location


# COMMAND ----------

import time
from random import randint
from datetime import datetime
from pyspark.sql.functions import *
from pyspark.sql import types
import json
import cdc_azure.databricks.etl.shared.cdh_helper as cdh_helper
import cdc_azure.databricks.etl.shared.data_load_helper as data_load_helper

job_url = ""
success = True
error = ""
try:
    if "_history" in database_name:
        print("Starting History DB Load..")
        start_time = datetime.now()
        partition_cols = []
        partition_cols.append(partition_column)
        for partition in partitions.split(","):
            if len(partition) > 0:
                partition_cols.append(partition)
        print("Partition_Columns:", partition_cols)
        print("Source path:" + path)
        today_date = datetime.now()
        # print(today_date)
        array = path.split("/")
        # print(array)
        # tableName=array[len(array) - 1]
        tableName = table_name
        print("Database_Name:", database_name)
        print("Table_Name:", tableName)
        location = get_database_table_location(database_name, tableName)
        partition_value = delivery_date  # dbutils.widgets.get("data_delivery_date")#array[len(array) - 2].split("_")
        dF = (
            spark.read.format(source_file_format)
            .option("mergeSchema", "true")
            .load(path)
            .withColumn(partition_column, lit(partition_value))
        )
        schema_drift_change = ""
        schema_update_type = "mergeSchema"
        cast_logic = ""
        if data_load_helper.isTableExists(database_name + "." + tableName):
            targetDF = spark.sql("DESCRIBE " + database_name + "." + tableName + "")
        # For History converting the dataType
        tuple_data = data_load_helper.upCast(dF)
        dF = tuple_data[0]
        if len(tuple_data[1]) > 0:
            schema_drift_change = str(tuple_data[1])
            tuple_data = data_load_helper.dataTypedriftRewrite(
                dF,
                targetDF,
                (database_name + "." + tableName),
                partition_column,
                drift_manage_type,
                partition_value,
            )
            schema_update_type = str(tuple_data[2])
            cast_logic = str(tuple_data[3])
            dF = tuple_data[0]
            if len(tuple_data[1]) > 0:
                schema_drift_change = str(tuple_data[1])
        data_colums = []
        for cols in dF.columns:
            if cols not in partition_cols:
                data_colums.append(cols)
        dF = dF.select([col(x) for x in (data_colums + partition_cols)])
        # display(dF)
        schemaString = str(dF.schema.json())
        start_time = datetime.now()
        targetDF = spark.sql("DESCRIBE " + database_name + "." + tableName + "")
        process_name = "Schema Control Load"
        schema_controlDF = spark.createDataFrame(
            [
                [
                    data_source,
                    database_name,
                    tableName,
                    delivery_control_id,
                    partition_value,
                    schemaString,
                    str(targetDF.schema.json()),
                    schema_drift_change,
                    schema_update_type,
                    cast_logic,
                    path,
                    today_date,
                ]
            ],
            schema=[
                "dataset_name",
                "database_name",
                "table_name",
                "delivery_control_id",
                "delivery_partition",
                "source_schema",
                "target_schema",
                "schema_drift",
                "schema_update_type",
                "datatype_cast_logic",
                "source_path",
                "created_date",
            ],
        )
        # schema_controlDF.show()
        schema_controlDF.repartition(1).write.format("delta").option(
            "mergeSchema", "true"
        ).mode("append").saveAsTable(schema_control)
        end_time = datetime.now()
        time_taken = end_time - start_time
        print(
            "Time taken to complete " + tableName + " Schema Control Load: ", time_taken
        )
        # Logs Table
        logs_json["process_start_time"] = start_time.strftime("%Y-%m-%d %H:%M:%S")
        logs_json["process_end_time"] = end_time.strftime("%Y-%m-%d %H:%M:%S")
        logs_json["process_status"] = "Success"
        data_load_helper.insert_process_logs(
            process_logs_table, process_name, logs_json
        )
        process_name = "Target table Load"
        # Logs Table
        # If Drift Type is audit then only we exit without insert
        if len(schema_drift_change) > 0 and drift_manage_type == "audit":
            dbutils.notebook.exit(
                json.dumps(
                    {
                        "database_name": database_name,
                        "table_name": table_name,
                        "delivery_control": delivery_control,
                        "success": success,
                        "error": error,
                        "drift_action": "Schema Drift detected in audit mode",
                    }
                )
            )
        try:
            dF.write.partitionBy([x for x in partition_cols]).option(
                "delta.deletedFileRetentionDuration", deleted_file_retention
            ).option("delta.logRetentionDuration", log_retention).format("delta").mode(
                write_mode
            ).option(
                "replaceWhere", "" + partition_column + " ='" + partition_value + "' "
            ).option(
                "mergeSchema", "true"
            ).option(
                "path", location
            ).saveAsTable(
                database_name + "." + tableName
            )
        except Exception as err:
            print("ERROR :-\n")
            raise
        end_time = datetime.now()
        time_taken = end_time - start_time
        print("Time taken to complete " + tableName + " Load: ", time_taken)
        # Logs Table
        logs_json["process_start_time"] = start_time.strftime("%Y-%m-%d %H:%M:%S")
        logs_json["process_end_time"] = end_time.strftime("%Y-%m-%d %H:%M:%S")
        logs_json["process_status"] = "Success"
        data_load_helper.insert_process_logs(
            process_logs_table, process_name, logs_json
        )
        process_name = "Partition Control Load"
        # Logs Table
        start_time = datetime.now()
        source_count = dF.count()
        target_count = spark.sql(
            "DESCRIBE HISTORY " + database_name + "." + tableName
        ).orderBy(col("version").desc())
        version_id = int(target_count.collect()[0]["version"])
        target_count = int(
            target_count.collect()[0]["operationMetrics"]["numOutputRows"]
        )
        target_count = 0 if target_count == None else target_count

        parition_controlDF = (
            spark.createDataFrame(
                [
                    [
                        data_source,
                        database_name,
                        tableName,
                        delivery_control_id,
                        partition_value,
                        version_id,
                        source_count,
                        target_count,
                        today_date,
                    ]
                ],
                schema=[
                    "dataset_name",
                    "database_name",
                    "table_name",
                    "delivery_control_id",
                    "delivery_partition",
                    "version",
                    "source_count",
                    "target_count",
                    "created_date",
                ],
            )
            .withColumn("archive_date", lit(None))
            .withColumn("rehydrated_date", lit(None))
        )
        parition_controlDF.repartition(1).write.format("delta").option(
            "mergeSchema", "true"
        ).mode("append").saveAsTable(partition_control)
        end_time = datetime.now()
        time_taken = end_time - start_time
        print(
            "Time taken to complete " + tableName + " Partition Control Load: ",
            time_taken,
        )
        # Logs Table
        logs_json["process_start_time"] = start_time.strftime("%Y-%m-%d %H:%M:%S")
        logs_json["process_end_time"] = end_time.strftime("%Y-%m-%d %H:%M:%S")
        logs_json["process_status"] = "Success"
        data_load_helper.insert_process_logs(
            process_logs_table, process_name, logs_json
        )
        # Logs Table
        start_time = datetime.now()
        if data_load_helper.isTableExists(delivery_control):
            end_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            delivery_control_df = spark.createDataFrame(
                [
                    [
                        data_source,
                        database_name,
                        table_name,
                        delivery_control_id,
                        delivery_type,
                        path,
                        delivery_date,
                        busines_partitions,
                        today_date,
                        int(file_count),
                        int(file_size),
                        source_count,
                        target_count,
                        today_date,
                        end_date,
                    ]
                ],
                schema=[
                    "dataset_name",
                    "database_name",
                    "table_name",
                    "delivery_control_id",
                    "delivery_type",
                    "delivery_path",
                    "data_delivery_date",
                    "business_partitions",
                    "created_date",
                    "file_count",
                    "file_size",
                    "source_count",
                    "target_count",
                    "cdh_process_start_date",
                    "cdh_process_end_date",
                ],
            )
            end_time = datetime.now()
            time_taken = end_time - start_time
            print(
                "Time taken to update " + tableName + " Delivery Control Table: ",
                time_taken,
            )
    else:
        print("Starting Current DB Load..")
        start_time = datetime.now()
        if len(partitions) > 0:
            partitions = partitions.split(",")
        partition_cols = []
        for partition in partitions:
            partition_cols.append(partition)
        today_date = datetime.now()
        array = path.split("/")
        tableName = table_name
        location = get_database_table_location(database_name, tableName)
        process_name = "Taget Table Load"
        print("Source_Path:", path)
        print("Database_Name:", database_name)
        print("Table_Name:", tableName)
        print("Partition Columns:", partition_cols)
        print("source_file_format:", source_file_format)
        print("path:", path)

        dF = (
            spark.read.format(source_file_format)
            .option("mergeSchema", "true")
            .load(path)
        )
        # display(dF)
        try:
            if len(partition_cols) > 0:
                dF.write.partitionBy([x for x in partition_cols]).format("delta").mode(
                    write_mode
                ).option(schema_option, "true").option("path", location).saveAsTable(
                    database_name + "." + tableName
                )
            else:
                dF.write.format("delta").mode(write_mode).option(
                    schema_option, "true"
                ).option("path", location).saveAsTable(database_name + "." + tableName)
        except Exception as err:
            print("ERROR :-\n")
            print(err)
            raise
        end_time = datetime.now()
        time_taken = end_time - start_time
        print("Time taken to load " + tableName + ":" + str(time_taken))
        # Logs Table
        logs_json["process_start_time"] = start_time.strftime("%Y-%m-%d %H:%M:%S")
        logs_json["process_end_time"] = end_time.strftime("%Y-%m-%d %H:%M:%S")
        logs_json["process_status"] = "Success"
        data_load_helper.insert_process_logs(
            process_logs_table, process_name, logs_json
        )
        process_name = "Schema Control Load"
        # Logs Table
        start_time = datetime.now()
        schemaString = str(dF.schema.json())
        targetDF = spark.sql("DESCRIBE " + database_name + "." + tableName + "")
        schema_controlDF = spark.createDataFrame(
            [
                [
                    data_source,
                    database_name,
                    tableName,
                    delivery_control_id,
                    delivery_date,
                    schemaString,
                    str(targetDF.schema.json()),
                    "",
                    schema_option,
                    "",
                    path,
                    today_date,
                ]
            ],
            schema=[
                "dataset_name",
                "database_name",
                "table_name",
                "delivery_control_id",
                "delivery_partition",
                "source_schema",
                "target_schema",
                "schema_drift",
                "schema_update_type",
                "datatype_cast_logic",
                "source_path",
                "created_date",
            ],
        )
        schema_controlDF.write.format("delta").option("mergeSchema", "true").mode(
            "append"
        ).saveAsTable(schema_control)
        end_time = datetime.now()
        time_taken = end_time - start_time
        print(
            "Time taken to insert into Schema Control Table for "
            + tableName
            + ":"
            + str(time_taken)
        )
        # Logs Table
        logs_json["process_start_time"] = start_time.strftime("%Y-%m-%d %H:%M:%S")
        logs_json["process_end_time"] = end_time.strftime("%Y-%m-%d %H:%M:%S")
        logs_json["process_status"] = "Success"
        print("logs_json:", logs_json)
        data_load_helper.insert_process_logs(
            process_logs_table, process_name, logs_json
        )
        process_name = "Partition Control Load"
        print("process_name:", process_name)
        # Logs Table
        start_time = datetime.now()
        source_count = dF.count()
        print("source_count:", source_count)
        target_count = spark.sql(
            "DESCRIBE HISTORY " + database_name + "." + tableName
        ).orderBy(col("version").desc())
        version_id = int(target_count.collect()[0]["version"])
        print("version_id:", version_id)
        target_count = int(
            target_count.collect()[0]["operationMetrics"]["numOutputRows"]
        )
        target_count = 0 if target_count == None else target_count
        print("target_count:", target_count)
        print("data_source:", data_source)
        print("tableName:", tableName)
        print("delivery_control_id:", delivery_control_id)
        print("delivery_date:", delivery_date)
        print("delivery_date:", delivery_date)
        print("version_id:", version_id)
        print("source_count:", source_count)
        print("today_date:", today_date)
        parition_controlDF = (
            spark.createDataFrame(
                [
                    [
                        data_source,
                        database_name,
                        tableName,
                        delivery_control_id,
                        delivery_date,
                        version_id,
                        source_count,
                        target_count,
                        today_date,
                    ]
                ],
                schema=[
                    "dataset_name",
                    "database_name",
                    "table_name",
                    "delivery_control_id",
                    "delivery_partition",
                    "version",
                    "source_count",
                    "target_count",
                    "created_date",
                ],
            )
            .withColumn("archive_date", lit(None))
            .withColumn("rehydrated_date", lit(None))
        )
        parition_controlDF.repartition(1).write.format("delta").option(
            "mergeSchema", "true"
        ).mode("append").saveAsTable(partition_control)

        # Logs Table
        end_time = datetime.now()
        time_taken = end_time - start_time
        print(
            "Time taken to insert into Parition Control Table for "
            + tableName
            + ":"
            + str(time_taken)
        )
        logs_json["process_start_time"] = start_time.strftime("%Y-%m-%d %H:%M:%S")
        logs_json["process_end_time"] = end_time.strftime("%Y-%m-%d %H:%M:%S")
        logs_json["process_status"] = "Success"
        data_load_helper.insert_process_logs(
            process_logs_table, process_name, logs_json
        )
        # Logs Table
        if data_load_helper.isTableExists(delivery_control):
            end_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            delivery_control_df = spark.createDataFrame(
                [
                    [
                        data_source,
                        database_name,
                        table_name,
                        delivery_control_id,
                        delivery_type,
                        path,
                        delivery_date,
                        busines_partitions,
                        created_date,
                        int(file_count),
                        int(file_size),
                        source_count,
                        target_count,
                        today_date,
                        end_date,
                    ]
                ],
                schema=[
                    "dataset_name",
                    "database_name",
                    "table_name",
                    "delivery_control_id",
                    "delivery_type",
                    "delivery_path",
                    "data_delivery_date",
                    "business_partitions",
                    "created_date",
                    "file_count",
                    "file_size",
                    "source_count",
                    "target_count",
                    "cdh_process_start_date",
                    "cdh_process_end_date",
                ],
            )
            end_time = datetime.now()
            time_taken = end_time - start_time
            print(
                "Time taken to update Delivery Control Table for "
                + tableName
                + ":"
                + str(time_taken)
            )
except Exception as ex:
    print(ex)
    success = False
    error = str(ex)
    end_time = datetime.now()
    logs_json["process_start_time"] = start_time.strftime("%Y-%m-%d %H:%M:%S")
    logs_json["process_end_time"] = end_time.strftime("%Y-%m-%d %H:%M:%S")
    logs_json["process_status"] = "Failed"
    logs_json["error_desc"] = error
    data_load_helper.insert_process_logs(process_logs_table, process_name, logs_json)


# COMMAND ----------

if "delivery_control_df" in locals():
    delivery_control = delivery_control_df.toJSON().collect()[0]
else:
    delivery_control = {}

dbutils.notebook.exit(
    json.dumps(
        {
            "database_name": database_name,
            "table_name": table_name,
            "delivery_control": delivery_control,
            "success": success,
            "error": error,
        }
    )
)
