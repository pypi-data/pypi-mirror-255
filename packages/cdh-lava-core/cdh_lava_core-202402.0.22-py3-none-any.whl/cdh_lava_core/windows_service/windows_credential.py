import os
import win32cred

from azure.storage.queue import QueueServiceClient
from azure.identity import ClientSecretCredential
from cdh_lava_core.cdc_log_service.environment_logging import LoggerSingleton

# Get the currently running file name
NAMESPACE_NAME = os.path.basename(os.path.dirname(__file__))
# Get the parent folder name of the running file
SERVICE_NAME = os.path.basename(__file__)


class WindowsCredential:
    def list_credentials():
        """
        Retrieves a list of credentials from the Windows Credential Manager.

        Returns:
            A list of dictionaries representing the credentials.
            Each dictionary contains the following keys:
            - 'TargetName': The name of the credential target (e.g., website, application).
            - 'UserName': The username associated with the credential.
            - 'CredentialBlob': The encrypted password or credential information.
        """
        creds = []
        try:
            # Enumerate credentials from the Windows Credential Manager
            creds = win32cred.CredEnumerate(None, win32cred.CRED_TYPE_GENERIC)
        except Exception as e:
            print(f"Error retrieving credentials: {str(e)}")

        return creds

    def get_credential_by_address(target_address):
        """
        Retrieves a credential from the Windows Credential Manager based on the target address.

        Args:
            target_address (str): The network address for which to retrieve the credential.

        Returns:
            dict or None: A dictionary representing the credential if found, containing the following keys:
                - 'TargetName': The name of the credential target (e.g., website, application).
                - 'UserName': The username associated with the credential.
                - 'CredentialBlob': The encrypted password or credential information.
                Returns None if no matching credential is found.
        """
        try:
            creds = win32cred.CredEnumerate(None, win32cred.CRED_TYPE_GENERIC)
            for cred in creds:
                if target_address.lower() in cred["TargetName"].lower():
                    return cred
        except Exception as e:
            print(f"Error retrieving credentials: {str(e)}")

        return None
