# Databricks notebook
import os
import traceback
import json
import base64
import requests
import uuid
from datetime import datetime, timezone

from cdc_azure.databricks.etl.shared import constants

from pyspark.dbutils import DBUtils
from pyspark.sql import SparkSession
from delta.tables import *

spark = SparkSession.builder.getOrCreate()
dbutils = DBUtils(spark)


def delete_zero_byte_folder(path):
    match = "$folder$"
    dir_files = get_dbutils().fs.ls(path)
    for file in dir_files:
        #     print(file)
        if file.name.find(match) != -1:
            # print("found zerobyte folder file " + file.path )
            dbutils.fs.rm(file.path)
        if file.isDir():
            cdh_delete_zero_byte_folder(file.path)


def secure_connect_spark_adls():
    secret_scope = constants.get_secret_scope()
    # Application (Client) ID
    applicationId = dbutils.secrets.get(scope=secret_scope, key="cdh-adb-client-id")
    # Application (Client) Secret Key
    authenticationKey = dbutils.secrets.get(
        scope=secret_scope, key="cdh-adb-client-secret"
    )
    # Directory (Tenant) ID
    tenantId = dbutils.secrets.get(scope=secret_scope, key="cdh-adb-tenant-id")

    endpoint = "https://login.microsoftonline.com/" + tenantId + "/oauth2/token"

    # Connecting using Service Principal secrets and OAuth
    configs = {
        "fs.azure.account.auth.type": "OAuth",
        "fs.azure.account.oauth.provider.type": "org.apache.hadoop.fs.azurebfs.oauth2.ClientCredsTokenProvider",
        "fs.azure.account.oauth2.client.id": applicationId,
        "fs.azure.account.oauth2.client.secret": authenticationKey,
        "fs.azure.account.oauth2.client.endpoint": endpoint,
    }

    spark.conf.set("fs.azure.account.auth.type", "OAuth")
    spark.conf.set(
        "fs.azure.account.oauth.provider.type",
        "org.apache.hadoop.fs.azurebfs.oauth2.ClientCredsTokenProvider",
    )
    spark.conf.set("fs.azure.account.oauth2.client.id", applicationId)
    spark.conf.set("fs.azure.account.oauth2.client.secret", authenticationKey)
    spark.conf.set("fs.azure.account.oauth2.client.endpoint", endpoint)


def find_nth(haystack, needle, n):
    start = haystack.find(needle)
    while start >= 0 and n > 1:
        start = haystack.find(needle, start + len(needle))
        n -= 1
    return start


def get_table_list(source_folder_location):
    lists = dbutils.fs.ls(source_folder_location)
    tables = []
    for file in lists:
        table = file.path
        loc = find_nth(table, "/", 6)
        loc2 = find_nth(table, "$", 1)
        if loc2 == -1:
            tables.append(table[loc + 1 : -1])
    return tables


def get_all_files_in_directory(ls_path):
    dir_paths = dbutils.fs.ls(ls_path)
    subdir_paths = [
        get_all_files_in_directory(p.path)
        for p in dir_paths
        if p.isDir() and p.path != ls_path
    ]
    flat_subdir_paths = [p for subdir in subdir_paths for p in subdir]
    return list(map(lambda p: p.path, dir_paths)) + flat_subdir_paths


def get_specific_files_in_directory(ls_path, file_name, exact_match=True):
    paths = get_all_files_in_directory(ls_path)
    result = []
    for path in paths:
        path_file_name = os.path.basename(path)
        # print(file_name)
        if exact_match:
            if file_name.casefold() == path_file_name.casefold():
                result.append(path)
        else:
            if file_name.casefold() in path_file_name.casefold():
                result.append(path)

    return result


def get_file_info_in_directory(path: str):
    for x in dbutils.fs.ls(path):
        if x.path[-1] != "/":
            yield x
        else:
            for y in get_file_info_in_directory(path=x.path):
                yield y


def get_first_file_in_directory(ls_path: str, file_type: str):
    paths = get_all_files_in_directory(ls_path)
    for path in paths:
        file_name = os.path.basename(path)
        # print(file_name)
        if file_name != "":
            file_name_and_path = os.path.splitext(file_name)
            file_extension = file_name_and_path[1]
            if file_extension == file_type:
                return path


def get_first_level_subfolders(SourceFolderLocation):
    lists = dbutils.fs.ls(SourceFolderLocation)
    tables = []
    for list in lists:
        if list.isDir():
            tables.append(list.name[:-1])
    return tables


