# Databricks notebook source
# MAGIC %sql
# MAGIC DROP TABLE IF EXISTS cdh_engineering.cdm_delivery_control;
# MAGIC CREATE TABLE IF NOT EXISTS cdh_engineering.cdm_delivery_control (
# MAGIC   delivery_control_id STRING NOT NULL,
# MAGIC   dataset_name STRING NOT NULL,
# MAGIC   database_name STRING NOT NULL,
# MAGIC   table_name STRING NOT NULL,
# MAGIC   delivery_type STRING NOT NULL,
# MAGIC   delivery_path STRING NOT NULL,
# MAGIC   data_delivery_date STRING,
# MAGIC   business_partitions STRING,
# MAGIC   created_date TIMESTAMP,
# MAGIC   file_count BIGINT,
# MAGIC   file_size BIGINT,
# MAGIC   source_count BIGINT,
# MAGIC   target_count BIGINT,
# MAGIC   cdh_process_start_date TIMESTAMP,
# MAGIC   cdh_process_end_date TIMESTAMP
# MAGIC   )
# MAGIC USING delta;

# COMMAND ----------

# MAGIC %sql
# MAGIC DROP TABLE IF EXISTS cdh_engineering.cdm_schema_control;
# MAGIC CREATE TABLE IF NOT EXISTS cdh_engineering.cdm_schema_control (
# MAGIC   dataset_name STRING NOT NULL,
# MAGIC   database_name STRING NOT NULL,
# MAGIC   table_name STRING NOT NULL,
# MAGIC   delivery_control_id STRING NOT NULL,
# MAGIC   delivery_partition STRING,
# MAGIC   source_schema STRING,
# MAGIC   target_schema STRING,
# MAGIC   schema_drift STRING,
# MAGIC   schema_update_type STRING,
# MAGIC   datatype_cast_logic STRING,
# MAGIC   source_path STRING,
# MAGIC   created_date TIMESTAMP)
# MAGIC USING delta;

# COMMAND ----------

# MAGIC %sql
# MAGIC DROP TABLE IF EXISTS cdh_engineering.cdm_partition_control;
# MAGIC CREATE TABLE IF NOT EXISTS cdh_engineering.cdm_partition_control (
# MAGIC   dataset_name STRING NOT NULL,
# MAGIC   database_name STRING NOT NULL,
# MAGIC   table_name STRING NOT NULL,
# MAGIC   delivery_control_id STRING NOT NULL,
# MAGIC   delivery_partition STRING,
# MAGIC   version BIGINT,
# MAGIC   source_count BIGINT,
# MAGIC   target_count BIGINT,
# MAGIC   archive_date TIMESTAMP,
# MAGIC   rehydrated_date TIMESTAMP,
# MAGIC   created_date TIMESTAMP)
# MAGIC USING delta;

# COMMAND ----------

# MAGIC %sql
# MAGIC DROP TABLE IF EXISTScdh_engineering.cdm_raw_delivery_info;
# MAGIC CREATE TABLE IF NOT EXISTS cdh_engineering.cdm_raw_delivery_info(dataset_name string, data_delivery_date string,workflow_id string,  delivery_path string,file_count bigint,file_size bigint, source_schema string,created_date timestamp );

# COMMAND ----------

# MAGIC %sql
# MAGIC DROP TABLE IF EXISTS cdh_engineering.cdm_raw_delivery_metrics_table_level;
# MAGIC CREATE TABLE IF NOT EXISTS cdh_engineering.cdm_raw_delivery_metrics_table_level(dataset_name string, data_delivery_date string,workflow_id string,  table_name string,row_count bigint, created_date timestamp );

# COMMAND ----------

# MAGIC %sql
# MAGIC DROP TABLE IF EXISTS cdh_engineering.etl_workflow_header;
# MAGIC CREATE TABLE IF NOT EXISTS cdh_engineering.etl_workflow_header(dataset_name string, data_delivery_date string,workflow_id string,  tracking_status string,tracking_start_utc timestamp, tracking_end_utc timestamp,last_updated_date_utc timestamp,triggerred_by string, target_database string );
# MAGIC --CREATE TABLE cdh_engineering.etl_workflow_header(dataset_name string, data_delivery_date string,workflow_id string,  tracking_status string );

# COMMAND ----------

# MAGIC %sql
# MAGIC DROP TABLE if exists cdh_engineering.etl_workflow_service;
# MAGIC CREATE TABLE IF NOT EXISTS cdh_engineering.etl_workflow_service(dataset_name string, data_delivery_date string,workflow_id string,display_name string, target_system string, target_resource_name string,  tracking_status string,tracking_start_utc timestamp, tracking_end_utc timestamp,tracking_request_id string, tracking_response_id string, last_updated_date_utc timestamp );

# COMMAND ----------

# MAGIC %sql
# MAGIC DROP TABLE if exists cdh_engineering.etl_workflow_service_scheduled;
# MAGIC CREATE TABLE IF NOT EXISTS cdh_engineering.etl_workflow_service_scheduled
# MAGIC (dataset_name string, data_delivery_date string,workflow_id string,request_id string, display_name string, target_system string, target_resource_name string,prevent_run_window_start_time_et timestamp,prevent_run_window_end_time_et timestamp,processed_id string, last_updated_date_utc timestamp);

# COMMAND ----------

# MAGIC %sql
# MAGIC DROP TABLE IF EXISTS cdh_engineering.cdm_process_logs;
# MAGIC CREATE TABLE spark_catalog.cdh_engineering.cdm_process_logs 
# MAGIC (
# MAGIC dataset_name STRING NOT NULL,
# MAGIC database_name STRING NOT NULL,
# MAGIC table_name STRING NOT NULL,
# MAGIC delivery_control_id STRING NOT NULL,
# MAGIC workflow_id STRING,
# MAGIC request_id STRING,
# MAGIC process_name STRING,
# MAGIC process_start_time TIMESTAMP,
# MAGIC process_end_time TIMESTAMP,
# MAGIC process_status STRING,
# MAGIC error_desc STRING
# MAGIC )
# MAGIC USING delta;

# COMMAND ----------

# MAGIC %sql
# MAGIC ALTER TABLE cdh_engineering.etl_workflow_header ADD columns (triggerred_by string, target_database string);

# COMMAND ----------

# MAGIC %sql
# MAGIC select * from cdh_engineering.etl_workflow_header
