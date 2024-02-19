import subprocess
import sys
import os


from cdh_lava_core.cdc_log_service.environment_logging import LoggerSingleton

# Get the currently running file name
NAMESPACE_NAME = os.path.basename(os.path.dirname(__file__))
# Get the parent folder name of the running file
SERVICE_NAME = os.path.basename(__file__)


class SphinxClient:
    """
    A class representing a Sphinx client.

    Attributes:
        None

    Methods:
        build_html: Builds the HTML documentation using Sphinx.
    """

    @staticmethod
    def get_sphinx_source_dir(doc_folder_path: str, data_product_id, environment):
        """
        Gets the path to the Sphinx source directory.

        Args:
            doc_folder_path (str): The path to the Sphinx source directory.

        Returns:
            str: The path to the Sphinx source directory.
        """

        tracer, logger = LoggerSingleton.instance(
            NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
        ).initialize_logging_and_tracing()

        with tracer.start_as_current_span("get_sphinx_source_dir"):
            try:
                sphinx_path = os.path.abspath(
                    os.path.join(sys.prefix, "Scripts", "sphinx-build.exe")
                )
                return sphinx_path
            except subprocess.CalledProcessError as ex:
                error_msg = "Error: %s", ex
                exc_info = sys.exc_info()
                LoggerSingleton.instance(
                    NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
                ).error_with_exception(error_msg, exc_info)
                raise

    @staticmethod
    def build_html(doc_folder_path: str, data_product_id: str, environment: str):
        """
        Builds the HTML documentation using Sphinx.

        Args:
            doc_folder_path (str): The path to the Sphinx source directory.
            data_product_id (str): The ID of the data product.
            environment (str): The environment in which the documentation is being built.

        Returns:
            subprocess.CompletedProcess: The result of the Sphinx build command.
        """

        tracer, logger = LoggerSingleton.instance(
            NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
        ).initialize_logging_and_tracing()

        with tracer.start_as_current_span("build_html"):
            try:
                current_dir = doc_folder_path

                # Path to your Sphinx source directory (two directories up)
                sphinx_source_dir = doc_folder_path
                logger.info(f"doc_folder_path: {doc_folder_path}")
                logger.info(f"sphinx_source_dir: {sphinx_source_dir}")
                logger.info(f"current_dir: {current_dir}")

                # Path to the directory to output the HTML files
                # (two directories up and down to 'build')
                build_dir = os.path.abspath(os.path.join(current_dir, "build", "html"))
                logger.info(f"build_dir: {build_dir}")

                # Command to build Sphinx documentation
                command = ["sphinx-build", "-b", "html", sphinx_source_dir, build_dir]
                logger.info(f"command: {command}")

                # Run the Sphinx build command
                result = subprocess.run(
                    command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
                )

                logger.info("Command output: %s", result.stdout.decode())
                return result

            except subprocess.CalledProcessError as e:
                # CalledProcessError is raised when the subprocess exits with a non-zero status
                logger.error(
                    "Command '%s' failed with return code: %s", e.cmd, e.returncode
                )
                logger.error("Error output: %s", e.stderr.decode())
            except FileNotFoundError as e:
                # FileNotFoundError is raised when the command is not found
                logger.error("Command not found: %s", e.filename)
                logger.error("Full error: %s", e)
                logger.error("Current PATH: %s", os.environ.get("PATH"))
            except Exception as e:
                # Generic exception handling for any other exceptions
                logger.error("An error occurred: %s", e)

    @staticmethod
    def build_pdf(doc_folder_path: str, data_product_id, environment):
        """
        Builds the PDF documentation using Sphinx.

        Args:
            doc_folder_path (str): The path to the folder containing the Sphinx documentation.

        Returns:
            CompletedProcess: The result of the Sphinx build command.
        """

        tracer, logger = LoggerSingleton.instance(
            NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
        ).initialize_logging_and_tracing()

        with tracer.start_as_current_span("build_pdf"):
            try:
                current_dir = doc_folder_path

                # Path to your Sphinx source directory (two directories up)
                sphinx_source_dir = doc_folder_path
                print(sphinx_source_dir)

                # Path to the directory to output the HTML files
                # (two directories up and down to 'build')
                build_dir = os.path.abspath(os.path.join(current_dir, "build", "latex"))
                logger.info(f"build_dir: {build_dir}")

                # Command to build Sphinx documentation
                command = ["sphinx-build", "-b", "latex", sphinx_source_dir, build_dir]
                logger.info(f"command: {command}")

                # Run the Sphinx build command
                result = subprocess.run(
                    command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
                )

                logger.info("Command output: %s", result.stdout.decode())
                return result

            except subprocess.CalledProcessError as e:
                # CalledProcessError is raised when the subprocess exits with a non-zero status
                logger.error(
                    "Command '%s' failed with return code: %s", e.cmd, e.returncode
                )
                logger.error("Error output: %s", e.stderr.decode())
            except FileNotFoundError as e:
                # FileNotFoundError is raised when the command is not found
                logger.error("Command not found: %s", e.filename)
                logger.error("Full error: %s", e)
                logger.error("Current PATH: %s", os.environ.get("PATH"))
            except Exception as e:
                # Generic exception handling for any other exceptions
                logger.error("An error occurred: %s", e)
