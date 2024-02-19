import os
import sys
import subprocess
import platform

from cdh_lava_core.cdc_log_service.environment_logging import LoggerSingleton


# Get the currently running file name
NAMESPACE_NAME = os.path.basename(os.path.dirname(__file__))
# Get the parent folder name of the running file
SERVICE_NAME = os.path.basename(__file__)


class NpmClient:
    """
    A class representing a client for interacting with NPM.
    """

    @classmethod
    def install_node(cls, data_product_id, environment):
        """
        Install Node by running the npm install command.

        Returns:
            A subprocess.CompletedProcess object representing the result of the installation command.
        """

        tracer, logger = LoggerSingleton.instance(
            NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
        ).initialize_logging_and_tracing()

        with tracer.start_as_current_span("install_node"):
            try:
                if platform.system() == "Windows":
                    cls.install_node_windows(data_product_id, environment)
                    logger.info("Installed node")
                else:
                    logger.info("This is not a Windows operating system.")

            except subprocess.CalledProcessError as ex:
                error_msg = "Error: %s", ex
                exc_info = sys.exc_info()
                LoggerSingleton.instance(
                    NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
                ).error_with_exception(error_msg, exc_info)
                raise

    @staticmethod
    def install_node_windows(data_product_id, environment):
        """
        Installs Node.js and necessary dependencies on Windows.

        Args:
            data_product_id (str): The ID of the data product.
            environment (str): The environment in which the installation is being performed.

        Raises:
            subprocess.CalledProcessError: If any of the subprocess calls result in an error.

        """

        tracer, logger = LoggerSingleton.instance(
            NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
        ).initialize_logging_and_tracing()

        with tracer.start_as_current_span("install_node"):
            try:
                # Deactivate virtual environment if necessary
                # subprocess.call(["deactivate"], shell=True)

                # Change to the home directory
                os.chdir(os.path.expanduser("~"))

                # Uninstall nodeenv
                subprocess.call(["pip", "uninstall", "-y", "nodeenv"], shell=True)

                # Install Node.js (Requires manual download or a separate script to download and run the installer)

                # Install a specific version of npm if necessary
                # subprocess.call(["npm", "install", "npm@9.1.1", "-g"], shell=True)

                # Install nodeenv
                subprocess.call(["pip", "install", "nodeenv"], shell=True)

                # Install Mermaid CLI
                subprocess.call(
                    ["npm", "install", "@mermaid-js/mermaid-cli"], shell=True
                )

                # Test installations
                subprocess.call(["node", "-v"], shell=True)
                subprocess.call(["npm", "-v"], shell=True)
                subprocess.call(["mmdc", "-h"], shell=True)

                logger.info("installed node on windows")

            except subprocess.CalledProcessError as ex:
                error_msg = "Error: %s", ex
                exc_info = sys.exc_info()
                LoggerSingleton.instance(
                    NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
                ).error_with_exception(error_msg, exc_info)
                raise

    @staticmethod
    def create_npmrc_file(
        file_path, registry_url, auth_token, data_product_id, environment
    ):
        """
        Create an .npmrc file with the specified registry URL and authentication token.

        Args:
            file_path (str): The path to the .npmrc file to be created.
            registry_url (str): The URL of the npm registry.
            auth_token (str): The authentication token for the npm registry.
            data_product_id (str): The ID of the data product.
            environment (str): The environment in which the installation is being performed.

        Returns:
            None
        """

        tracer, logger = LoggerSingleton.instance(
            NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
        ).initialize_logging_and_tracing()

        with tracer.start_as_current_span("create_npmrc_file"):
            try:
                with open(file_path, "w", encoding="utf-8") as file:
                    file.write(f"registry={registry_url}\n")
                    file.write(f"//{registry_url}/:_authToken={auth_token}\n")

                logger.info("Create .nprc file")
            except subprocess.CalledProcessError as ex:
                error_msg = "Error: %s", ex
                exc_info = sys.exc_info()
                LoggerSingleton.instance(
                    NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
                ).error_with_exception(error_msg, exc_info)
                raise

    @staticmethod
    def publish_package(data_product_id, environment, version_bump="patch"):
        """
        Publishes a package to the npm registry.

        Args:
            data_product_id (str): The ID of the data product.
            environment (str): The environment in which the package is being published.
            version_bump (str, optional): The version bump type. Defaults to "patch".

        Returns:
            bool: True if the package was published successfully, False otherwise.
        """

        tracer, logger = LoggerSingleton.instance(
            NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
        ).initialize_logging_and_tracing()

        with tracer.start_as_current_span("publish_package"):
            try:
                # Bump the package version
                subprocess.run(["npm", "version", version_bump], check=True)

                # Publish the package
                subprocess.run(["npm", "publish"], check=True)

                logger.info("Package published successfully.")
                return True

            except subprocess.CalledProcessError as e:
                logger.info(f"An error occurred: {e}")
                return False
