import os
import sys
import subprocess

from cdh_lava_core.cdc_log_service.environment_logging import LoggerSingleton

# Get the currently running file name
NAMESPACE_NAME = os.path.basename(os.path.dirname(__file__))
# Get the parent folder name of the running file
SERVICE_NAME = os.path.basename(__file__)


class MermaidClient:
    """
    A class representing a client for interacting with Mermaid.
    """

    @staticmethod
    def add_mermaid_to_path(data_product_id, environment):
        """
        Adds the mmdc executable path to the PATH environment variable.

        This function retrieves the npm path and appends the mmdc executable path to the PATH environment variable.
        It then checks if mmdc is accessible by running the `mmdc --version` command.

        Raises:
            subprocess.CalledProcessError: If the `mmdc` command fails.
            FileNotFoundError: If `mmdc` is not found in the PATH.
            subprocess.SubprocessError: If there is an error during the subprocess execution.
        """

        tracer, logger = LoggerSingleton.instance(
            NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
        ).initialize_logging_and_tracing()

        with tracer.start_as_current_span("add_mermaid_to_path"):
            try:
                npm_path = subprocess.check_output(
                    ["npm", "config", "get", "prefix"], text=True
                ).strip()
                mmdc_path = os.path.join(npm_path, "node_modules", ".bin")

                # Add mmdc path to the PATH environment variable
                os.environ["PATH"] += os.pathsep + mmdc_path

                # Check if mmdc is now accessible
                subprocess.run(
                    ["mmdc", "--version"],
                    check=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                )
                logger.info("mmdc is accessible in the script.")
            except subprocess.CalledProcessError:
                error_msg = "mmdc command failed."
                exc_info = sys.exc_info()
                LoggerSingleton.instance(
                    NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
                ).error_with_exception(error_msg, exc_info)
                raise
            except FileNotFoundError:
                error_msg = "mmdc is not found in the PATH."
                exc_info = sys.exc_info()
                LoggerSingleton.instance(
                    NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
                ).error_with_exception(error_msg, exc_info)
                raise
            except subprocess.SubprocessError as e:
                error_msg = "Error: %s", e
                exc_info = sys.exc_info()
                LoggerSingleton.instance(
                    NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
                ).error_with_exception(error_msg, exc_info)
                raise

    @staticmethod
    def install_mermaid(data_product_id, environment):
        """
        Install Mermaid by running the npm install command.

        Returns:
            A subprocess.CompletedProcess object representing the result of the installation command.
        """

        tracer, logger = LoggerSingleton.instance(
            NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
        ).initialize_logging_and_tracing()

        with tracer.start_as_current_span("install_mermaid"):
            try:
                npm_command = [
                    "npm",
                    "install",
                    "@mermaid-js/mermaid-cli",
                    "--global",
                    "--registry=https://registry.npmjs.org",
                ]
                result = subprocess.run(
                    npm_command,
                    check=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    shell=True,
                )

                logger.info("result: %s", str(result))
                return result
            except FileNotFoundError as ex_file_not_found:
                error_msg = (
                    f"Error: {ex_file_not_found} running command {npm_command}",
                )
                exc_info = sys.exc_info()
                LoggerSingleton.instance(
                    NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
                ).error_with_exception(error_msg, exc_info)
                raise
            except subprocess.CalledProcessError as ex:
                error_msg = "Error: %s", ex
                exc_info = sys.exc_info()
                LoggerSingleton.instance(
                    NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
                ).error_with_exception(error_msg, exc_info)
                raise

    @staticmethod
    def show_help(data_product_id, environment):
        """
        Display the help information for the mermaid command.

        Returns:
            The result of the subprocess run.
        Raises:
            FileNotFoundError: If the 'mmdc' command is not found.
            subprocess.CalledProcessError: If an error occurs while running the command.
        """

        tracer, logger = LoggerSingleton.instance(
            NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
        ).initialize_logging_and_tracing()

        with tracer.start_as_current_span("show_help"):
            try:
                mermaid_command = ["mmdc", "-h"]
                result = subprocess.run(
                    mermaid_command,
                    check=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                )
                logger.info("result.stdout: %s", result.stdout)
                return result
            except FileNotFoundError as ex_file_not_found:
                error_msg = (
                    f"Error: {ex_file_not_found} running command {mermaid_command}",
                )
                exc_info = sys.exc_info()
                LoggerSingleton.instance(
                    NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
                ).error_with_exception(error_msg, exc_info)
                raise
            except subprocess.CalledProcessError as ex:
                error_msg = "Error: %s", ex
                exc_info = sys.exc_info()
                LoggerSingleton.instance(
                    NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
                ).error_with_exception(error_msg, exc_info)
                raise

    @staticmethod
    def export_mermaid(
        memaid_file_path,
        output_file_path,
        data_product_id,
        environment,
        output_format="transparent",
    ):
        """
        Export a Mermaid file to a specified output format.

        Args:
            memaid_file_path (str): The path to the Mermaid file.
            output_file_path (str): The path to save the output file.
            background_format (str): The desired background format. Defaults to 'transparent'.

        Returns:
            subprocess.CompletedProcess: The result of the export process.

        Raises:
            FileNotFoundError: If the 'mmdc' command is not found.
            subprocess.CalledProcessError: If the export process fails.
        """

        logger_singleton = LoggerSingleton.instance(NAMESPACE_NAME, SERVICE_NAME)
        with tracer.start_as_current_span("export_mermaid"):
            try:
                mermaid_command = [
                    "mmdc",
                    "-i",
                    memaid_file_path,
                    "-o",
                    output_file_path,
                    "-b",
                    "transparent",
                ]
                result = subprocess.run(
                    mermaid_command,
                    check=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                )
                logger.info("result.stdout: %s", result.stdout)
                return result
            except FileNotFoundError as ex_file_not_found:
                error_msg = (
                    f"Error: {ex_file_not_found} running command {mermaid_command}",
                )
                exc_info = sys.exc_info()
                LoggerSingleton.instance(
                    NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
                ).error_with_exception(error_msg, exc_info)
                raise
            except subprocess.CalledProcessError as ex:
                error_msg = "Error: %s", ex
                exc_info = sys.exc_info()
                LoggerSingleton.instance(
                    NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
                ).error_with_exception(error_msg, exc_info)
                raise
