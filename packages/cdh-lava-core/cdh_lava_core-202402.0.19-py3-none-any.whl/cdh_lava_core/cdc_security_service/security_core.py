""" Module for security_core for cdc_security_service with minimal dependencies. """

import os, sys
from azure.core.exceptions import ClientAuthenticationError

# Import from sibling directory ..\cdc_tech_environment_service
OS_NAME = os.name

ENV_SHARE_FALLBACK_PATH = "/usr/local/share"

sys.path.append("..")
if OS_NAME.lower() == "nt":
    print("environment_logging: windows")
    sys.path.append(os.path.dirname(os.path.abspath(__file__ + "\\..")))
    sys.path.append(os.path.dirname(os.path.abspath(__file__ + "\\..\\..")))
    sys.path.append(os.path.dirname(os.path.abspath(__file__ + "\\..\\..\\..")))
    sys.path.append(os.path.dirname(os.path.abspath(sys.executable + "\\..\\share")))
else:
    print("environment_logging: non windows")
    sys.path.append(os.path.dirname(os.path.abspath(__file__ + "/..")))
    sys.path.append(os.path.dirname(os.path.abspath(__file__ + "/../..")))
    sys.path.append(os.path.dirname(os.path.abspath(__file__ + "/../../..")))
    env_path = os.path.dirname(os.path.abspath(sys.executable + "/.."))
    sys.path.append(os.path.dirname(os.path.abspath(sys.executable + "/../share")))


from cdh_lava_core.cdc_log_service.environment_logging import LoggerSingleton

from cdh_lava_core.cdc_tech_environment_service import (
    environment_file as cdc_env_file,
)

# core
import cdh_lava_core.cdc_log_service.environment_logging as cdh_env_log
from adal import AuthenticationContext
import requests
from html.parser import HTMLParser  # web scraping html
from azure.identity import ClientSecretCredential
import json
import traceback  # don't remove required for error handling
from distutils.log import error

sys.path.append(".")

# Get the currently running file name
NAMESPACE_NAME = os.path.basename(os.path.dirname(__file__))
# Get the parent folder name of the running file
SERVICE_NAME = os.path.basename(__file__)


