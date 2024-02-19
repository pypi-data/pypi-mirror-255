""" Module for spark and os environment for cdc_tech_environment_service with minimal dependencies. """

import sys  # don't remove required for error handling
import os

import io

# library management
from importlib import util  # library management

# error handling
from subprocess import check_output, Popen, PIPE, CalledProcessError
import subprocess

# http
from urllib.parse import urlparse
import requests

# azcopy and adls
from azure.identity import (
    DefaultAzureCredential,
    ManagedIdentityCredential,
    ClientSecretCredential,
)
from azure.storage.filedatalake import (
    DataLakeServiceClient,
    DataLakeDirectoryClient,
)
from azure.keyvault.secrets import SecretClient

# spark
from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.functions import (
    coalesce,
    col,
    concat_ws,
    lit,
    udf,
    regexp_replace,
)
from pyspark.sql.types import (
    IntegerType,
    LongType,
    StringType,
    StructField,
    StructType,
)

#  data
os.environ["PYARROW_IGNORE_TIMEZONE"] = "1"
pyspark_pandas_loader = util.find_spec("pyspark.pandas")
pyspark_pandas_found = pyspark_pandas_loader is not None

if pyspark_pandas_found:
    # import pyspark.pandas  as pd
    # bug - pyspark version will not read local files in the repo
    import pyspark.pandas as pd
else:
    import pandas as pd


# Get the currently running file name
NAMESPACE_NAME = os.path.basename(os.path.dirname(__file__))
# Get the parent folder name of the running file
SERVICE_NAME = os.path.basename(__file__)


class EnvironmentSpark:
    """EnvironmentSpark class with minimal dependencies for the developer service.
    - This class is used to configure the Spark environment.
    """

    @staticmethod
    def configure_spark_local(
        spark_home_path: str = "",
        pyspark_python_path: str = "",
        java_home_path: str = "",
    ) -> str:
        """Configures spark locally

        Args:
            spark_home_path (str, optional): path for spark home. Defaults to "".
            pyspark_python_path (str, optional): path for pyspark python. Defaults to "".
            java_home_path (str, optional): path for java home. Defaults to "".

        Returns:
            str: spark_home_path
        """
        os.environ["PYARROW_IGNORE_TIMEZONE"] = "1"
        os.environ["SPARK_HOME"] = spark_home_path
        os.environ["JAVA_HOME"] = java_home_path

        # Add the PySpark directories to the Python path:
        sys.path.insert(1, os.path.join(java_home_path, "/bin"))
        sys.path.insert(1, os.path.join(spark_home_path, "python"))
        sys.path.insert(1, os.path.join(spark_home_path, "python", "pyspark"))
        sys.path.insert(1, os.path.join(spark_home_path, "python", "build"))

        # If PySpark isn't specified, use currently running Python binary:
        pyspark_python_path = pyspark_python_path or sys.executable
        os.environ["PYSPARK_PYTHON"] = pyspark_python_path

        # Find Spark Locally
        # location = findspark.find()
        # findspark.init(location, edit_rc=True)
        # Start a SparkContext

        return spark_home_path

    @staticmethod
    def configure_spark_path_server(spark: SparkSession) -> str:
        """Configures spark path on server

        Args:
            spark (SparkSession): Spark Session

        Returns:
            str: root_path
        """

        spark_home_path_current = os.environ.get("SPARK_HOME", None)
        print("spark_home_path_current:{spark_home_path_current}")
        print(spark_home_path_current)
        spark.conf.set("spark.databricks.userInfoFunctions.enabled", "True")
        spark.conf.set("spark.databricks.io.cache.enabled", "True")

        df_user_name = spark.sql("select current_user()")
        row_user_name = df_user_name.first()
        if row_user_name is not None:
            username = row_user_name["current_user"]
        else:
            username = "dataframe is empty error"
        repo = "cdh"
        sys_path = str(sys.path)
        root_path = os.path.abspath(
            f"/Workspace/Repos/{username}/{repo}/cdh_lava_core"
        )
        if root_path not in sys_path:
            sys.path.append(root_path)

        return root_path

    @staticmethod
    def get_spark_home_path_local(spark_home_path: str) -> str:
        """Retrieve spark home path when running locally

        Args:
            spark_home_path (str): default spark home path

        Returns:
            str: spark home path
        """

        if not spark_home_path:
            for path in [
                "/usr/local/opt/apache-spark/libexec",  # OS X Homebrew
                "/usr/lib/spark/"  # AWS Amazon EMR
                # Any other common places to look?
            ]:
                if os.path.exists(path):
                    spark_home_path = path
                    break

        if not spark_home_path:
            spark_home_path = "SPARK_HOME_NOT_FOUND"

        return spark_home_path
