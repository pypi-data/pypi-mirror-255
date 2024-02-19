from azure.storage.filedatalake import DataLakeServiceClient
from azure.identity import ClientSecretCredential
from azure.storage.filedatalake import DataLakeDirectoryClient
from urllib.parse import urlparse
from cdh_lava_core.databricks_service import repo_core as databricks_repo_core

# error handling
from subprocess import check_output, Popen, PIPE, CalledProcessError
import os
import sys
import subprocess
import requests

# Get the currently running file name
NAMESPACE_NAME = os.path.basename(os.path.dirname(__file__))
# Get the parent folder name of the running file
SERVICE_NAME = os.path.basename(__file__)

from cdh_lava_core.cdc_log_service.environment_logging import LoggerSingleton
from cdh_lava_core.cdc_tech_environment_service.environment_http import EnvironmentHttp


class AzStorageFile:
    """
    A class that provides utility methods for working with files in Azure Data Lake Storage.
    """

    @staticmethod
    def get_file_size(
        account_url: str,
        tenant_id,
        client_id: str,
        client_secret: str,
        storage_container: str,
        file_path: str,
        data_product_id: str,
        environment: str,
    ):
        """
        Retrieves the size of a file in an Azure Data Lake Storage account.

        Args:
            account_url (str): The URL of the Azure Storage account. Example: https://<account_name>.dfs.core.windows.net.
            tenant_id (str): The tenant ID of the Azure Active Directory.
            client_id (str): The client ID of the Azure Active Directory application.
            client_secret (str): The client secret of the Azure Active Directory application.
            storage_container (str): The name of the file system in the Azure Data Lake Storage account.
            file_path (str): The path to the file in the file system.

        Returns:
            int: The size of the file in bytes.

        Raises:
            Exception: If there is an error retrieving the file properties.
        """

        credential = ClientSecretCredential(tenant_id, client_id, client_secret)

        service_client = DataLakeServiceClient(
            account_url=account_url,
            credential=credential,
        )
        file_system_client = service_client.get_file_system_client(storage_container)
        file_client = file_system_client.get_file_client(file_path)

        try:
            file_props = file_client.get_file_properties()
            return file_props.size  # Returns the size of the file in bytes
        except Exception as e:
            print(e)
            return None

    @classmethod
    def rename_directory(cls, config: dict, source_path, new_directory_name) -> str:
        """
        Renames a directory in Azure Blob File System Storage (ABFSS).

        Args:
            config (dict): The configuration dictionary containing the necessary Azure parameters.
            source_path (str): The original path of the directory to be renamed in ABFSS.
            new_directory_name (str): The new name for the directory.

        Returns:
            str: A message indicating the status of the rename operation.
        """

        try:
            client_id = config["az_sub_client_id"]
            client_secret = config["client_secret"]

            result = "file_adls_copy failed"

            if client_secret is None:
                az_sub_client_secret_key = str(config["az_sub_client_secret_key"])
                key = az_sub_client_secret_key
                client_secret = f"Environment variable: {key} not found"

            os.environ["AZCOPY_SPA_CLIENT_SECRET"] = client_secret
            tenant_id = config["az_sub_tenant_id"]

            running_local = config["running_local"]
            print(f"running_local:{running_local}")
            print(f"source_path:{source_path}")
            print(f"new_directory_name:{new_directory_name}")

            credential = ClientSecretCredential(tenant_id, client_id, client_secret)
            storage_account_loc = urlparse(source_path).netloc
            storage_path = urlparse(source_path).path
            storage_path_list = storage_path.split("/")
            storage_container = storage_path_list[1]
            account_url = f"https://{storage_account_loc}"

            service_client = DataLakeServiceClient(
                account_url=account_url, credential=credential
            )
            file_system_client = service_client.get_file_system_client(
                storage_container
            )

            dir_path = storage_path.replace(f"{storage_container}" + "/", "")

            is_directory = None
            directory_client: DataLakeDirectoryClient
            try:
                directory_client = file_system_client.get_directory_client(dir_path)
                if directory_client.exists():
                    is_directory = True
                else:
                    is_directory = True

                if is_directory:
                    directory_client.rename_directory(new_directory_name)
                    result = "Success"
                else:
                    result = f"rename_directory failed: {dir_path} does not exist"
            except Exception as ex:
                directory_client = DataLakeDirectoryClient("empty", "empty", "empty")
                print(ex)
                result = "rename_directory failed"
        except Exception as ex_rename_directory:
            print(ex_rename_directory)
            result = "rename_directory failed"
        result = str(result)
        return result

    @classmethod
    def folder_adls_create(cls, config, dir_path: str, dbutils) -> str:
        """
        Creates a new directory in Azure Data Lake Storage (ADLS).

        Args:
            config (dict): The configuration dictionary containing the necessary Azure parameters.
            dir_path (str): The path of the directory to be created in ADLS.
            dbutils: An instance of Databricks dbutils, used for filesystem operations.

        Returns:
            str: A message indicating the status of the directory creation operation.
        """

        running_local = config["running_local"]
        client_id = config["az_sub_client_id"]
        client_secret = config["client_secret"]

        if client_secret is None:
            az_sub_client_secret_key = str(config["az_sub_client_secret_key"])
            client_secret = (
                f"Environment variable: {az_sub_client_secret_key} not found"
            )

        os.environ["AZCOPY_SPA_CLIENT_SECRET"] = client_secret
        tenant_id = config["az_sub_tenant_id"]

        storage_account_loc = urlparse(dir_path).netloc
        storage_path = urlparse(dir_path).path
        storage_path_list = storage_path.split("/")
        storage_container = storage_path_list[1]
        account_url = f"https://{storage_account_loc}"

        credential = ClientSecretCredential(tenant_id, client_id, client_secret)
        service_client = DataLakeServiceClient(
            account_url=account_url, credential=credential
        )
        file_system_client = service_client.get_file_system_client(storage_container)

        return "True"

    @classmethod
    def file_adls_copy(
        cls,
        config,
        source_path: str,
        destination_path: str,
        from_to: str,
        dbutils,
    ) -> str:
        """
        Copies a file from the local filesystem to Azure Data Lake Storage (ADLS), or vice versa.

        Args:
            config (dict): The configuration dictionary containing the necessary Azure and local filesystem parameters.
            source_path (str): The path of the file to be copied.
            destination_path (str): The path where the file will be copied. If 'bytes' is passed, the function will return a byte array instead of performing a copy.
            from_to (str): Indicates the direction of the copy. 'BlobFSLocal' signifies ADLS to local copy, and 'LocalBlobFS' signifies local to ADLS copy.
            dbutils: An instance of Databricks dbutils, used for filesystem operations.

        Returns:
            str: A message indicating the status of the copy operation.
        """

        running_local = not ("dbutils" in locals() or "dbutils" in globals())

        result = "file_adls_copy failed"
        running_local = config["running_local"]
        client_id = config["az_sub_client_id"]
        client_secret = config["client_secret"]

        if client_secret is None:
            az_sub_client_secret_key = str(config["az_sub_client_secret_key"])
            client_secret = (
                f"Environment variable: {az_sub_client_secret_key} not found"
            )

        os.environ["AZCOPY_SPA_CLIENT_SECRET"] = client_secret
        tenant_id = config["az_sub_tenant_id"]

        print(f"running_local:{running_local}")
        print(f"from_to:{from_to}")
        print(f"source_path:{source_path}")
        print(f"destination_path:{destination_path}")

        if running_local is True and (
            from_to == "BlobFSLocal" or from_to == "LocalBlobFS"
        ):
            p_1 = f"--application-id={client_id}"
            p_2 = f"--tenant-id={tenant_id}"
            arr_azcopy_command = [
                "azcopy",
                "login",
                "--service-principal",
                p_1,
                p_2,
            ]
            arr_azcopy_command_string = " ".join(arr_azcopy_command)
            print(arr_azcopy_command_string)

            try:
                check_output(arr_azcopy_command)
                result_1 = f"login --service-principal {p_1} to {p_2} succeeded"
            except subprocess.CalledProcessError as ex_called_process:
                result_1 = str(ex_called_process.output)

            print(result_1)

            if from_to == "BlobFSLocal":
                arr_azcopy_command = [
                    "azcopy",
                    "copy",
                    f"{source_path}",
                    f"{destination_path}",
                    f"--from-to={from_to}",
                    "--recursive",
                    "--trusted-microsoft-suffixes=",
                    "--log-level=INFO",
                ]
            elif from_to == "LocalBlobFS":
                arr_azcopy_command = [
                    "azcopy",
                    "copy",
                    f"{source_path}",
                    f"{destination_path}",
                    "--log-level=DEBUG",
                    f"--from-to={from_to}",
                ]
            else:
                arr_azcopy_command = [f"from to:{from_to} is not supported"]

            arr_azcopy_command_string = " ".join(arr_azcopy_command)
            print(arr_azcopy_command_string)

            try:
                check_output(arr_azcopy_command)
                result_2 = f"copy from {source_path} to {destination_path} succeeded"
            except subprocess.CalledProcessError as ex_called_process:
                result_2 = str(ex_called_process.output)

            result = result_1 + result_2
        elif (running_local is False) and from_to == "BlobFSLocal":
            credential = ClientSecretCredential(tenant_id, client_id, client_secret)
            storage_account_loc = urlparse(source_path).netloc
            storage_path = urlparse(source_path).path
            storage_path_list = storage_path.split("/")
            storage_container = storage_path_list[1]
            account_url = f"https://{storage_account_loc}"
            service_client = DataLakeServiceClient(
                account_url=account_url, credential=credential
            )
            file_system_client = service_client.get_file_system_client(
                storage_container
            )
            dir_path = storage_path.replace(f"{storage_container}" + "/", "")
            is_directory = None
            directory_client: DataLakeDirectoryClient
            try:
                directory_client = file_system_client.get_directory_client(dir_path)
                if directory_client.exists():
                    is_directory = True
                else:
                    is_directory = True
            except Exception as ex:
                directory_client = DataLakeDirectoryClient("empty", "empty", "empty")
                print(ex)

            obj_repo = databricks_repo_core.RepoCore()

            if is_directory is True:
                azure_files = []

                try:
                    azure_files = file_system_client.get_paths(path=dir_path)
                except Exception as ex:
                    print(ex)

                for file_path in azure_files:
                    print(str(f"file_path:{file_path}"))
                    file_path_name = file_path.name
                    file_name = os.path.basename(file_path_name)
                    file_client = directory_client.get_file_client(file_path)
                    file_data = file_client.download_file()
                    file_bytes = file_data.readall()
                    file_string = file_bytes.decode("utf-8")
                    first_200_chars_of_string = file_string[0:200]
                    destination_file_path = destination_path + "/" + file_path_name

                    if len(file_string) > 0:
                        try:
                            # os.remove(destination_file_path)
                            dbutils.fs.rm(destination_file_path)
                        except OSError as ex_os_error:
                            # if failed, report it back to the user
                            print(
                                f"Error: {ex_os_error.filename} - {ex_os_error.strerror}."
                            )
                        try:
                            print(
                                f"dbutils.fs.put({destination_file_path}, {first_200_chars_of_string}, True)"
                            )
                            result = dbutils.fs.put(
                                destination_file_path, file_string, True
                            )
                        except Exception as ex_os_error:
                            # if failed, report it back to the user
                            print(f"Error: {ex_os_error}.")

                        content_type = "bytes"
                        result = obj_repo.import_file(
                            config,
                            file_bytes,
                            content_type,
                            destination_file_path,
                        )

                    else:
                        result = (
                            f"destination_file_path:{destination_file_path} is empty"
                        )
                    # file_to_copy = io.BytesIO(file_bytes)
                    # print(f"destination_file_path:{destination_file_path}")
            else:
                file_path = storage_path.replace(f"{storage_container}" + "/", "")
                print(f"file_path:{file_path}")
                file_client = file_system_client.get_file_client(file_path)
                file_data = file_client.download_file()
                file_bytes = file_data.readall()
                file_string = file_bytes.decode("utf-8")
                file_name = os.path.basename(file_path)
                destination_file_path = destination_path + "/" + file_name
                first_200_chars_of_string = file_string[0:500]
                if len(file_string) > 0:
                    try:
                        # os.remove(destination_file_path)
                        dbutils.fs.rm(destination_file_path)
                    except OSError as ex_os_error:
                        # if failed, report it back to the user
                        print(f"Error: {ex_os_error.filename}-{ex_os_error.strerror}.")

                    try:
                        print(
                            f"dbutils.fs.put({destination_file_path}, {first_200_chars_of_string}, True)"
                        )
                        result = dbutils.fs.put(
                            destination_file_path, file_string, True
                        )
                    except Exception as ex_os_error:
                        # if failed, report it back to the user
                        print(f"Error: {ex_os_error}.")

                    content_type = "bytes"
                    result = obj_repo.import_file(
                        config, file_bytes, content_type, destination_file_path
                    )
                else:
                    result = f"destination_file_path:{destination_file_path} is empty"
        elif (running_local is False) and from_to == "LocalBlobFS":
            url = destination_path
            storage_account_loc = urlparse(url).netloc
            storage_path = urlparse(url).path
            storage_path_list = storage_path.split("/")
            storage_container = storage_path_list[1]
            file_name = os.path.basename(destination_path)
            dir_path = storage_path.replace(file_name, "")
            dir_path = dir_path.replace(storage_container + "/", "")
            account_url = f"https://{storage_account_loc}"
            print(f"account_url:{account_url}")
            print(f"url:{url}")
            print(f"storage_path:{storage_path}")
            print(f"storage_container:{storage_container}")
            print(f"dir_path:{dir_path}")
            print(f"file_name:{file_name}")

            credential = ClientSecretCredential(tenant_id, client_id, client_secret)
            service_client = DataLakeServiceClient(
                account_url=account_url, credential=credential
            )
            file_system_client = service_client.get_file_system_client(
                storage_container
            )
            directory_client = file_system_client.get_directory_client(dir_path)
            file_client = directory_client.create_file(file_name)
            local_file = open(source_path, "r", encoding="utf-8")
            file_contents = local_file.read()
            file_client.append_data(
                data=file_contents, offset=0, length=len(file_contents)
            )
            result = file_client.flush_data(len(file_contents))

            # with open(source_path) as f_json:
            #     json_data = json.load(f_json)
            # result = file_client.upload_data(json_data, overwrite=True, max_concurrency=5)

            # file_client = file_system_client.get_file_client(file_path)
            # file_data = file_client.download_file(0)
            # result = file_data.readall()

            # print(f" dbutils.fs.cp({source_path}, {destination_path})")
            # result = dbutils.fs.cp(source_path, destination_path)
        else:
            result = (
                "invalid config: must download/client config files from azure to local"
            )
            result = result + " - functionality not available on databricks"
            print(result)

        result = str(result)

        return result

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
        Check if a file exists at the specified path.

        Args:
            running_local (bool): Indicates if the code is running locally.
            path (str): The path of the file to check.
            data_product_id (str): The ID of the data product.
            environment (str): The environment in which the code is running.
            dbutils (optional): The dbutils object for Databricks. Defaults to None.
            client_id (str, optional): The client ID for authentication. Defaults to None.
            client_secret (str, optional): The client secret for authentication. Defaults to None.
            tenant_id (str, optional): The tenant ID for authentication. Defaults to None.

        Returns:
            bool: True if the file exists, False otherwise.
        """

        tracer, logger = LoggerSingleton.instance(
            NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
        ).initialize_logging_and_tracing()

        with tracer.start_as_current_span("file_exists"):
            try:
                if running_local is True:
                    if path.startswith("abfss://"):
                        try:
                            credential = ClientSecretCredential(
                                tenant_id, client_id, client_secret
                            )

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

                            logger.info(f"storage_path:{storage_path}")
                            logger.info(f"https_path:{https_path}")
                            logger.info(f"path:{path}")
                            service_client = DataLakeServiceClient(
                                account_url=account_url, credential=credential
                            )
                            file_system_client = service_client.get_file_system_client(
                                storage_container
                            )
                            file_client = file_system_client.get_file_client(file_path)
                            file_exists = file_client.exists()
                            logger.info(
                                f"file_path{file_path}:file_exists:{file_exists}"
                            )
                            return file_exists
                        except Exception as e:
                            raise
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

                return b_exists
            except Exception as ex:
                error_msg = "Error: %s", ex
                exc_info = sys.exc_info()
                LoggerSingleton.instance(
                    NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
                ).error_with_exception(error_msg, exc_info)
                raise

    @classmethod
    def copy_url_to_blob(
        cls,
        config: dict,
        src_url: str,
        dest_path: str,
        file_name: str,
        data_product_id: str,
        environment: str,
    ) -> str:
        """
        Downloads a file from the source URL and uploads it to the specified path in Azure Storage.

        Args:
            config (dict): The configuration dictionary containing the necessary Azure Storage parameters.
            src_url (str): The source URL from which to download the file.
            dest_path (str): The destination path in Azure Storage where the file will be uploaded.
            file_name (str): The name to be given to the file when it is uploaded to Azure Storage.

        Returns:
            str: A message indicating the status of the upload.
        """

        tracer, logger = LoggerSingleton.instance(
            NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
        ).initialize_logging_and_tracing()

        with tracer.start_as_current_span("copy_url_to_blob"):
            try:
                dest_path = cls.fix_url(dest_path, data_product_id, environment)
                info_message = f"copy_url_to_blob: src_url:{src_url}, dest_path:{dest_path}, file_name:{file_name}"
                logger.info(info_message)

                client_id = config["az_sub_client_id"]
                client_secret = config["client_secret"]
                tenant_id = config["az_sub_tenant_id"]
                if client_secret is None:
                    az_sub_client_secret_key = str(config["az_sub_client_secret_key"])
                    message = (
                        f"Environment variable: {az_sub_client_secret_key} not found"
                    )
                    client_secret = message
                    logger.info(client_secret)
                credential = ClientSecretCredential(tenant_id, client_id, client_secret)
                storage_account_loc = urlparse(dest_path).netloc
                storage_path = urlparse(dest_path).path
                storage_path_list = storage_path.split("/")
                storage_container = storage_path_list[1]
                account_url = f"https://{storage_account_loc}"
                service_client = DataLakeServiceClient(
                    account_url=account_url, credential=credential
                )
                os.environ["AZCOPY_SPA_CLIENT_SECRET"] = client_secret
                dir_path = storage_path.replace(f"{storage_container}" + "/", "")
                logger.info(f"dir_path:{dir_path}")
                file_system_client = service_client.get_file_system_client(
                    storage_container
                )
                directory_client = file_system_client.get_directory_client(dir_path)

                obj_http = EnvironmentHttp()
                http_headers = {}
                params = {}
                file_response = obj_http.get(
                    src_url, http_headers, 120, params, data_product_id, environment
                )

                if file_response.status_code != 200:
                    # Raise an exception if the status code is not 200 (OK)
                    file_response.raise_for_status()

                file_data = file_response.content
                try:
                    file_client = directory_client.create_file(file_name)
                    result = file_client.upload_data(
                        file_data, overwrite=True, max_concurrency=5
                    )
                except Exception as ex:
                    print(ex)
                    error_msg = "Error: %s", ex
                    exc_info = sys.exc_info()
                    LoggerSingleton.instance(
                        NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
                    ).error_with_exception(error_msg, exc_info)
                    result = "upload failed"
                return result

            except Exception as ex:
                error_msg = "Error: %s", ex
                exc_info = sys.exc_info()
                LoggerSingleton.instance(
                    NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
                ).error_with_exception(error_msg, exc_info)
                raise

    @staticmethod
    def fix_url(path: str, data_product_id: str, environment: str):
        """
        Fixes the URL by replacing backslashes with forward slashes and adding the default scheme "https://" if necessary.

        Args:
            path (str): The URL path to be fixed.

        Returns:
            str: The fixed URL path.
        """

        tracer, logger = LoggerSingleton.instance(
            NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
        ).initialize_logging_and_tracing()

        with tracer.start_as_current_span("fix_url"):
            try:
                original_url = path
                # Replace backslashes with forward slashes for uniformity
                path = path.replace("\\", "/")

                # Check if the path starts with a valid URL scheme
                if not path.startswith("http://") and not path.startswith("https://"):
                    path = "https://" + path  # Add "https://" as the default scheme
                else:
                    # Correct double "https://" occurrences
                    path = path.replace("https://https:/", "https://")
                    path = path.replace("https://https://", "https://")

                # Validate the URL
                parsed_url = urlparse(path)
                if not parsed_url.scheme or not parsed_url.netloc:
                    raise ValueError(
                        f"Invalid URL: original_url: {original_url}, parsed_url {parsed_url}"
                    )

                logger.info(f"original_url:{original_url}")
                logger.info(f"parsed_url:{parsed_url}")
                logger.info(f"path:{path}")
                return path

            except Exception as ex:
                error_msg = "Error: %s", ex
                exc_info = sys.exc_info()
                LoggerSingleton.instance(
                    NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
                ).error_with_exception(error_msg, exc_info)
                raise
