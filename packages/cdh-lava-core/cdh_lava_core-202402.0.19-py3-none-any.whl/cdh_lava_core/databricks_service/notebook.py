"""
This module contains the implementation of a Databricks notebook class and related functions.

The module includes the following classes:
- Notebook: A class representing a Databricks notebook.

The module includes the following functions:
- fix_file_path_if_windows: Fixes the file path for Windows OS by normalizing backslashes and forward slashes.
- run_notebook: Run a Databricks notebook using the Databricks REST API.
"""

import sys
import os


OS_NAME = os.name
sys.path.append("../..")

if OS_NAME.lower() == "nt":
    print("environment_logging: windows")
    sys.path.append(os.path.dirname(os.path.abspath(__file__ + "\\..")))
    sys.path.append(os.path.dirname(os.path.abspath(__file__ + "\\..\\..")))
    sys.path.append(os.path.dirname(os.path.abspath(__file__ + "\\..\\..\\..")))
else:
    print("environment_logging: non windows")
    sys.path.append(os.path.dirname(os.path.abspath(__file__ + "/..")))
    sys.path.append(os.path.dirname(os.path.abspath(__file__ + "/../..")))
    sys.path.append(os.path.dirname(os.path.abspath(__file__ + "/../../..")))

from cdh_lava_core.cdc_log_service.environment_logging import LoggerSingleton
from cdh_lava_core.cdc_tech_environment_service.environment_http import EnvironmentHttp

# Get the currently running file name
NAMESPACE_NAME = os.path.basename(os.path.dirname(__file__))
# Get the parent folder name of the running file
SERVICE_NAME = os.path.basename(__file__)


class Notebook:
    """
    A class representing a Databricks notebook.

    Methods:
    - run_notebook: Run a Databricks notebook using the Databricks REST API.
    """

    @staticmethod
    def fix_file_path_if_windows(path):
        """
        Fixes the file path for Windows OS by normalizing backslashes and forward slashes.

        Args:
        path (str): The file path to be fixed.

        Returns:
        str: The normalized file path for Windows, or the original path for other OS.
        """
        # Check if the operating system is Windows
        if os.name == "nt":
            # Normalize the path by replacing backslashes with forward slashes
            normalized_path = path.replace("\\", "/")

            # Further normalize using os.path.normpath to handle any other irregularities
            return os.path.normpath(normalized_path)
        else:
            # If not Windows, return the original path
            return path

    @classmethod
    def run_notebook(
        cls,
        token,
        databricks_instance_id,
        cdh_databricks_cluster,
        notebook_path,
        parameters,
        data_product_id,
        environment,
    ):
        """
        Run a Databricks notebook using the Databricks REST API.

        Parameters:
        - dbx_pat_token (str): Databricks personal access token.
        - databricks_instance_id (str): URL of the Databricks instance.
        - cdh_databricks_cluster (str): ID of the Databricks cluster to run the notebook.
        - notebook_path (str): Path to the notebook in the Databricks workspace.
        - parameters (dict): Dictionary of notebook parameters.

        Returns:
        - response (dict): The JSON response from the Databricks API.
        """
        tracer, logger = LoggerSingleton.instance(
            NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
        ).initialize_logging_and_tracing()

        with tracer.start_as_current_span("run_notebook"):
            try:
                bearer = "Bearer " + token
                api_url = f"https://{databricks_instance_id}/api/2.0/jobs/runs/submit"
                logger.info(
                    f"- Attempting run_notebook for query_name:{notebook_path} url:{str(api_url)} ----"
                )

                headers = {
                    "Authorization": f"{bearer}",
                    "Content-Type": "application/json",
                }

                headers_redacted = str(headers).replace(bearer, "[bearer REDACTED]")
                logger.info(f"Headers: {headers_redacted}")

                obj_http = EnvironmentHttp()
                notebook_path = obj_http.fix_url_slashes(notebook_path)

                payload = {
                    "run_name": "Databricks Notebook Run",
                    "existing_cluster_id": cdh_databricks_cluster,
                    "notebook_task": {
                        "notebook_path": notebook_path,
                        "base_parameters": parameters,
                    },
                }

                try:
                    obj_http = EnvironmentHttp()

                    response = obj_http.post(
                        api_url,
                        headers,
                        120,
                        data_product_id,
                        environment,
                        json=payload,  # Use 'json' instead of 'payload' to ensure proper JSON formatting
                    )

                    if response.status_code == 200:
                        logger.info("run_notebook API call successful.")
                        logger.info(f"Response: {response.json()}")
                        return response.json()
                    else:
                        error_msg = f"Error in API call to {api_url} with json:{payload} : {response.status_code} {response.text}"
                        logger.error(error_msg)
                        response.raise_for_status()
                except Exception as ex:
                    error_msg = f"Error: {ex}"
                    exc_info = sys.exc_info()
                    LoggerSingleton.instance(
                        NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
                    ).error_with_exception(error_msg, exc_info)
                    raise

            except Exception as ex:
                error_msg = "Error: %s", ex
                exc_info = sys.exc_info()
                LoggerSingleton.instance(
                    NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
                ).error_with_exception(error_msg, exc_info)
                raise
