""" Module for tar_compression for cdc_tech_environment_service with
 minimal dependencies. """

import os
import sys
import subprocess
import tarfile
from cdh_lava_core.cdc_log_service.environment_logging import LoggerSingleton

# Get the currently running file name
NAMESPACE_NAME = os.path.basename(os.path.dirname(__file__))
# Get the parent folder name of the running file
SERVICE_NAME = os.path.basename(__file__)

# Get the currently running file name
NAMESPACE_NAME = os.path.basename(os.path.dirname(__file__))
# Get the parent folder name of the running file
SERVICE_NAME = os.path.basename(__file__)


class EnvironmentTar:
    @staticmethod
    def decompress_tar_gz(file_path, extract_to="."):
        """
        Decompresses a .tar.gz file to the specified directory.

        Args:
            file_path (str): The path to the .tar.gz file.
            extract_to (str, optional): The directory to extract the contents to. Defaults to the current directory.

        Raises:
            tarfile.TarError: If there is an error while extracting the .tar.gz file.

        """
        with tarfile.open(file_path, "r:gz") as tar:
            tar.extractall(path=extract_to)

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