def exception_to_string(ex):
    stack = traceback.extract_stack()[:-3] + traceback.extract_tb(
        ex.__traceback__
    )  # add limit=??
    pretty = traceback.format_list(stack)
    return "".join(pretty) + "\n  {} {}".format(ex.__class__, ex)


def publish_event_status(
    status_success: bool,
    data_source: str,
    workflow_id: str,
    request_id: str,
    outputs=[],
):
    if status_success:
        status = "Succeeded"
    else:
        status = "Failed"

    publish_event_status_with_custom_status(
        status=status,
        data_source=data_source,
        workflow_id=workflow_id,
        request_id=request_id,
        outputs=outputs,
    )


def publish_event_status_with_custom_status(
    status: str, data_source: str, workflow_id: str, request_id: str, outputs=[]
):
    datetime_now_utc = datetime.now(tz=timezone.utc)
    now = datetime_now_utc.strftime("%Y-%m-%dT%H:%M:%SZ")

    if status.casefold() not in ["succeeded", "failed", "rejected"]:
        print(f"Invalid status: {status}")

    job_payload = {
        "data_source": "{data_source}",
        "workflow_id": "{workflow_id}",
        "request_id": "{request_id}",
        "event_source": "adb",
        "event_time_utc": "{event_time_utc}",
        "outputs": outputs,
        "status": "{status}",
    }

    job_payload = (
        json.dumps(job_payload)
        .replace("{request_id}", request_id)
        .replace("{workflow_id}", workflow_id)
        .replace("{data_source}", data_source)
        .replace("{status}", status)
        .replace("{event_time_utc}", now)
    )

    print(f"\n job_payload back to orchestrator: {job_payload}")
    if (
        workflow_id is None
        or workflow_id == ""
        or workflow_id.casefold() == "simulated".casefold()
        or workflow_id.casefold() == "demo".casefold()
        or workflow_id.casefold() == "isolated".casefold()
    ):
        print(f"\n Running in ISOLATED mode. No messages are sent to queue")
        return

    # get sas token
    secret_scope = constants.get_secret_scope()
    url = dbutils.secrets.get(scope=secret_scope, key="cdh-event-publish-func-url")

    response = requests.post(url, data=job_payload)
    if not response.ok:
        print(response.text)
        raise Exception(
            f"Error publishing message to queue at {url} with payload {job_payload} \n Status_Code: {response.status_code}. Text: {response.text}"
        )


def fetchTables(database):
    tables = []
    print("Fetching tables for database:", database)
    v = spark.sql("SHOW TABLES in " + database + "")
    for row in v.collect():
        tables.append(row["tableName"])

    return tables


def get_json_file_from_datalake(
    storage_account_name: str, file_system: str, file_name: str
):
    from azure.identity import ClientSecretCredential
    from azure.storage.filedatalake import DataLakeServiceClient
    import tempfile
    import json

    account_url = f"https://{storage_account_name}.dfs.core.windows.net/cdh"
    secret_scope = constants.get_secret_scope()
    applicationId = dbutils.secrets.get(scope=secret_scope, key="cdh-adb-client-id")
    # Application (Client) Secret Key
    authenticationKey = dbutils.secrets.get(
        scope=secret_scope, key="cdh-adb-client-secret"
    )
    # Directory (Tenant) ID
    tenantId = dbutils.secrets.get(scope=secret_scope, key="cdh-adb-tenant-id")

    credential = ClientSecretCredential(
        client_id=applicationId, client_secret=authenticationKey, tenant_id=tenantId
    )

    service_client = DataLakeServiceClient(
        account_url=account_url, credential=credential
    )

    directory_client = service_client.get_file_system_client(file_system=file_system)
    file_client = directory_client.get_file_client(file_name)
    download = file_client.download_file()
    downloaded_bytes = download.readall()
    temp_file_path = tempfile.gettempdir()
    file_local_path = f"{temp_file_path}/{file_name}"
    with open(file_local_path, "wb") as my_file:
        my_file.write(downloaded_bytes)
        my_file.close()

    file_object = open(file_local_path, "r")
    file_text = file_object.read()
    config_json = json.loads(file_text)
    return config_json


def get_notification_service_url():
    scope = constants.get_secret_scope()
    notifier_url = dbutils.secrets.get(
        scope=scope, key="cdh-email-notification-logicapp-url"
    )
    return notifier_url


def get_app_environment():
    return constants.CDH_ENVIRONMENT
