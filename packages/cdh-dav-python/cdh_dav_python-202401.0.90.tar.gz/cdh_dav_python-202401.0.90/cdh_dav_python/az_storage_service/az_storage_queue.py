import os

from azure.storage.queue import QueueServiceClient
from azure.identity import ClientSecretCredential


# Get the currently running file name
NAMESPACE_NAME = os.path.basename(os.path.dirname(__file__))
# Get the parent folder name of the running file
SERVICE_NAME = os.path.basename(__file__)


class AzureStorageQueue:
    """A wrapper class for Azure Storage Queue service.

    This class provides convenient methods to interact with the Azure Storage Queue
    using a service principal for authentication.
    """

    def __init__(
        self, storage_account_url, queue_name, tenant_id, client_id, client_secret
    ):
        """Initializes the AzureStorageQueue object.

        Args:
            storage_account_url (str): The URL of your Azure Storage Account.
            queue_name (str): The name of the queue to interact with.
            tenant_id (str): The tenant ID of your Azure account. This is the directory ID.
            client_id (str): The client ID of the service principal.
            client_secret (str): The client secret of the service principal.
        """
        credential = ClientSecretCredential(tenant_id, client_id, client_secret)

        self.queue_service = QueueServiceClient(
            account_url=storage_account_url, credential=credential
        )
        self.queue_name = queue_name
        self.queue_service.create_queue()

    def enqueue_task(self, message):
        """Sends a new message to the Azure Storage Queue.

        Args:
            message (str): The message to add to the queue.
        """
        self.queue_service.send_message(message)

    def dequeue_task(self):
        """Retrieves a single message from the Azure Storage Queue.

        Returns:
            tuple: A tuple containing the content of the message, its ID, and its pop receipt,
            or None if no message is available.
        """
        messages = self.queue_service.receive_messages(num_messages=1)
        if messages:
            message = messages[0]
            return message.content, message.id, message.pop_receipt
        return None

    def delete_task(self, message_id, pop_receipt):
        """Deletes a message from the Azure Storage Queue.

        Args:
            message_id (str): The ID of the message to delete.
            pop_receipt (str): The pop receipt of the message to delete.
            This is returned by dequeue_task when retrieving the message.
        """
        self.queue_service.delete_message(message_id, pop_receipt)
