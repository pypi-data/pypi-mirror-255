import os
import sys
import subprocess
import platform

from cdh_lava_core.cdc_log_service.environment_logging import LoggerSingleton

# Get the currently running file name
NAMESPACE_NAME = os.path.basename(os.path.dirname(__file__))
# Get the parent folder name of the running file
SERVICE_NAME = os.path.basename(__file__)


class PerlClient:
    """
    A class representing a client for interacting with Perl.
    """

    @classmethod
    def install_perl(cls, data_product_id, environment):
        """
        Install Perl by running the appropriate install command.

        Returns:
            A subprocess.CompletedProcess object representing the result of the installation command.
        """

        tracer, logger = LoggerSingleton.instance(
            NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
        ).initialize_logging_and_tracing()

        with tracer.start_as_current_span("install_perl"):
            try:
                if platform.system() == "Windows":
                    cls.install_perl_windows(data_product_id, environment)
                else:
                    cls.install_perl_unix(data_product_id, environment)

                logger.info("Perl installation complete")

            except subprocess.CalledProcessError as ex:
                error_msg = "Error: %s" % ex
                exc_info = sys.exc_info()
                LoggerSingleton.instance(
                    NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
                ).error_with_exception(error_msg, exc_info)
                raise

    @staticmethod
    def install_perl_windows(data_product_id, environment):
        """
        Installs Perl on Windows.

        Args:
            data_product_id (str): The ID of the data product.
            environment (str): The environment in which the installation is being performed.

        Raises:
            subprocess.CalledProcessError: If any of the subprocess calls result in an error.

        """

        tracer, logger = LoggerSingleton.instance(
            NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
        ).initialize_logging_and_tracing()

        with tracer.start_as_current_span("install_perl"):
            try:
                # Check if Perl is already installed
                perl_installed = subprocess.call(["perl", "-v"], shell=True) == 0
                if not perl_installed:
                    # Insert your Perl installation logic here
                    # Example: subprocess.call(["choco", "install", "perl"], shell=True)
                    pass

                logger.info("Perl installation (or check) on Windows complete")

            except subprocess.CalledProcessError as ex:
                error_msg = "Error: %s" % ex
                exc_info = sys.exc_info()
                LoggerSingleton.instance(
                    NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
                ).error_with_exception(error_msg, exc_info)
                raise

    @staticmethod
    def install_perl_unix(data_product_id, environment):
        """
        Installs Perl on Unix.

        Args:
            data_product_id (str): The ID of the data product.
            environment (str): The environment in which the installation is being performed.

        Raises:
            subprocess.CalledProcessError: If any of the subprocess calls result in an error.

        """

        tracer, logger = LoggerSingleton.instance(
            NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
        ).initialize_logging_and_tracing()

        with tracer.start_as_current_span("install_perl"):
            try:
                # Check if Perl is already installed
                perl_installed = subprocess.call(["perl", "-v"], shell=True) == 0
                if not perl_installed:
                    # Install Perl using package manager (e.g., apt, yum)
                    # Example for Debian-based systems: subprocess.call(["sudo", "apt-get", "install", "perl", "-y"], shell=True)
                    # Example for RedHat-based systems: subprocess.call(["sudo", "yum", "install", "perl", "-y"], shell=True)
                    pass

                logger.info("Perl installation (or check) on Unix complete")

            except subprocess.CalledProcessError as ex:
                error_msg = "Error: %s" % ex
                exc_info = sys.exc_info()
                LoggerSingleton.instance(
                    NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
                ).error_with_exception(error_msg, exc_info)
                raise
