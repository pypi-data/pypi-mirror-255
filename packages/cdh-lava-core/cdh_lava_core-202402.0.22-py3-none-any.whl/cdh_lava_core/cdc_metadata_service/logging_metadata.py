"""Module to log warning, debug, error and info messages based on project metadata
"""
import sys
import os

import cdh_lava_core.cdc_log_service.environment_logging as davt_env_log


class LoggingMetaData:
    """
    Class to log warning, debug, error and info messages based on project metadata
    """

    @staticmethod
    def log_debug(config: dict, message):
        """Log debug message."""
        data_product_id = config["data_product_id"]
        environment = config["environment"]
        data_product_id_env = f"{data_product_id}_{environment}"
        data_product_id_env = data_product_id_env.upper()
        instrumentation_key = config["davt_python_app_insights_key"]
        obj_log_core = davt_env_log.EnvironmentLogging()
        obj_log_core.log_debug(
            data_product_id_env, message, instrumentation_key
        )

    @staticmethod
    def log_warning(config: dict, message):
        """Log warning message."""
        obj_env_log = davt_env_log.EnvironmentLogging()
        data_product_id = config["data_product_id"]
        environment = config["environment"]
        data_product_id_env = f"{data_product_id}_{environment}"
        data_product_id_env = data_product_id_env.upper()
        instrumentation_key = config["davt_python_app_insights_key"]
        obj_env_log.log_warning(
            data_product_id_env, message, instrumentation_key
        )

    @staticmethod
    def log_info(config, message):
        """Log info message."""
        obj_env_log = davt_env_log.EnvironmentLogging()
        data_product_id = config["data_product_id"]
        environment = config["environment"]
        data_product_id_env = f"{data_product_id}_{environment}"
        data_product_id_env = data_product_id_env.upper()
        instrumentation_key = config["davt_python_app_insights_key"]
        obj_env_log.log_info(data_product_id_env, message, instrumentation_key)

    @staticmethod
    def log_error(config, message):
        """Log debug message."""
        obj_env_log = davt_env_log.EnvironmentLogging()
        data_product_id = config["data_product_id"]
        environment = config["environment"]
        data_product_id_env = f"{data_product_id}_{environment}"
        data_product_id_env = data_product_id_env.upper()
        instrumentation_key = config["davt_python_app_insights_key"]
        obj_env_log.log_error(
            data_product_id_env, message, instrumentation_key
        )
