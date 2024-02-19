# Databricks notebook source
# MAGIC %sql
# MAGIC DROP TABLE IF EXISTS cdh_engineering.cdm_ingest;
# MAGIC CREATE TABLE IF NOT EXISTS cdh_engineering.cdm_ingest(workflow_id string, dataset_name string, delivery_date string,delivery_path string,  file_count int,file_size_mb FLOAT, created_time timestamp );

# COMMAND ----------

# MAGIC %sql
# MAGIC DROP TABLE IF EXISTS cdh_engineering.cdm_ingest_metadata;
# MAGIC CREATE TABLE IF NOT EXISTS cdh_engineering.cdm_ingest_metadata(workflow_id string, dataset_name string, table_name string,column_name string,  metric string,metric_value string, created_time timestamp );

# COMMAND ----------

# MAGIC %sql
# MAGIC DROP TABLE IF EXISTS cdh_engineering.cdm_process_version_adjustment;
# MAGIC CREATE TABLE IF NOT EXISTS cdh_engineering.cdm_process_version_adjustment(workflow_id string, dataset_name string,database_name string, table_name string,start_version int,  end_version int,created_time timestamp );

# COMMAND ----------

# MAGIC %sql
# MAGIC DROP TABLE IF EXISTS cdh_engineering.cdm_process_transform;
# MAGIC CREATE TABLE IF NOT EXISTS cdh_engineering.cdm_process_transform(workflow_id string, dataset_name string, table_name string, source_path string,  source_file_count int,source_file_format string, source_file_size_mb FLOAT,target_path string,  target_file_count int,target_file_format string,target_file_size_mb FLOAT, start_time timestamp, end_time timestamp,created_time timestamp );

# COMMAND ----------

# MAGIC %sql
# MAGIC DROP TABLE IF EXISTS cdh_engineering.cdm_process_schema_compare;
# MAGIC CREATE TABLE IF NOT EXISTS cdh_engineering.cdm_process_schema_compare(workflow_id string, dataset_name string, table_name string, source_schema string, target_schema string,  schema_diff string, created_time timestamp );

# COMMAND ----------

# MAGIC %sql
# MAGIC DROP TABLE IF EXISTS cdh_engineering.cdm_process_load;
# MAGIC CREATE TABLE IF NOT EXISTS cdh_engineering.cdm_process_load(workflow_id string, dataset_name string, delivery_date string, table_name string, delivery_type string, delivery_path string,  business_partitions string, file_count int,file_size_mb FLOAT,table_version int,  table_row_count int,start_time timestamp, end_time timestamp,created_time timestamp );
