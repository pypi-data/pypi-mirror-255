import os

TENANT_ID = os.getenv("AZURE_TENANT_ID")
CLIENT_ID = os.getenv("az_sub_client_id")
CLIENT_SECRET = os.getenv("AZURE_CLIENT_SECRET")

WORKFLOW_IN_PROGRESS_DIRECTORY = "work/datahub/inprogress"

WORKFLOW_STATUS_PENDING_APPROVAL = "PendingApproval"


EDAV_STORAGE_CDH_CONTAINER_URL = (
    f'https://{os.getenv("EDAV_STORAGE_ACCOUNT_NAME")}.dfs.core.windows.net/cdh'
)

DATABRICKS_TOKEN = os.getenv("DATABRICKS_TOKEN")
DATABRICKS_SERVER_HOSTNAME = os.getenv("DATABRICKS_SERVER_HOSTNAME")
DATABRICKS_HTTP_PATH = os.getenv("DATABRICKS_HTTP_PATH")


QUEUE_ORCHESTRATOR_START_NAME = "cdh-orchestrator-workflow-start"
QUEUE_STORAGE_CONNECTION_STRING = os.getenv("QueueStorageUri__queueServiceUri")
