"""
azd_client module

This module provides functionality to download and install the azd client and run azd commands.

Classes:
    AzdClient: A class used to install the azd client and run azd commands.

Usage:
    # Create an instance of AzClient
    client = AzClient()

    # Download and install azd client
    client.download_and_install_azd()

    # Run azd commands
    client.run_azd_command("some_command --option value")
"""
import os
import sys
import platform

from cdh_lava_core.cdc_log_service.environment_logging import LoggerSingleton
from cdh_lava_core.cdc_tech_environment_service import environment_file as cdc_env_file

# Get the currently running file name
NAMESPACE_NAME = os.path.basename(os.path.dirname(__file__))
# Get the parent folder name of the running file
SERVICE_NAME = os.path.basename(__file__)
AZD_URL = "https://github.com/Azure/azure-dev/releases/download/azure-dev-cli_1.0.2/azd-linux-amd64.tar.gz"


class AzdClient:
    """This class is used to install azd and run azd commands"""

    @staticmethod
    def download_and_install_azd(data_product_id, environment):
        """
        Downloads and installs the azd client.

        This method performs the following steps:
        1. Downloads azd-linux-amd64.tar.gz from the official GitHub repository.
        2. Extracts the contents of the tarball.
        3. Makes the azd-linux-amd64 executable.
        4. Copies azd-linux-amd64 to the ~/.local/bin directory.
        5. Creates a symbolic link to azd-linux-amd64.
        6. Runs the 'azd' command.

        Note: Ensure that the necessary permissions are available to perform file
        operations and execute the 'azd' command.
        """

        tracer, logger = LoggerSingleton.instance(
            NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
        ).initialize_logging_and_tracing()

        with tracer.start_as_current_span("download_and_install_azd"):
            try:
                # Change directory to home (~)
                download_dir = os.path.expanduser("~")
                os.chdir(download_dir)
                logger.info(f"Changed directory to {download_dir}")

                env_file = cdc_env_file.EnvironmentFile()

                url = ""
                local_file_name = ""

                if platform.system() == "Windows":
                    url = 'https://aka.ms/install-azd.ps1"'
                    local_file_name = "install-azd.ps1"
                elif platform.system() == "Linux":
                    local_file_name = "https://aka.ms/install-azd.sh"
                else:
                    logger.info("Unsupported platform")
                    return

                logger.info(f"Downloading {url} to {local_file_name}")
                status_code, result_content = env_file.download_file(
                    url=url, local_file_name=local_file_name
                )

                if status_code != 200:
                    error_msg = "Error: %s", str(result_content)
                    logger.error(error_msg)
                else:
                    msg = "Output %s", str(result_content)
                    logger.info(msg)

                script_path = os.path.join(download_dir, local_file_name)

                logger.info(f"Executing {script_path}")
                status_code, result_content = env_file.execute_script_file(script_path)

                if status_code != 200:
                    logger.error(f"Error: {result_content.decode()}")
                else:
                    logger.info(f"Output: {result_content.decode()}")

                status_code, result_content = env_file.execute_script_string(
                    script_path
                )

                script_string = "azd --version"
                status_code, result_content = env_file.execute_script_string(
                    script_string
                )

            except Exception as ex:
                error_msg = f"An unexpected error occurred: {str(ex)}"
                exc_info = sys.exc_info()
                LoggerSingleton.instance(
                    NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
                ).error_with_exception(error_msg, exc_info)
                LoggerSingleton.instance(
                    NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
                ).force_flush()
                return 500, {"error": f"An unexpected error occurred: {error_msg}"}
