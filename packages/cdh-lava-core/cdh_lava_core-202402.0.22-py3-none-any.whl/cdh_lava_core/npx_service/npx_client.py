import os
import sys
import subprocess

from cdh_lava_core.cdc_log_service.environment_logging import LoggerSingleton

# Get the currently running file name
NAMESPACE_NAME = os.path.basename(os.path.dirname(__file__))
# Get the parent folder name of the running file
SERVICE_NAME = os.path.basename(__file__)


class NpxClient:
    @staticmethod
    def generate_changelog(
        data_product_id: str = "wonder_metadata", environment: str = "dev"
    ):
        """Generates the changelog using conventional-changelog."""

        tracer, logger = LoggerSingleton.instance(
            NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
        ).initialize_logging_and_tracing()

        with tracer.start_as_current_span("generate_changelog"):
            try:
                # Change to the home directory
                # os.chdir(os.path.expanduser("~"))

                # Uninstall nodeenv
                subprocess.run(
                    "npx conventional-changelog -p angular -i CHANGELOG.md -s",
                    shell=True,
                )

                logger.info("Successfully generated the changelog.")

            except subprocess.CalledProcessError as ex:
                error_msg = "Error: %s", ex
                exc_info = sys.exc_info()
                LoggerSingleton.instance(
                    NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
                ).error_with_exception(error_msg, exc_info)
                raise
