import base64

from azure.identity import DefaultAzureCredential
from azure.storage.queue import QueueClient

from shared_code import app_config


def send_message_to_queue(queue_name: str, message: str):
    default_credential = DefaultAzureCredential()
    queue_client = QueueClient.from_queue_url(
                queue_url=f"{app_config.QUEUE_STORAGE_CONNECTION_STRING}/{queue_name}",
                credential=default_credential
            )
    message_bytes = message.encode('utf-8')
    base64_bytes = base64.b64encode(message_bytes)
    base64_message = base64_bytes.decode('utf-8')
    queue_client.send_message(base64_message)

