import os
from datetime import datetime
import requests
import sys
from opentelemetry import trace
from dotenv import load_dotenv, set_key, dotenv_values

from cdh_lava_core.cdc_log_service.environment_logging import LoggerSingleton

 


from cdh_lava_core.az_key_vault_service import (
    az_key_vault as cdh_az_key_vault,
)


# Get the currently running file name
NAMESPACE_NAME = os.path.basename(os.path.dirname(__file__))
# Get the parent folder name of the running file
SERVICE_NAME = os.path.basename(__file__)
TIMEOUT_SECONDS = 30


class EdcAlationTokenError(Exception):
    def __init__(self, message):
        super().__init__(message)


class TokenEndpoint:
    def __init__(self, base_url):
        """
        Creates a TokenEndpoint object

        Parameters
        ----------
        base_url: string
            The root URL for the Alation server to use. It should not have a slash "/" at the end of the URL.
            Example: https://edc.cdc.gov
        """
        self.base_url = base_url

    REFRESH_TOKEN_ENDPOINT = "/integration/v1/validateRefreshToken/"
    API_TOKEN_ENDPOINT = "/integration/v1/createAPIAccessToken/"

    def get_api_token_from_config(self, config):
        """Retrieves the API access token from a configuration dictionary.

        The function fetches various configuration values from the input dictionary,
        including Azure subscription details and Key Vault secrets, to create an Azure
        Key Vault client and fetch the Alation refresh token. The API access token is then
        generated using the TokenEndpoint and the relevant Alation details.

        Args:
            config (dict): A dictionary containing necessary configuration values,
            such as Azure subscription details, Key Vault name, Key Vault secret keys,
            and Alation base URL.

        Returns:
            tuple: A tuple containing the status code and either the API access token or an error message.
        """

        data_product_id = config.get("data_product_id")
        environment = config.get("environment")
        
        tracer, logger = LoggerSingleton.instance(
            NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
        ).initialize_logging_and_tracing()

        with tracer.start_as_current_span("get_api_token_from_config"):
            try:
                edc_alation_base_url = config.get("edc_alation_base_url")
                edc_alation_user_id = config.get("edc_alation_user_id")
                az_sub_tenant_id = config.get("az_sub_tenant_id")
                az_sub_client_id = config.get("az_sub_client_id")
                az_kv_key_vault_name = config.get("az_kv_key_vault_name")
                az_sub_client_secret_key = config.get("az_sub_client_secret_key")
                az_sub_client_secret_key = az_sub_client_secret_key.replace("-", "_")
                client_secret = os.getenv(az_sub_client_secret_key)
                logger.info(f"az_sub_client_secret_key:{az_sub_client_secret_key}")
                logger.info(f"az_sub_client_id:{az_sub_client_id}")

                # Initialize running_interactive as False
                running_interactive = False

                # Check if the client_secret is None or a zero-length string
                if not client_secret:
                    running_interactive = True
                else:
                    # Trim leading and trailing whitespace from client_secret
                    client_secret = client_secret.strip()

                az_key_vault = cdh_az_key_vault.AzKeyVault(
                    az_sub_tenant_id,
                    az_sub_client_id,
                    client_secret,
                    az_kv_key_vault_name,
                    running_interactive,
                    data_product_id,
                    environment,
                )
                cdh_alation_refresh_secret_key = config.get(
                    "cdh_alation_refresh_secret_key"
                )
                logger.info(
                    f"cdh_alation_refresh_secret_key: {cdh_alation_refresh_secret_key}"
                )
                logger.info(
                    f"cdh_alation_refresh_secret_key_length:{str(len(cdh_alation_refresh_secret_key))}"
                )
                cdh_databricks_kv_scope = config.get("cdh_databricks_kv_scope")
                alation_refresh_token = az_key_vault.get_secret(
                    cdh_alation_refresh_secret_key, cdh_databricks_kv_scope
                )
                edc_alation_api_token = self.get_api_token(
                    edc_alation_base_url,
                    edc_alation_user_id,
                    alation_refresh_token,
                )

                logger.info(
                    f"edc_alation_api_access_token_length: {len(edc_alation_api_token)}"
                )
                status_code = 200
                return (
                    status_code,
                    edc_alation_api_token,
                    alation_refresh_token,
                )
            except Exception as ex:
                error_msg = (f"Error: {str(ex)}",)
                exc_info = sys.exc_info()
                LoggerSingleton.instance(
                    NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
                ).error_with_exception(error_msg, exc_info)
                raise

    def validate_api_token(self, edc_alation_base_url, edc_alation_api_token, user_id):
        """
        Validates an API token in Alation.

        Args:
            api_token: The API token to validate.
            user_id: The user ID associated with the API token.

        Returns:
            True if the token is valid, False otherwise.
        """

        tracer, logger = LoggerSingleton.instance(
            NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
        ).initialize_logging_and_tracing()

        with tracer.start_as_current_span("validate_api_token"):
            api_url = f"{edc_alation_base_url}/integration/v1/validateAPIAccessToken/"
            data = {
                "api_access_token": edc_alation_api_token,
                "user_id": user_id,
            }

            response_validation = requests.post(api_url, data=data)

            if response_validation.status_code == 200:
                response_validation_json = response_validation.json()
                token_status = response_validation_json.get(
                    "token_status", "invalid"
                ).lower()
                token_expires_at = response_validation_json.get(
                    "token_expires_at"
                ).split("T")[0]
                if token_status == "active":
                    print("INFO: Alation Refresh token is valid")
                    print("Token will expire on " + token_expires_at)
                    # Regenerate token if expires within 7 days
                    if token_expires_at:
                        days_to_expiration = abs(
                            datetime.strptime(token_expires_at, "%Y-%m-%d")
                            - datetime.now()
                        ).days
                        if days_to_expiration < 7:
                            logger.info(
                                "Alation Refresh Token will expire in "
                                + str(days_to_expiration)
                                + " days. Please create a new refresh token and replace the Pipeline API Token Variable."
                            )

                    elif token_status == "expired":
                        raise EdcAlationTokenError(
                            "ERROR: Alation Refresh Token has EXPIRED. Please create a new refresh token and replace the Pipeline API Token Variable."
                        )
                    else:
                        raise EdcAlationTokenError(
                            "ERROR: Alation Refresh Token is INVALID. Please create a new refresh token and replace the Pipeline API Token Variable."
                        )
                return days_to_expiration
            else:
                return_code = False

            return return_code

    def get_api_token(
        self,
        edc_alation_base_url,
        edc_alation_user_id,
        edc_alation_refresh_token,
    ):
        """
        Retrieves the API access token from an environment variable. If the token is not present or invalid,
        a new token is obtained and stored in the environment variable.

        Returns:
            str: The API access token.

        Raises:
            requests.HTTPError: If there is an error during the token retrieval process.
        """

        logger_singleton = cdh_env_logging.LoggerSingleton.instance(
            NAMESPACE_NAME, SERVICE_NAME
        )


        with tracer.start_as_current_span("get_api_token"):
            try:
                dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
                load_dotenv(dotenv_path)
                # Load environment variables from env file
                env_variables = dotenv_values(dotenv_path)
                # Check if the API access token is already stored in an environment variable
                edc_alation_api_token = env_variables.get("API_ACCESS_TOKEN")

                if edc_alation_api_token:
                    if self.validate_api_token(
                        edc_alation_base_url,
                        edc_alation_api_token,
                        edc_alation_user_id,
                    ):
                        # If the API access token exists and is valid, return it
                        return edc_alation_api_token

                new_api_access_token = self.create_api_access_token_via_refresh(
                    edc_alation_base_url,
                    edc_alation_user_id,
                    edc_alation_refresh_token,
                )

                # Update the environment variable with the new API access token
                set_key(dotenv_path, "API_ACCESS_TOKEN", new_api_access_token)
                load_dotenv(dotenv_path)

                return new_api_access_token
            except Exception as ex:
                error_msg = "Error: %s", ex
                exc_info = sys.exc_info()
                LoggerSingleton.instance(
                    NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
                ).error_with_exception(error_msg, exc_info)
                raise

    def validate_refresh_token(self, user_id, refresh_token):
        """
        Confirms that a refresh token is valid and return the number of days until
        the token expires.

        The function will cause the interpreter to exit if the token is invalid.

        Parameters
        ----------
        user_id: int
            The ID of the user obtaining the API access token
        refresh_token: string
            A valid refresh token from the user

        Returns
        -------
        int
            The number of days until the refresh token expires.
        """

        days_to_expiration = None
        token_data = {"refresh_token": refresh_token, "user_id": user_id}
        response = requests.post(
            "{base_url}{refresh}".format(
                base_url=self.base_url, refresh=self.REFRESH_TOKEN_ENDPOINT
            ),
            data=token_data,
            verify=True,
            timeout=30,
        )
        response.raise_for_status()
        json_body = response.json()
        token_status = json_body.get("token_status", "invalid").lower()
        token_expires_at = json_body.get("token_expires_at").split("T")[0]
        if token_status == "active":
            print("INFO: Alation Refresh token is valid")
            print("Token will expire on " + token_expires_at)
            # Regenerate token if expires within 7 days
            if token_expires_at:
                days_to_expiration = abs(
                    datetime.strptime(token_expires_at, "%Y-%m-%d") - datetime.now()
                ).days
                if days_to_expiration < 7:
                    print(
                        "Alation Refresh Token will expire in "
                        + str(days_to_expiration)
                        + " days. Please create a new refresh token and replace the Pipeline API Token Variable."
                    )
                    sys.exit(
                        "Alation Refresh Token expiring in "
                        + str(days_to_expiration)
                        + " days."
                    )

            elif token_status == "expired":
                print(
                    "ERROR: Alation Refresh Token has EXPIRED. Please create a new refresh token and replace the Pipeline API Token Variable."
                )
                sys.exit("Expired Alation Refresh Token.")
            else:
                print(
                    "ERROR: Alation Refresh Token is INVALID. Please create a new refresh token and replace the Pipeline API Token Variable."
                )
                sys.exit("Invalid Alation Refresh Token.")
        return days_to_expiration

    @classmethod
    def getAPIToken(cls, alation_refresh_token, alation_user_id, alation_url):
        """Obtains an API token from Alation using a refresh token, user ID, and Alation URL.

        Args:
            alation_refresh_token (str): A refresh token obtained from Alation.
            alation_user_id (str): The user ID associated with the refresh token.
            alation_url (str): The URL of the Alation instance to connect to.

        Raises:
            Exception: If there is an error obtaining the API token.

        Returns:
            str: The API token.
        """

        tracer, logger = LoggerSingleton.instance(
            NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
        ).initialize_logging_and_tracing()

        with tracer.start_as_current_span(f"getAPIToken"):
            logger.info(
                f"Getting API token with {alation_refresh_token} refresh token for user {alation_user_id}"
            )
            token_data = {
                "refresh_token": alation_refresh_token,
                "user_id": alation_user_id,
            }
            alation_access_token = ""
            token_status = ""
            token_expires_at = None
            logger.info(f"user_id: {alation_user_id}")
            logger.info(f"refresh_token_length: {str(len(alation_refresh_token))}")
            try:
                token_r = requests.post(
                    "{base_url}/integration/v1/validateRefreshToken/".format(
                        base_url=alation_url
                    ),
                    data=token_data,
                    verify=False,
                    timeout=30,
                ).json()
                token_status = token_r.get("token_status", "invalid").lower()
                token_expires_at = token_r.get("token_expires_at").split("T")[0]
            except Exception as e:
                logger.error("Error in Alation refresh token validation request.")
                logger.error("ERROR : " + str(e))
                raise e

            if token_status == "active":
                logger.info("INFO: Alation Refresh token is valid")
                logger.info("Token will expire on " + token_expires_at)
                # Regenerate token if expires within 7 days
                if token_expires_at:
                    days_to_expiration = abs(
                        datetime.strptime(token_expires_at, "%Y-%m-%d") - datetime.now()
                    ).days
                    if days_to_expiration < 7:
                        logger.info(
                            "Alation Refresh Token will expire in "
                            + str(days_to_expiration)
                            + " days. Please create a new refresh token and replace the Pipeline API Token Variable."
                        )
                        sys.exit(
                            "Alation Refresh Token expiring in "
                            + str(days_to_expiration)
                            + " days."
                        )

                    try:
                        access_token_r = requests.post(
                            "{base_url}/integration/v1/createAPIAccessToken/".format(
                                base_url=alation_url
                            ),
                            data=token_data,
                            verify=True,
                            timeout=30,
                        ).json()
                        alation_access_token = access_token_r.get(
                            "edc_alation_api_token"
                        )
                        logger.info(
                            "Alation API access token created is {alation_access_token}"
                        )
                    except Exception as ex_access_token_request:
                        logger.error("Error in Alation access token request.")
                        logger.error(f"ERROR : {str(ex_access_token_request)}")
            elif token_status == "expired":
                logger.error(
                    "ERROR: Alation Refresh Token has EXPIRED. Please create a new refresh token and replace the Pipeline API Token Variable."
                )
                sys.exit("Expired Alation Refresh Token.")
            else:
                logger.error(
                    "ERROR: Alation Refresh Token is INVALID. Please create a new refresh token and replace the Pipeline API Token Variable."
                )
                sys.exit("Invalid Alation Refresh Token.")

            # 0.1 Create the Authorization headers with the API_TOKEN
            alation_headers = {
                "Accept": "application/json",
                "Content-Type": "application/json",
                "Token": alation_access_token,
                "token": alation_access_token,
            }

            return alation_access_token, alation_headers

    # Won't work for CDC because we use SSO
    @staticmethod
    def create_alation_refresh_token(config):
        
        data_product_id = config.get("data_product_id")
        environment = config.get("environment")
        
        tracer, logger = LoggerSingleton.instance(
            NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
        ).initialize_logging_and_tracing()

        with tracer.start_as_current_span(f"create_alation_refresh_token"):
            edc_alation_base_url = config.get("edc_alation_base_url")
            az_kv_edc_client_secret_key = config.get("az_kv_edc_client_secret_key")
            az_kv_edc_env_var = az_kv_edc_client_secret_key.replace("-", "_")
            edc_alation_client_id = config.get("edc_alation_client_id")

            # Retrieve the value of the environment variable
            edc_alation_client_secret = os.getenv(az_kv_edc_env_var)
            api_url = "/integration/v1/createRefreshToken/"
            data_product_id = config.get("data_product_id")
            # Replace email_address_here and password_here with your email and password
            data = {
                "username": edc_alation_client_id,
                "password": edc_alation_client_secret,
                "name": data_product_id,
            }

            # Get refresh token
            headers = {"Content-Type": "application/json"}
            response = requests.post(
                edc_alation_base_url + api_url, json=data, headers=headers
            )
            print(response.json())
            refresh_token = response.json()
            return refresh_token

    @staticmethod
    def create_api_access_token_via_refresh(
        edc_alation_base_url, edc_alation_user_id, edc_alation_refresh_token, data_product_id, environment
    ):
        """
        This function creates a new API access token using a refresh token.

        Args:
        edc_alation_base_url (str): The base URL of the Alation instance.
        edc_alation_user_id (str): The user ID for the Alation instance.
        edc_alation_refresh_token (str): The refresh token for the Alation instance.

        Returns:
        dict: The new API access token.
        """

        tracer, logger = LoggerSingleton.instance(
            NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
        ).initialize_logging_and_tracing()
        )
        tracer = tracer_singleton.get_tracer()

        with tracer.start_as_current_span("create_api_access_token_via_refresh"):
            auth_url = edc_alation_base_url + "/integration/v1/createAPIAccessToken/"
            data = {
                "refresh_token": edc_alation_refresh_token,
                "user_id": edc_alation_user_id,
            }
            headers = {"Content-Type": "application/json"}
            logger.info(f"auth_url: {auth_url}")
            logger.info(f"edc_refresh_token_length: {len(edc_alation_refresh_token)}")
            response_create_api_token = requests.post(
                auth_url, json=data, headers=headers
            )

            response_create_api_token.raise_for_status()

            edc_alation_api_token = "not_set"
            # Check the response status code to determine if the request was successful
            if response_create_api_token.status_code in (200, 201):
                # Extract the API token from the response
                response_create_api_token_json = response_create_api_token.json()
                logger.info(
                    f"response_data length: {len(response_create_api_token_json)}"
                )
                edc_alation_api_token = response_create_api_token_json.get(
                    "api_access_token"
                )
                logger.info(
                    f"Generated API response length: {len(edc_alation_api_token)}"
                )
            else:
                logger.error(
                    "Failed to generate API token:" + str(response_create_api_token)
                )

            return edc_alation_api_token

    @staticmethod
    def create_api_access_token_via_login(config):
        """
        This function generates an API access token via login using client credentials.
        It retrieves configuration information from the provided config object, including the base URL for the
        Alation instance, the client secret key and client ID. It then makes a POST request to the auth URL
        with these credentials to obtain the API token.

        Args:
            config (dict): A dictionary containing configuration information. Expected keys are
                        "edc_alation_base_url", "az_kv_edc_client_secret_key", and "edc_alation_client_id".
                        The values associated with these keys should be strings.

        Returns:
            str: The API token if the request is successful, "not_set" otherwise.
        """

        tracer, logger = LoggerSingleton.instance(
            NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
        ).initialize_logging_and_tracing()

        with tracer.start_as_current_span(f"create_api_access_token_via_login"):
            edc_alation_base_url = config.get("edc_alation_base_url")
            az_kv_edc_client_secret_key = config.get("az_kv_edc_client_secret_key")
            az_kv_edc_env_var = az_kv_edc_client_secret_key.replace("-", "_")
            edc_alation_client_id = config.get("edc_alation_client_id")

            # Retrieve the value of the environment variable
            edc_alation_client_secret = os.getenv(az_kv_edc_env_var)
            api_url = "/account/auth/"
            # Get refresh token
            auth_url = edc_alation_base_url + api_url
            print(f"edc_alation_client_id: {edc_alation_client_id}")
            print(f"edc_alation_client_secret: {edc_alation_client_secret}")
            print(f"auth_url: {auth_url}")
            response = requests.post(
                auth_url,
                auth=(edc_alation_client_id, edc_alation_client_secret),
            )

            api_token = "not_set"
            # Check the response status code to determine if the request was successful
            if response.status_code == 200:
                # Extract the API token from the response
                api_token = response.json()["api_token"]
                print(f"Generated API token: {api_token}")
            else:
                print("Failed to generate API token:" + str(response))

            return api_token

    @classmethod
    def get_edc_alation_api_access_token(
        cls,
        edc_alation_base_url,
        edc_alation_user_id,
        edc_alation_refresh_token,
    ):
        """Gets an API access token using the provided Alation base URL, user ID, and refresh token.

        This method sends a request to the Alation API to get an access token, which is then returned.

        Args:
            edc_alation_base_url (str): The base URL for the Alation instance.
            edc_alation_user_Id (str): The user ID for the Alation API.
            edc_alation_refresh_token (str): The refresh token to use when requesting an access token from the Alation API.

        Returns:
            str: The API access token.
        """

        tracer, logger = LoggerSingleton.instance(
            NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
        ).initialize_logging_and_tracing()

        with tracer.start_as_current_span(f"get_edc_alation_api_access_token"):
            api_token = cls.create_api_access_token_via_refresh(
                edc_alation_base_url,
                edc_alation_user_id,
                edc_alation_refresh_token,
            )
            return api_token
