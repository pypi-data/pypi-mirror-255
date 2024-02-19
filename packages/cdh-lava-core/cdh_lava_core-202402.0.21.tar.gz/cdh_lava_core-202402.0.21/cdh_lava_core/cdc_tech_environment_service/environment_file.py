""" Module for spark and os environment for cdc_tech_environment_service with
 minimal dependencies. """

# library management
from importlib import util  # library management
import subprocess
import fnmatch

# error handling
from subprocess import check_output, Popen, PIPE, CalledProcessError

import sys  # don't remove required for error handling
import os
import importlib

# files
import glob
import json
import platform

# http
from urllib.parse import urlparse
import requests

# Get the currently running file name
NAMESPACE_NAME = os.path.basename(os.path.dirname(__file__))
# Get the parent folder name of the running file
SERVICE_NAME = os.path.basename(__file__)

from cdh_lava_core.cdc_log_service.environment_logging import LoggerSingleton

from cdh_lava_core.az_storage_service.az_storage_file import AzStorageFile

# spark
from pyspark.sql import SparkSession
from pyspark.sql.types import (
    IntegerType,
    LongType,
    StringType,
    StructField,
    StructType,
)

from cdh_lava_core.cdc_log_service.environment_logging import LoggerSingleton


#  data
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


class EnvironmentFile:
    """EnvironmentFile class with minimal dependencies for the developer
    service.
    - This class is used to perform file and directory operations.
    """

    # Get the currently running file name
    NAMESPACE_NAME = os.path.basename(os.path.dirname(__file__))
    # Get the parent folder name of the running file
    SERVICE_NAME = os.path.basename(__file__)

    @staticmethod
    def class_exists() -> bool:
        """Basic check to make sure object is instantiated

        Returns:
            bool: true/false indicating object exists
        """
        return True

    @staticmethod
    def delete_directory_files(
        directory, data_product_id, environment, file_extension="*", files_to_keep=[]
    ):
        """
        Deletes all files in a given directory with a specified extension, except for the files that match patterns in files_to_keep.

        Parameters
        ----------
        directory : str
            The directory from which files will be deleted.
        file_extension : str, optional
            The extension of the files that will be deleted. By default, all files ('*') will be deleted.
        files_to_keep : list of str, optional
            A list of filename patterns to keep. Files that match these patterns will not be deleted, even if their extension matches file_extension.
            example, files_to_keep=['*.csv', 'important*']

        Returns
        -------
        msg : str
            A message that lists which files have been deleted.
        """

        tracer, logger = LoggerSingleton.instance(
            NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
        ).initialize_logging_and_tracing()

        with tracer.start_as_current_span("delete_directory_files"):
            try:
                files = glob.glob(os.path.join(directory, f"*.{file_extension}"))
                msg = ""
                for file in files:
                    # Check if the file matches any of the patterns in the list of files to keep
                    if any(
                        fnmatch.fnmatch(os.path.basename(file), pattern)
                        for pattern in files_to_keep
                    ):
                        continue  # Skip this file

                    try:
                        os.remove(file)
                        msg = msg + f"{file} has been deleted\n"
                        logger.info(msg)

                    except OSError as e:
                        error_msg = f"Error: {file} : {e}"
                        exc_info = sys.exc_info()
                        LoggerSingleton.instance(
                            NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
                        ).error_with_exception(error_msg, exc_info)
                        raise

                return msg

            except Exception as ex:
                error_msg = "Error: %s", ex
                exc_info = sys.exc_info()
                LoggerSingleton.instance(
                    NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
                ).error_with_exception(error_msg, exc_info)
                raise

    @classmethod
    def convert_to_current_os_dir(
        cls, path: str, data_product_id: str, environment: str
    ) -> str:
        """Converts path to current os path

        Args:
            path (str): path to convert

        Returns:
            str: converted path
        """

        tracer, logger = LoggerSingleton.instance(
            NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
        ).initialize_logging_and_tracing()

        with tracer.start_as_current_span("convert_to_current_os_dir"):
            try:
                logger.info(f"convert_to_current_os_dir: {path}")
                if platform.system() == "Windows":
                    converted_path = cls.convert_to_windows_dir(
                        path, data_product_id, environment
                    )
                else:
                    converted_path = cls.convert_to_unix_dir(
                        path, data_product_id, environment
                    )

                logger.info(f"converted_path: {converted_path}")

                # Fix any double slashes
                converted_path = converted_path.replace("//", "/")

                return converted_path

            except Exception as ex:
                error_msg = "Error: %s", ex
                exc_info = sys.exc_info()
                LoggerSingleton.instance(
                    NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
                ).error_with_exception(error_msg, exc_info)
                raise

    @staticmethod
    def convert_to_windows_dir(
        folder_path: str, data_product_id: str, environment: str
    ) -> str:
        """Converts to a Windows folder path from bash format

        Args:
            folder_path (str): path to convert

        Returns:
            str: _converted path
        """

        tracer, logger = LoggerSingleton.instance(
            NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
        ).initialize_logging_and_tracing()

        with tracer.start_as_current_span("convert_to_windows_dir"):
            logger.info(f"convert_to_windows_dir: {folder_path}")
            window_dir = "\\"
            unix_dir = "/"

            folder_path = folder_path.replace(unix_dir, window_dir)
            # Replace double backslashes with a single backslash
            folder_path = folder_path.replace("\\\\", "\\")

            converted_path = folder_path.rstrip(window_dir) + window_dir
            logger.info(f"converted_path: {converted_path}")
            return converted_path

    @staticmethod
    def convert_to_unix_dir(
        folder_path: str, data_product_id: str, environment: str
    ) -> str:
        """Converts tp a unix folder path to windows format

        Args:
            folder_path (str): path to convert

        Returns:
            str: _converted path
        """

        tracer, logger = LoggerSingleton.instance(
            NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
        ).initialize_logging_and_tracing()

        with tracer.start_as_current_span("convert_to_unix_dir"):
            logger.info(f"convert_to_unix_dir: {folder_path}")

            window_dir = "\\"
            unix_dir = "/"
            drive_letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

            if window_dir in folder_path:
                # Check if a drive letter exists at the start of the string
                if folder_path[0].upper() in drive_letters and folder_path[1] == ":":
                    drive_letter = folder_path[0].lower()
                    # remove the drive letter and the colon
                    folder_path = folder_path[2:]
                    folder_path = (
                        "/" + drive_letter + folder_path
                    )  # prepend the drive letter
                folder_path = folder_path.replace(window_dir, unix_dir)
            converted_path = folder_path.rstrip(unix_dir) + unix_dir

            converted_path = converted_path.replace("//", "/")

            return converted_path

    @staticmethod
    def execute_script_file(script_path, data_product_id, environment) -> str:
        """
        Executes a script file and returns its output or error message.

        The function first checks the operating system, then uses the corresponding command to run the script.
        If the script execution fails (i.e., if the return code is non-zero), a subprocess.CalledProcessError is raised.

        Args:
            script_path (str): The path to the script to execute.
            shell (bool, optional): If true, the specified command will be executed through the shell. Default is False.

        Raises:
            subprocess.CalledProcessError: If there is an error executing the script. The exception object will contain the return code, command, output, and error message.
            Exception: If there is an unknown error.

        Returns:
            tuple: A tuple containing two elements:
                - int: The status code - 200 for successful execution, 500 for an error.
                - str: The output of the script in case of success, or the error message in case of an error.
        """

        tracer, logger = LoggerSingleton.instance(
            NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
        ).initialize_logging_and_tracing()

        with tracer.start_as_current_span("execute_script_file"):
            try:
                result_string = ""

                # Determine the current operating system
                os_name = platform.system()
                if os_name == "Windows":
                    # In Windows, use cmd to run the script
                    process = subprocess.Popen(
                        ["cmd", "/c", script_path], stderr=subprocess.PIPE
                    )
                elif os_name in ["Linux", "Darwin"]:
                    # In Unix-based systems, use sh to run the script
                    os.chmod(script_path, 0o755)
                    process = subprocess.Popen(
                        ["sh", script_path], stderr=subprocess.PIPE
                    )
                else:
                    raise ValueError("Unsupported platform: %s" % os_name)

                process.wait()  # Wait for the process to complete

                if process.returncode != 0:
                    # Read the error message from stderr
                    error_msg = process.stderr.read().decode("utf-8")
                    raise subprocess.CalledProcessError(
                        process.returncode,
                        process.args,
                        output=process.stdout,
                        stderr=error_msg,
                    )
                    # process.stdout contains the output
                result_string = process.stdout
                return 200, result_string

            except Exception as err:
                error_msg = "Error %s", err
                exc_info = sys.exc_info()
                LoggerSingleton.instance(
                    NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
                ).error_with_exception(error_msg, exc_info)
                return 500, error_msg

    @staticmethod
    def execute_script_string(
        script_string, data_product_id, environment, shell=False
    ) -> str:
        """
        Executes a command represented as a string and returns its output or error message.

        The function runs the command using subprocess.Popen, capturing its output. If the command fails
        (i.e., if the return code is non-zero), a subprocess.CalledProcessError is raised.

        Args:
            script_string (str): The command to execute as a string.
            shell (bool, optional): If true, the specified command will be executed through the shell. Default is False.

        Raises:
            subprocess.CalledProcessError: If there is an error executing the command. The exception object will contain the return code and the command.
            Exception: If there is an unknown error.

        Returns:
            tuple: A tuple containing two elements:
                - int: The status code - 200 for successful execution, 500 for an error.
                - str: The output of the command in case of success, or the error message in case of an error.
        """

        tracer, logger = LoggerSingleton.instance(
            NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
        ).initialize_logging_and_tracing()

        with tracer.start_as_current_span("execute_script_string"):
            try:
                result_string = ""

                with Popen(
                    script_string,
                    stdout=PIPE,
                    bufsize=1,
                    universal_newlines=True,
                    shell=shell,
                ) as p_output:
                    if p_output is not None:
                        stdout = p_output.stdout
                        if stdout is not None:
                            for line in stdout:
                                # process line here
                                result_string = result_string + line
                    else:
                        result_string = "p_output is None"

                if p_output.returncode != 0:
                    raise CalledProcessError(p_output.returncode, p_output.args)

                return 200, result_string

            except Exception as err:
                error_msg = "Error %s", err
                exc_info = sys.exc_info()
                LoggerSingleton.instance(
                    NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
                ).error_with_exception(error_msg, exc_info)
                return 500, error_msg

    @staticmethod
    def get_local_bin_folder():
        """
        Get the path to the .local/bin folder in the user's home directory.
        If the folder doesn't exist, it will be created.

        Returns:
            str: Path to the .local/bin folder
        """
        # Get the user's home directory
        home_dir = os.path.expanduser("~")

        # Create the .local/bin folder if it doesn't exist
        bin_folder = os.path.join(home_dir, ".local", "bin")
        os.makedirs(bin_folder, exist_ok=True)

        return bin_folder

    @staticmethod
    def import_xattr():
        if sys.platform.startswith("linux") or sys.platform == "darwin":
            try:
                xattr_module = importlib.import_module("xattr")
                return xattr_module
            except ImportError:
                print("Unable to import 'xattr'. Please install the 'xattr' package.")
                # Handle the ImportError or use a fallback method if necessary.
                return None
        else:
            print("The 'xattr' module is not supported on this operating system.")
            # Handle the case where the module is not supported on the current OS.
            return None

    @classmethod
    def set_file_metadata(cls, file_path, key, value, data_product_id, environment):
        tracer, logger = LoggerSingleton.instance(
            NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
        ).initialize_logging_and_tracing()

        with tracer.start_as_current_span("set_file_metadata"):
            try:
                if sys.platform.startswith("win"):
                    import win32api
                    import win32con

                    # Convert the key and value to a null-terminated string
                    key = key + "\x00"
                    value = value + "\x00"

                    # Set the metadata using the Windows API
                    win32api.SetFileAttributes(
                        file_path,
                        win32api.GetFileAttributes(file_path)
                        & ~win32con.FILE_ATTRIBUTE_ARCHIVE,
                    )
                    win32api.SetFileExtendedAttribute(file_path, key, value)
                    win32api.SetFileAttributes(
                        file_path,
                        win32api.GetFileAttributes(file_path)
                        | win32con.FILE_ATTRIBUTE_ARCHIVE,
                    )

                elif sys.platform.startswith("darwin") or sys.platform.startswith(
                    "linux"
                ):
                    xattr = cls.import_xattr()

                    # Convert the key and value to strings
                    key_str = str(key)
                    value_str = str(value)

                    # Encode the key and value as bytes
                    key_bytes = key_str.encode("utf-8")
                    value_bytes = value_str.encode("utf-8")

                    # Set the metadata using the xattr library
                    xattr.setxattr(file_path, key_bytes, value_bytes)

                else:
                    raise ValueError(
                        "Unsupported operating system: {}".format(sys.platform)
                    )

            except OSError as os_error:
                logger.warning("Failed to set file metadata: %s", str(os_error))

            except Exception as ex:
                # Raise all other exceptions
                raise

    @staticmethod
    def download_file(
        url: str,
        data_product_id,
        environment,
        timeout: int = 60,
        download_folder: str = "",
        local_file_name="",
    ) -> str:
        """
        Downloads a file from a URL.

        Args:
            url (str): The URL of the file to download.
            timeout (int, optional): The maximum number of seconds to wait for the request to complete. Default is 60 seconds.
            download_folder (str, optional): The folder where the downloaded file will be saved. If the folder doesn't exist, it will be created. Default is the user's .local/bin folder.
            local_file_name (str, optional): The name of the downloaded file. If not provided, the file name in the URL will be used.

        Returns:
            tuple: A tuple consisting of an integer and a string.
                The integer is the HTTP status code - 200 for a successful download, 500 for an error.
                The string is the local file path where the file was saved in case of success, or the error message in case of an error.
        """

        tracer, logger = LoggerSingleton.instance(
            NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
        ).initialize_logging_and_tracing()

        with tracer.start_as_current_span("download_file"):
            try:
                logger.info(f"download_file: {url}")
                if local_file_name is None or local_file_name == "":
                    local_file_name = url.split("/")[-1]

                # Get the user's home directory
                home_dir = os.path.expanduser("~")

                # Create the .local/bin folder if it doesn't exist
                bin_folder = os.path.join(home_dir, ".local", "bin")
                os.makedirs(bin_folder, exist_ok=True)

                # Check if download_folder exists and local_file_name doesn't contain a path
                if (
                    download_folder
                    and os.path.basename(local_file_name) == local_file_name
                ):
                    local_file_name = os.path.join(download_folder, local_file_name)
                else:
                    local_file_name = os.path.join(bin_folder, local_file_name)

                # NOTE the stream=True parameter below
                with requests.get(url, stream=True, timeout=timeout) as request_result:
                    request_result.raise_for_status()
                    with open(local_file_name, "wb") as file_result:
                        for chunk in request_result.iter_content(chunk_size=8192):
                            # If you have chunk encoded response uncomment if
                            # and set chunk_size parameter to None.
                            # if chunk:
                            file_result.write(chunk)
                return 200, local_file_name
            except requests.exceptions.HTTPError as errh:
                error_msg = "Http Error: %s", errh
                exc_info = sys.exc_info()
                LoggerSingleton.instance(
                    NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
                ).error_with_exception(error_msg, exc_info)
                return 500, error_msg
            except requests.exceptions.ConnectionError as errc:
                error_msg = "Http connectuion Error: %s", errc
                exc_info = sys.exc_info()
                LoggerSingleton.instance(
                    NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
                ).error_with_exception(error_msg, exc_info)
                return 500, error_msg
            except requests.exceptions.Timeout as errt:
                error_msg = "Http timeout Error: %s", errt
                exc_info = sys.exc_info()
                LoggerSingleton.instance(
                    NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
                ).error_with_exception(error_msg, exc_info)
                return 500, error_msg
            except Exception as err:
                error_msg = "Error: %s", err
                exc_info = sys.exc_info()
                LoggerSingleton.instance(
                    NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
                ).error_with_exception(error_msg, exc_info)
                return 500, error_msg

    @staticmethod
    def scrub_utf_8_text(original_str: str) -> str:
        """
        Scrubs the given text by encoding it as UTF-8 and decoding it back,
        removing any invalid UTF-8 characters in the process.

        Args:
            original_str (str): The original text to be scrubbed.

        Returns:
            str: The scrubbed text.

        """
        encoded_bytes = original_str.encode("utf-8", errors="ignore")
        decoded_string = encoded_bytes.decode("utf-8")
        return decoded_string

    @staticmethod
    def scrub_file_name(original_file_name: str) -> str:
        """Scrubs characters in object to rename

        Args:
            original_file_name (str): original column name

        Returns:
            str: new object name
        """

        if original_file_name is None:
            original_file_name = "object_name_is_missing"

        c_renamed = original_file_name
        c_renamed = c_renamed.replace("†", "_")
        c_renamed = c_renamed.replace(",", "_")
        c_renamed = c_renamed.replace("*", "_")
        c_renamed = c_renamed.replace(" ", "_")
        c_renamed = c_renamed.replace("\r", "_")
        c_renamed = c_renamed.replace("\n", "_")
        c_renamed = c_renamed.replace(";", "")
        c_renamed = c_renamed.replace(".", "")
        c_renamed = c_renamed.replace("}", "")
        c_renamed = c_renamed.replace("{", "")
        c_renamed = c_renamed.replace("(", "")
        c_renamed = c_renamed.replace(")", "")
        c_renamed = c_renamed.replace("?", "")
        c_renamed = c_renamed.replace("-", "")
        c_renamed = c_renamed.replace("/", "")
        c_renamed = c_renamed.replace("//", "")
        c_renamed = c_renamed.replace("=", "_")
        c_renamed = c_renamed.replace("&", "w")
        c_renamed = c_renamed.lower()
        c_renamed = c_renamed.strip()

        return c_renamed

    @classmethod
    def prepend_line_to_file(
        cls,
        source_path: str,
        destination_path: str,
        line_to_prepend: str,
        data_product_id: str,
        environment: str,
    ) -> str:
        """Add line to the beginning of a file

        Args:
            source_path (str): _description_
            destination_path (str): _description_
            line_to_prepend (str): _description_

        Returns:
            str: Status of operation
        """

        tracer, logger = LoggerSingleton.instance(
            NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
        ).initialize_logging_and_tracing()

        with tracer.start_as_current_span("download_file"):
            try:
                result = "running"
                print(f"source_path: {source_path}")
                print(f"destination_path: {destination_path}")
                with open(source_path, "r", encoding="utf-8") as original:
                    data = original.read()
                with open(destination_path, "w", encoding="utf-8") as modified:
                    modified.write(f"{line_to_prepend}\n" + data)
                result = "Success"
                return result
            except Exception as err:
                error_msg = "Error %s", err
                exc_info = sys.exc_info()
                LoggerSingleton.instance(
                    NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
                ).error_with_exception(error_msg, exc_info)
                return 500, error_msg

    @classmethod
    def combine_files(
        cls, source_path: str, file_mask: str, destination_path: str
    ) -> str:
        """Joins/combines multilple files

        Args:
            source_path (str): _description_
            file_mask (str): _description_
            destination_path (str): _description_

        Returns:
            str: Status of operation
        """
        result = "running"
        source_files = f"{source_path}{file_mask}"
        all_files = glob.glob(source_files)
        with open(destination_path, "w+", encoding="utf-8", newline="\n") as f_output:
            for filename in all_files:
                print(f"filename:{filename}")
                with open(filename, "r", encoding="utf-8", newline="\n") as f_input:
                    for line in f_input:
                        f_output.write(line)
        result = "Success"
        return result

    @classmethod
    def get_file_size(
        cls,
        running_local: bool,
        path: str,
        dbutils,
        spark: SparkSession,
        data_product_id,
        environment,
        client_id: str = None,
        client_secret: str = None,
        tenant_id: str = None,
        account_name: str = None,
    ) -> int:
        """Takes in file path, dbutils object and spark object, returns file size of provided path

        Args:
            running_local (bool): Flag indicating if the code is running locally or on Databricks
            path (str): Path to check file size
            dbutils (object): Databricks dbutils object
            spark (SparkSession): Spark session object
            client_id (str, optional): Client ID for authentication. Defaults to None.
            client_secret (str, optional): Client secret for authentication. Defaults to None.
            tenant_id (str, optional): Tenant ID for authentication. Defaults to None.

        Returns:
            int: File size of the provided path. Returns -1 if the file does not exist.
        """

        tracer, logger = LoggerSingleton.instance(
            NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
        ).initialize_logging_and_tracing()

        with tracer.start_as_current_span("get_file_size"):
            try:
                file_exists = cls.file_exists(
                    running_local,
                    path,
                    data_product_id,
                    environment,
                    dbutils,
                    client_id,
                    client_secret,
                    tenant_id,
                )

                if file_exists is True:
                    ddl_schema_3 = StructType(
                        [
                            StructField("path", StringType()),
                            StructField("name", StringType()),
                            StructField("size", IntegerType()),
                        ]
                    )

                    ddl_schema_4 = StructType(
                        [
                            StructField("path", StringType()),
                            StructField("name", StringType()),
                            StructField("size", IntegerType()),
                            StructField("modification_time", LongType()),
                        ]
                    )

                    if running_local is True:
                        https_path = cls.convert_abfss_to_https_path(
                            path, data_product_id, environment
                        )
                        storage_account_loc = urlparse(https_path).netloc
                        account_url = f"https://{storage_account_loc}"
                        storage_path = urlparse(https_path).path
                        storage_path_list = storage_path.split("/")
                        storage_container = storage_path_list[1]
                        file_path = storage_path.lstrip("/")
                        if file_path.startswith(f"{storage_container}/"):
                            file_path = file_path.replace(
                                f"{storage_container}/", "", 1
                            )

                        obj_az_storage_file = AzStorageFile()
                        file_size = obj_az_storage_file.get_file_size(
                            account_url,
                            tenant_id,
                            client_id,
                            client_secret,
                            storage_container,
                            file_path,
                            data_product_id,
                            environment,
                        )
                    else:
                        logger.info(f"command: dbutils.fs.ls({path})")
                        sk_list = dbutils.fs.ls(path)
                        logger.info(f"num_elements:{len(sk_list)}")

                        df_file_list = None

                        if len(sk_list) > 0:
                            if len(sk_list[0]) == 3:
                                df_file_list = spark.createDataFrame(
                                    sk_list, ddl_schema_3
                                )
                            elif len(sk_list[0]) == 4:
                                df_file_list = spark.createDataFrame(
                                    sk_list, ddl_schema_4
                                )

                            if df_file_list is None:
                                file_size = 0
                            else:
                                first = df_file_list.first()
                                if first is not None:
                                    file_size = first.size
                                else:
                                    file_size = -1

                            # df_file_list = df_file_list.toPandas()
                            # file_size = df_file_list.iloc[0, df_file_list.columns.get_loc("size")]

                            file_size = int(str(file_size))
                        else:
                            file_size = -1
                else:
                    file_size = -1

                return file_size
            except Exception as ex:
                error_msg = "Error: %s", ex
                exc_info = sys.exc_info()
                LoggerSingleton.instance(
                    NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
                ).error_with_exception(error_msg, exc_info)
                raise

    @staticmethod
    def convert_abfss_to_https_path(
        abfss_path: str, data_product_id: str, environment: str
    ) -> str:
        """Converts abfs path to https path

        Args:
            abfss_path (str): abfss path

        Returns:
            str: https path
        """

        tracer, logger = LoggerSingleton.instance(
            NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
        ).initialize_logging_and_tracing()

        with tracer.start_as_current_span("convert_abfss_to_https_path"):
            try:
                # Use os.path.normpath() to normalize the path and handle both slashes
                normalized_path = os.path.normpath(abfss_path)

                # Split the path using the separator (either / or \) and get the hostname
                hostname = normalized_path.split(os.sep)[1]

                file_system = hostname.split("@")[0]
                logger.info(f"hostname:{hostname}")
                logger.info(f"file_system:{file_system}")
                storage_account = hostname.split("@")[1]
                logger.info(f"storage_account:{storage_account}")
                https_path = abfss_path.replace(
                    hostname, storage_account + "/" + file_system
                )
                https_path = https_path.replace("abfss", "https")

                # Replace backslashes with forward slashes for uniformity
                https_path = https_path.replace("\\", "/")

                # Check if the path starts with a valid URL scheme
                if not https_path.startswith("http://") and not https_path.startswith(
                    "https://"
                ):
                    https_path = (
                        "https://" + https_path
                    )  # Add "https://" as the default scheme
                else:
                    # Correct double "https://" occurrences
                    https_path = https_path.replace("https://https:/", "https://")
                    https_path = https_path.replace("https://https://", "https://")

                return https_path

            except Exception as ex:
                error_msg = "Error: %s", ex
                exc_info = sys.exc_info()
                LoggerSingleton.instance(
                    NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
                ).error_with_exception(error_msg, exc_info)
                raise

    @staticmethod
    def save_text_to_file(
        directory_path: str,
        text: str,
        file_name: str,
        file_extension: str,
        data_product_id: str,
        environment: str,
    ):
        """
        Save the given text to a file with the specified directory, file name, and extension.

        Args:
            directory_path (str): The directory path where the file will be saved.
            text (str): The text to be written to the file.
            file_name (str): The name of the file (without the extension).
            file_extension (str): The extension of the file.

        Raises:
            Exception: If an error occurs while saving the file.

        """

        tracer, logger = LoggerSingleton.instance(
            NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
        ).initialize_logging_and_tracing()

        with tracer.start_as_current_span("save_text_to_file"):
            try:
                logger.info("Preparing to save file")
                file_name_with_extension = (
                    f"{os.path.splitext(file_name)[0]}.{file_extension}"
                )

                # Ensure directory path ends with a path separator
                if not directory_path.endswith(os.path.sep):
                    directory_path += os.path.sep

                file_path = os.path.join(directory_path, file_name_with_extension)

                with open(file_path, "w") as file:
                    file.write(text)

            except Exception as ex:
                error_msg = f"Error: {ex}"
                exc_info = sys.exc_info()
                LoggerSingleton.instance(
                    NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
                ).error_with_exception(error_msg, exc_info)
                raise

    @classmethod
    def file_exists(
        cls,
        running_local: bool,
        path: str,
        data_product_id: str,
        environment: str,
        dbutils=None,
        client_id: str = None,
        client_secret: str = None,
        tenant_id: str = None,
    ) -> bool:
        """
        Checks whether a file exists at the provided path.

        Args:
            running_local (bool): A flag indicating if the function is running locally or on Databricks.
            path (str): The path to the file that should be checked.
            dbutils (object): An instance of Databricks dbutils. Used for filesystem operations when not running locally.
            client_id (str): The client ID for authentication (optional, required only when running locally with Azure Data Lake Storage Gen2).
            client_secret (str): The client secret for authentication (optional, required only when running locally with Azure Data Lake Storage Gen2).
            tenant_id (str): The tenant ID for authentication (optional, required only when running locally with Azure Data Lake Storage Gen2).

        Returns:
            bool: Returns True if the file exists, and False otherwise.
        """

        tracer, logger = LoggerSingleton.instance(
            NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
        ).initialize_logging_and_tracing()

        with tracer.start_as_current_span("file_exists"):
            try:
                if running_local is True:
                    if path.startswith("abfss://"):
                        try:
                            obj_az_storage_file = AzStorageFile()
                            b_exists = obj_az_storage_file.file_exists(
                                running_local,
                                path,
                                data_product_id,
                                environment,
                                dbutils,
                                client_id,
                                client_secret,
                                tenant_id,
                            )
                            return b_exists
                        except Exception as e:
                            raise e
                    else:
                        return os.path.exists(path)
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
                            b_exists = False
                        else:
                            b_exists = False
                            raise

                logger.info(f"b_exists: {b_exists}")
                return b_exists
            except Exception as ex:
                error_msg = "Error: %s", ex
                exc_info = sys.exc_info()
                LoggerSingleton.instance(
                    NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
                ).error_with_exception(error_msg, exc_info)
                raise

    @staticmethod
    def get_latest_file(
        path, data_product_id, environment, file_type=None, prefix=None
    ):
        """
        Gets the most recently modified file in a given directory.

        Args:
            path (str): The path to the directory to search.
            file_type (str): File extension to filter by.
            prefix (str): Prefix to filter files by.

        Returns:
            str: The full path of the most recently modified file. If the directory is empty or does not exist,
            returns an empty string.
        """

        tracer, logger = LoggerSingleton.instance(
            NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
        ).initialize_logging_and_tracing()

        with tracer.start_as_current_span("get_latest_file"):
            try:
                files = glob.glob(os.path.join(path, "*"))
                if file_type:
                    if "." not in file_type:
                        file_type = "." + file_type
                    files = [file for file in files if file.endswith(f"{file_type}")]
                if prefix:
                    files = [
                        file
                        for file in files
                        if os.path.basename(file).startswith(prefix)
                    ]
                if not files:  # If no files found, return None
                    return None
                latest_file = max(files, key=os.path.getctime)
                return latest_file
            except Exception as ex:
                error_msg = "Error: %s", ex
                exc_info = sys.exc_info()
                LoggerSingleton.instance(
                    NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
                ).error_with_exception(error_msg, exc_info)
                raise

    @staticmethod
    def create_tar_gz_for_folder(
        folder_name, output_file_name_no_extension, data_product_id, environment
    ):
        """
        Archives the specified folder into a tar.gz file.

        Args:
            folder_name (str): The name of the folder to archive. This should be the full path to the folder.
            output_file_name_no_extension (str): The desired name of the output file without the extension.

        Returns:
            str: The full path to the created archive file.
        """

        tracer, logger = LoggerSingleton.instance(
            NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
        ).initialize_logging_and_tracing()

        with tracer.start_as_current_span("create_tar_gz_for_folder"):
            try:
                subprocess.run(
                    [
                        "tar",
                        "-zcf",
                        f"{output_file_name_no_extension}.tar.gz",
                        "-C",
                        folder_name,
                        ".",
                    ],
                    check=True,
                )
                return (
                    f"Tar file: {output_file_name_no_extension} created successfully."
                )
            except subprocess.CalledProcessError as ex:
                return f"An error occurred while creating tar file: {str(ex)}"
            except Exception as ex:
                error_msg = "Error: %s", ex
                exc_info = sys.exc_info()
                LoggerSingleton.instance(
                    NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
                ).error_with_exception(error_msg, exc_info)
                raise

    @classmethod
    def is_valid_json(cls, file_path, data_product_id, environment):
        """
        Check if a file contains valid JSON.

        This function attempts to load the contents of a file as JSON.
        If the loading process fails due to a `json.JSONDecodeError`,
        it's assumed that the file does not contain valid JSON and the function returns False.
        If the loading process succeeds, the function returns True.

        Args:
            file_path (str): The path to the file to be checked.

        Returns:
            bool: True if the file contains valid JSON, False otherwise.
        """

        tracer, logger = LoggerSingleton.instance(
            NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
        ).initialize_logging_and_tracing()

        with tracer.start_as_current_span("is_valid_json"):
            try:
                file_path = cls.convert_to_current_os_dir(
                    file_path, data_product_id, environment
                )
                logger.info(f"file_path: {file_path}")
                with open(file_path, "r", encoding="utf-8") as file_contents:
                    json.load(file_contents)
                return True
            except json.JSONDecodeError:
                return False
            except Exception as ex:
                error_msg = "Error: %s", ex
                exc_info = sys.exc_info()
                LoggerSingleton.instance(
                    NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
                ).error_with_exception(error_msg, exc_info)
                raise
