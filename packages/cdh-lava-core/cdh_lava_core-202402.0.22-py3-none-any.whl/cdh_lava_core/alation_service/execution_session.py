import os
import json
import requests

from cdh_lava_core.cdc_log_service.environment_logging import LoggerSingleton

# Get the currently running file name
NAMESPACE_NAME = os.path.basename(os.path.dirname(__file__))
# Get the parent folder name of the running file
SERVICE_NAME = os.path.basename(__file__)

TIMEOUT_5_SEC = 5
TIMEOUT_ONE_MIN = 60
# Get the currently running file name


class ExecutionSession:
    """
    Represents an execution session in the EDC Alation instance.
    """

    def get_execution_sessions(
        self,
        edc_alation_base_url: str,
        headers: str,
        data_product_id: str,
        environment: str,
    ):
        """
        Retrieves all execution sessions from the specified EDC Alation base URL.

        Args:
            edc_alation_base_url (str): The base URL of the EDC Alation instance.
            headers (str): The headers to be included in the request.
            data_product_id (str): The ID of the data product.
            environment (str): The environment in which the execution sessions are retrieved.

        Returns:
            None
        """

        tracer, logger = LoggerSingleton.instance(
            NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
        ).initialize_logging_and_tracing()

        with tracer.start_as_current_span("get_execution_sessions"):
            logger.info("##### Get all execution sessions #####")
            api_url = "/integration/v1/query/execution_session/"
            session_list_url = edc_alation_base_url + api_url
            response = requests.get(
                session_list_url, headers=headers, timeout=TIMEOUT_ONE_MIN
            )
            sessions = json.loads(response.text)
            for session in sessions:
                session_id = session["id"]
                client_session_id = session["client_session_id"]
                msg = f"ID: {session_id}, Client-session-ID: {client_session_id}"
                logger.info(msg)

            query_id = "249"
