from azure.identity import ClientSecretCredential, DeviceCodeCredential
from azure.keyvault.secrets import SecretClient
from azure.identity import DefaultAzureCredential, AzureDeveloperCliCredential
from azure.mgmt.resource import ResourceManagementClient
import azure.keyvault.secrets
import os
import sys

from cdh_lava_core.cdc_log_service.environment_logging import LoggerSingleton
from cdh_lava_core.az_key_vault_service.az_key_vault import AzKeyVault

# Get the currently running file name
NAMESPACE_NAME = os.path.basename(os.path.dirname(__file__))
# Get the parent folder name of the running file
SERVICE_NAME = os.path.basename(__file__)


class AwsCredential:
    """Wrapper class for Aws Credential to get secrets.

    This class authenticates with the Aws Credential using a service
    principal and provides a method to retrieve secrets.
    """

    # Get the currently running file name
    NAMESPACE_NAME = os.path.basename(os.path.dirname(__file__))
    # Get the parent folder name of the running file
    SERVICE_NAME = os.path.basename(__file__)

    def __init__(
        self,
        tenant_id,
        client_id,
        client_secret,
        key_vault_name,
        running_interactive,
        aws_access_key_id,
        aws_kv_secret_access_key,
        data_product_id,
        environment,
    ):
        tracer, logger = LoggerSingleton.instance(
            NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
        ).initialize_logging_and_tracing()

        with tracer.start_as_current_span("__init__"):
            try:
                obj_key_vault = AzKeyVault(
                    tenant_id,
                    client_id,
                    client_secret,
                    key_vault_name,
                    running_interactive,
                    data_product_id,
                    environment,
                )

                aws_secret_access_key = obj_key_vault.get_secret(
                    aws_kv_secret_access_key
                )

                os.environ["AWS_ACCESS_KEY_ID"] = aws_access_key_id
                os.environ["AWS_SECRET_ACCESS_KEY"] = aws_secret_access_key

                logger.info(
                    f"Successfully retrieved AWS credentials for {aws_access_key_id} from Key Vault"
                )

            except Exception as ex:
                error_msg = "Error: %s", ex
                exc_info = sys.exc_info()
                LoggerSingleton.instance(
                    NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
                ).error_with_exception(error_msg, exc_info)
                raise
