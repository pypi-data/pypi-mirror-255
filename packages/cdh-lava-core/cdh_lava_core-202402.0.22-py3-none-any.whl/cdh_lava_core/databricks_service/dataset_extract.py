""" Module with a variety of metadata extraction routines for different source formats. """

# core
import cdh_lava_core.cdc_tech_environment_service.environment_file as cdc_env_file
from azure.identity import ClientSecretCredential
from azure.storage.filedatalake import DataLakeServiceClient
from pyspark.sql import SparkSession, DataFrame
import sys  # don't remove required for error handling
import os

from urllib.parse import urlparse
from io import BytesIO

# libraries
from importlib import util

import pyreadstat as prs
import pandas as pd_legacy

os.environ["PYARROW_IGNORE_TIMEZONE"] = "1"
pyspark_pandas_loader = util.find_spec("pyspark.pandas")
pyspark_pandas_found = pyspark_pandas_loader is not None

if pyspark_pandas_found:
    import pyspark.pandas as pd

    # bug - pyspark version will not read local files
    # import pandas as pd
else:
    import pandas as pd

# adls and azure security

# CDH


class DataSetExtract:
    """DataSetExtract class for Spark Datasets handle metadata extraction from different source formats"""

    @classmethod
    def extract_xpt_dataframe_schema(
        cls,
        spark: SparkSession,
        ingress_file_path: str,
        tenant_id: str,
        client_id: str,
        client_secret: str,
        data_prdocut_id: str,
        environment,
    ) -> DataFrame:
        """Extracts metadata from xpt file

        Args:
            spark (SparkSession): SparkSession
            ingress_file_path (str): ADLS2 path to csv or usv file
            tenant_id (str): azure tenant id used to download file
            client_id (str): azure client id used to download file
            client_secret (str): azure secret used to download file

        Returns:
            DataFrame: Spark dataframe
        """

        obj_env_file = cdc_env_file.EnvironmentFile()
        https_path = obj_env_file.convert_abfss_to_https_path(
            ingress_file_path, data_product_id, environment
        )
        credential = ClientSecretCredential(tenant_id, client_id, client_secret)

        # download file
        storage_account_loc = urlparse(https_path).netloc
        account_url = f"https://{storage_account_loc}"
        storage_path = urlparse(https_path).path
        storage_container = storage_path.split("/")[1]
        file_path = storage_path.replace(f"{storage_container}" + "/", "")
        service_client = DataLakeServiceClient(
            account_url=account_url, credential=credential
        )
        file_system_client = service_client.get_file_system_client(storage_container)
        file_client = file_system_client.get_file_client(file_path)
        download = file_client.download_file(0)
        download_bytes = download.readall()
        download_file = BytesIO(download_bytes)

        # step 1: get pandas data frame

        xpt_meta = prs.read_xport(download_file, metadataonly=True)

        # step 2: initalize empty pandas dataframe
        df_metadata = pd.DataFrame()

        # read column name, labels into the new pandas dataframe
        df_metadata["name"] = xpt_meta.column_names = xpt_meta.column_names.str.strip()
        df_metadata["label"] = xpt_meta.column_labels = [
            x.decode("utf-8") for x in xpt_meta.column_labels
        ]
        df_metadata["format"] = xpt_meta.column_formats = [
            x.decode("utf-8") for x in xpt_meta.column_formats
        ]
        df_metadata["type"] = xpt_meta.column_types = [
            x.decode("utf-8") for x in xpt_meta.variable_types
        ]
        df_metadata["type_in_source"] = xpt_meta.column_types = [
            x.decode("utf-8") for x in xpt_meta.original_variable_types
        ]
        df_metadata[
            "length"
        ] = xpt_meta.column_lengths = xpt_meta.column_lengths.astype(int)
        df_metadata["note"] = xpt_meta.column_notes = [
            x.decode("utf-8") for x in xpt_meta.column_notes
        ]
        df_metadata["table_name"] = xpt_meta.table_name = xpt_meta.table_name.decode(
            "utf-8"
        )

        metadata_df = spark.createDataFrame(df_metadata)

        return metadata_df