class SecurityCore:
    """Security functions with minimal dependencies"""

    @classmethod
    def acquire_access_token_with_client_credentials(
        cls,
        sp_client_id: str,
        sp_client_secret: str,
        sp_tenant_id: str,
        sp_redirect_url: str,
        sp_authority_host_url: str,
        sp_azure_databricks_resource_id: str,
        data_product_id: str,
        environment: str,
    ) -> dict:
        """Takes in config dictionary, client_id and client secret and returns config_user with access_token
        - initial call

        Args:
            config (dict): global config dictionary
            sp_client_id (str): service principal client id
            sp_client_secret (str): service principal secret
            sp_tenant_id (str): service principal tenant id
            sp_redirect_url (str): service principal redirect url
            sp_azure_databricks_resource_id (str): service principal azure databricks resource id
            data_product_id(str): project id for logging

        Returns:
            dict: config_user dictionary with access_token populated
        """

        tracer, logger = LoggerSingleton.instance(
            NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
        ).initialize_logging_and_tracing()

        with tracer.start_as_current_span(
            "acquire_access_token_with_client_credentials"
        ):
            info_message = (
                f"acquire_access_token_with_client_credentials for {data_product_id}"
            )
            print(info_message)

            config_user = cls.setup_user_configuration(
                sp_client_id,
                sp_client_secret,
                sp_tenant_id,
                sp_redirect_url,
                sp_authority_host_url,
                sp_azure_databricks_resource_id,
                data_product_id,
                environment,
            )

            az_sub_oauth_token_endpoint = config_user["az_sub_oauth_token_endpoint"]
            azure_databricks_resource_id = config_user["azure_databricks_resource_id"]
            print(f"az_sub_oauth_token_endpoint:{az_sub_oauth_token_endpoint}")
            print(f"sp_client_id:{sp_client_id}")
            print(f"azure_databricks_resource_id:{azure_databricks_resource_id}")
            context = AuthenticationContext(az_sub_oauth_token_endpoint)

            token_response = {"accessToken": "not_set"}

            # resource='https://management.core.windows.net/'
            # resource = "https://database.windows.net/"

            # Get token using username password first
            try:
                token_response = context.acquire_token_with_client_credentials(
                    azure_databricks_resource_id,
                    sp_client_id,
                    sp_client_secret,
                )
            except Exception as ex_access_token_with_client_credentials:
                # Get current system exception
                ex_type, ex_value, ex_traceback = sys.exc_info()

                # Extract unformatter stack traces as tuples
                trace_back = traceback.extract_tb(ex_traceback)

                # Format stacktrace
                stack_trace = list()
                error_string = "Error: Unable to acquire_access_token_with_client_credentials with sp_client_id"
                error_string = (
                    error_string
                    + f":{sp_client_id}: Details: {str(ex_access_token_with_client_credentials)}"
                )
                error_string = error_string + ": Extended:"
                for trace in trace_back:
                    error_string = (
                        f"File : {trace[0]} , Line : {trace[1]}, Func.Name : {trace[2]}"
                    )
                    error_string = (
                        error_string + f", Message : {trace[3]}, Type : {ex_type}"
                    )
                    error_string = error_string + f", Value : {ex_value}"
                    stack_trace.append(error_string)
                logger.error(error_string)
            # self.validate_token_response_username_password(token_response)

            logger.info(
                f"token_response: [REDACTED]: length:{len(str(token_response))}"
            )
            # Use returned refresh token to acquire a new token.
            access_token = token_response["accessToken"]
            config_user["access_token"] = access_token

            return config_user

    @classmethod
    def acquire_access_token_with_refresh_token(
        cls,
        sp_client_id: str,
        sp_client_secret: str,
        sp_tenant_id: str,
        sp_redirect_url: str,
        sp_authority_host_url: str,
        sp_azure_databricks_resource_id: str,
        data_product_id: str,
        environment: str,
    ) -> dict:
        """Takes in config dictionary, client_id and client secret and returns config_user with access_token
        - refresh token call

        Args:
            config (dict): global config dictionary
            sp_client_id (str): service principal client id
            sp_client_secret (str): service principal secret

        Returns:
            dict: config_user with refresh_token populated
        """

        tracer, logger = LoggerSingleton.instance(
            NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
        ).initialize_logging_and_tracing()

        with tracer.start_as_current_span("acquire_access_token_with_refresh_token"):
            config_user = cls.setup_user_configuration(
                sp_client_id,
                sp_client_secret,
                sp_tenant_id,
                sp_redirect_url,
                sp_authority_host_url,
                sp_azure_databricks_resource_id,
                data_product_id,
                environment,
            )

            if config_user is None:
                print("config_user is None")
            else:
                print(f"config_user exists: {str(config_user)}")

            az_sub_oauth_token_endpoint = config_user["az_sub_oauth_token_endpoint"]
            # client_id = config_user['client_id']
            azure_databricks_resource_id = config_user["azure_databricks_resource_id"]
            logger.info(
                f"creating context for az_sub_oauth_token_endpoint:{az_sub_oauth_token_endpoint}"
            )
            context = AuthenticationContext(az_sub_oauth_token_endpoint)
            if context is None:
                logger.info(
                    f"AuthenticationContext: None : not acquired for az_sub_oauth_token_endpoint:{az_sub_oauth_token_endpoint}"
                )
            elif len(str(context)) == 0:
                logger.info(
                    f"AuthenticationContext: empty string : not acquired for az_sub_oauth_token_endpoint:{az_sub_oauth_token_endpoint}"
                )
            else:
                logger.info(
                    f"AuthenticationContext acquired for az_sub_oauth_token_endpoint:{az_sub_oauth_token_endpoint}"
                )

            user_id = "zfi4@cdc.gov"  # TO DO MAKE Configurable
            logger.info(
                f"attempting to acquire token for azure_databricks_resource_id:{azure_databricks_resource_id}"
            )
            token_response = context.acquire_token(
                azure_databricks_resource_id, user_id, sp_client_id
            )

            if token_response is None:
                logger.info(f"token_response not found:{str(token_response)}")
                config_user["refresh_token"] = "error"
            else:
                t_s = f"acquired token_response:{str(token_response)} for azure_databricks_resource_id"
                t_s = t_s + f":{str(azure_databricks_resource_id)}"
                refresh_token = token_response["refreshToken"]
                config_user["refresh_token"] = refresh_token

            config_user_result = cls.refresh_access_token(config_user)

            return config_user_result

    @staticmethod
    def setup_user_configuration(
        sp_client_id: str,
        sp_client_secret: str,
        sp_tenant_id: str,
        sp_redirect_url: str,
        sp_authority_host_url: str,
        sp_azure_databricks_resource_id: str,
        data_product_id: str,
        environment: str,
    ) -> dict:
        """Takes in a config dictionary, client_id and client_secret and returns populated config_user dictionary

        Args:
            config (dict): global config dictionary
            sp_client_id (str): service principal client id
            sp_client_secret (str): service principal client secret
            sp_tenant_id (str): service principal tenant id
            sp_redirect_url (str): service principal redirect url
            sp_authority_host_url (str): service principal authority host url
            sp_azure_databricks_resource_id (str): service principal azure databricks resource id

        Returns:
            dict: populated config_user dictionary
        """

        tracer, logger = LoggerSingleton.instance(
            NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
        ).initialize_logging_and_tracing()

        with tracer.start_as_current_span("setup_user_configuration"):
            sp_az_sub_oauth_token_endpoint = "".join(
                [sp_authority_host_url.rstrip("/"), "/", sp_tenant_id]
            )

            # todo change from check if all exist rather than any
            # client_secret_exists = coalesce(sp_tenant_id, sp_redirect_url, sp_client_id, sp_client_secret)

            # if (client_secret_exists is None):
            #    client_secret_exists = False

            config_user = {
                "tenant": sp_tenant_id,
                "client_id": sp_client_id,
                "redirect_uri": sp_redirect_url,
                "client_secret": sp_client_secret,
                "authority_host_url": sp_authority_host_url,
                "azure_databricks_resource_id": sp_azure_databricks_resource_id,
                "az_sub_oauth_token_endpoint": sp_az_sub_oauth_token_endpoint,
            }

            # print(f"config_user:{str(config_user)}")
            return config_user

    @staticmethod
    def refresh_access_token(
        config_user: dict, data_product_id: str, environment: str
    ) -> dict:
        """Takes in config_user dictionary, returns config_user with access and refresh token

        Args:
            config_user (dict): config_user dictionary

        Returns:
            dict: config_user dictionary populated with with refresh token
        """

        tracer, logger = LoggerSingleton.instance(
            NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
        ).initialize_logging_and_tracing()

        with tracer.start_as_current_span("refresh_access_token"):
            az_sub_oauth_token_endpoint = config_user["az_sub_oauth_token_endpoint"]
            client_id = config_user["client_id"]
            client_secret = config_user["client_secret"]
            refresh_token = config_user["refresh_token"]
            azure_databricks_resource_id = config_user["azure_databricks_resource_id"]

            context = AuthenticationContext(az_sub_oauth_token_endpoint)
            token_response = context.acquire_token_with_refresh_token(
                refresh_token,
                client_id,
                azure_databricks_resource_id,
                client_secret,
            )

            refresh_token = token_response["refreshToken"]
            access_token = token_response["accessToken"]

            config_user["refresh_token"] = refresh_token
            config_user["access_token"] = access_token

            print(str("config_user:{config_user}"))

            return config_user

    @staticmethod
    def get_pat_tokens(
        config: dict, token: str, data_product_id: str, environment: str
    ):
        """Takes in a config dictionary, token and base_path, returns populated list of pat tokens

        Args:
            config (dict): global config dictionary
            token (str): token

        Returns:
            list: list of pat tokens
        """

        tracer, logger = LoggerSingleton.instance(
            NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
        ).initialize_logging_and_tracing()

        with tracer.start_as_current_span("get_pat_tokens"):
            databricks_instance_id = config["databricks_instance_id"]
            headers = {"Authentication": f"Bearer {token}"}
            url = f"https://{databricks_instance_id}/api/2.0/preview/permissions/authorization/tokens"

            logger.info(f"url:{str(url)}")
            headers_redacted = str(headers).replace(token, "[bearer REDACTED]")
            logger.info(f"headers:{headers_redacted}")

            response = requests.get(url=url, headers=headers)
            data = None

            try:
                response_text = str(response.text)
                data = json.loads(response_text)
                msg = f"Received credentials with length : {len(str(response_text))} when posting to : "
                msg = msg + "{url}"
                response_text_fetch = msg
                logger.info("- response : success  -")
                logger.info.infot(f"{response_text_fetch}")
                results = data["access_control_list"]

            except Exception as exception_object:
                f_filter = HTMLFilter()
                f_filter.feed(response.text)
                response_text = f_filter.text
                print(f"- response : error - {exception_object}")
                print(f"Error converting response text:{response_text} to json")
                results = []

            return results

    @staticmethod
    def get_credentials_git(
        config: dict, token: str, data_product_id: str, environment: str
    ):
        """Takes in a config dictionary, token and base_path, returns populated list of files

        Args:
            config (dict): global config dictionary
            token (str): token
            base_path (str): path to list files

        Returns:
            list: list of files at the path location
        """

        tracer, logger = LoggerSingleton.instance(
            NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
        ).initialize_logging_and_tracing()

        with tracer.start_as_current_span("get_credentials_git"):
            databricks_instance_id = config["databricks_instance_id"]
            headers = {"Authentication": f"Bearer {token}"}
            url = f"https://{databricks_instance_id}/api/2.0/git-credentials"

            logger.info(f"url:{str(url)}")
            headers_redacted = str(headers).replace(token, "[bearer REDACTED]")
            logger.info(f"headers:{headers_redacted}")

            response = requests.get(url=url, headers=headers)
            data = None

            try:
                response_text = str(response.text)
                data = json.loads(response_text)
                msg = f"Received credentials with length : {len(str(response_text))} when posting to : "
                msg = msg + "{url}"
                response_text_fetch = msg
                print("- response : success  -")
                print(f"{response_text_fetch}")
                results = data["credentials"]

            except Exception as exception_object:
                f_filter = HTMLFilter()
                f_filter.feed(response.text)
                response_text = f_filter.text
                logger.info(f"- response : error - {exception_object}")
                logger.info(f"Error converting response text:{response_text} to json")
                results = []

            return results

    @staticmethod
    def verify_az_sub_client_secret(
        tenant_id: str,
        client_id: str,
        client_secret: str,
        data_product_id: str,
        environment: str,
    ):
        """
        Verifies the Azure subscription client secret.

        Args:
            tenant_id (str): The Azure tenant ID.
            client_id (str): The Azure client ID.
            client_secret (str): The Azure client secret.
            data_product_id (str): The ID of the data product.
            environment (str): The environment name.

        Returns:
            tuple: A tuple containing the status code and a message.
                The status code is 200 if the service principal password is valid,
                or 500 if it is not valid.
                The message provides additional information about the status.
        """

        tracer, logger = LoggerSingleton.instance(
            NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
        ).initialize_logging_and_tracing()

        with tracer.start_as_current_span("verify_az_sub_client_secret"):
            credential = ClientSecretCredential(tenant_id, client_id, client_secret)

            try:
                logger.info("Attempting to get token with service principal password.")
                logger.info(f"tenant_id:{tenant_id}")
                logger.info(f"client_id:{client_id}")
                logger.info(f"client_secret_length:{len(client_secret)}")
                token = credential.get_token("https://management.azure.com/.default")
                # NOTE LOGIN resource does not work to validate service principal password
                # credential.get_token("https://login.microsoftonline.com")
                logger.info(f"token:{token}")
                logger.info("Service principal password is valid.")
                return 200, "Service principal password is valid."

            except ClientAuthenticationError as e:
                # Log more specific details about the error
                error_message = f"Service principal password is not valid. Error: {e}"
                logger.error(error_message)
                # Include stack trace in debug level
                logger.debug(e, exc_info=True)
                return 500, error_message

            except Exception as e:
                # Handle other exceptions that might occur
                error_message = f"An unexpected error occurred: {e}"
                logger.error(error_message)
                logger.debug(e, exc_info=True)
                return 500, error_message

    @staticmethod
    def set_credentials_git(
        config: dict, token: str, data_product_id: str, environment: str
    ):
        """Takes in a config dictionary, token and base_path, returns populated list of files

        Args:
            config (dict): global config dictionary
            token (str): token
            base_path (str): path to list files

        Returns:
            list: list of files at the path location
        """

        tracer, logger = LoggerSingleton.instance(
            NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
        ).initialize_logging_and_tracing()

        with tracer.start_as_current_span("set_credentials_git"):
            databricks_instance_id = config["databricks_instance_id"]
            headers = {"Authentication": f"Bearer {token}"}
            url = f"https://{databricks_instance_id}/api/2.0/git-credentials"

            logger.info(f"url:{str(url)}")
            headers_redacted = str(headers).replace(token, "[bearer REDACTED]")
            logger.info(f"headers:{headers_redacted}")

            response = requests.get(url=url, headers=headers)
            data = None

            try:
                response_text = str(response.text)
                data = json.loads(response_text)
                msg = f"Received credentials with length : {len(str(response_text))} when posting to : "
                msg = msg + "{url}"
                response_text_fetch = msg
                logger.info("- response : success  -")
                logger.info(f"{response_text_fetch}")
                results = data["credentials"]

            except Exception as exception_object:
                f_filter = HTMLFilter()
                f_filter.feed(response.text)
                response_text = f_filter.text
                logger.error(f"- response : error - {exception_object}")
                logger.error(f"Error converting response text:{response_text} to json")
                results = []

            return results


class HTMLFilter(HTMLParser):
    """Parses HTMLData

    Args:
        HTMLParser (_type_): _description_
    """

    text = ""

    def handle_data(self, data):
        """Parses HTMLData

        Args:
            data (_type_): _description_

        Returns:
            None
        """
        self.text += data
