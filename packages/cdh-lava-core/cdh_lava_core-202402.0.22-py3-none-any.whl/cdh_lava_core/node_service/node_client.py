import os
import sys
import subprocess
import platform
import urllib.request
import tempfile

from cdh_lava_core.cdc_log_service.environment_logging import LoggerSingleton

# Get the currently running file name
NAMESPACE_NAME = os.path.basename(os.path.dirname(__file__))
# Get the parent folder name of the running file
SERVICE_NAME = os.path.basename(__file__)


class NodeClient:
    """
    A class representing a client for interacting with Node.
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
                    cls.install_node_windows()
                else:
                    print("This is not a Windows operating system.")

            except subprocess.CalledProcessError as ex:
                error_msg = "Error: %s", ex
                exc_info = sys.exc_info()
                LoggerSingleton.instance(
                    NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
                ).error_with_exception(error_msg, exc_info)
                raise

    @staticmethod
    def install_node_windows():
        """
        Installs Node.js and necessary dependencies on a Windows system.

        This function performs the following steps:
        1. Deactivates the virtual environment if necessary.
        2. Changes to the home directory.
        3. Uninstalls nodeenv.
        4. Downloads and installs a specific version of Node.js.
        5. Installs a specific version of npm if necessary.
        6. Installs nodeenv.
        7. Installs Mermaid CLI.
        8. Tests the installations by printing the Node.js version, npm version, and Mermaid CLI help.

        Note: Some steps may require administrative privileges.

        """

        tracer, logger = LoggerSingleton.instance(
            NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
        ).initialize_logging_and_tracing()

        with tracer.start_as_current_span("install_node_windows"):
            try:
                # Deactivate virtual environment if necessary
                # subprocess.call(["deactivate"], shell=True)

                # Change to the home directory
                os.chdir(os.path.expanduser("~"))

                # Uninstall nodeenv
                subprocess.call(["pip", "uninstall", "-y", "nodeenv"], shell=True)

                # Install Node.js (Requires manual download or a separate script to download and run the installer)
                # Node.js installation URL (change to the version you need)
                node_install_url = (
                    "https://nodejs.org/dist/v16.13.0/node-v16.13.0-x64.msi"
                )

                # Download Node.js installer
                with tempfile.NamedTemporaryFile(
                    delete=False, suffix=".msi"
                ) as tmp_file:
                    urllib.request.urlretrieve(node_install_url, tmp_file.name)
                    # Install Node.js (this will require administrative privileges)
                    subprocess.call(
                        ["msiexec", "/i", tmp_file.name, "/passive", "/norestart"],
                        shell=True,
                    )

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

            except Exception as ex:
                error_msg = "Error: %s", ex
                exc_info = sys.exc_info()
                LoggerSingleton.instance(
                    NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
                ).error_with_exception(error_msg, exc_info)
                raise
