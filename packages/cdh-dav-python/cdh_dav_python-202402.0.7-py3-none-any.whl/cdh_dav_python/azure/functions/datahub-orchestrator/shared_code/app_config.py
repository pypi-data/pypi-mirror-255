import os
from datetime import datetime, timezone

START_WORKFLOW_EVENT_TYPE = "start_workflow"
UPDATE_WORKFLOW_EVENT_STATUS = "update_workflow_status"

EDAV_STORAGE_CDH_CONTAINER_NAME = "cdh"
EDAV_STORAGE_ACCOUNT_NAME = os.getenv("EDAV_STORAGE_ACCOUNT_NAME")
DMZ_STORAGE_ACCOUNT_NAME = os.getenv("DMZ_STORAGE_ACCOUNT_NAME")
EDAV_STORAGE_URL = (
    f'https://{os.getenv("EDAV_STORAGE_ACCOUNT_NAME")}.blob.core.windows.net/'
)
EDAV_STORAGE_CDH_CONTAINER_URL = (
    f'https://{os.getenv("EDAV_STORAGE_ACCOUNT_NAME")}.dfs.core.windows.net/cdh'
)
DMZ_STORAGE_CDH_CONTAINER_URL = (
    f'https://{os.getenv("DMZ_STORAGE_ACCOUNT_NAME")}.dfs.core.windows.net/cdh'
)
APP_ENVIRONMENT = os.getenv("APP_ENVIRONMENT", default="PROD")
GIT_BRANCH = os.getenv("GIT_BRANCH", default="main")

QUEUE_STORAGE_CONNECTION_STRING = os.getenv("QueueStorageUri__queueServiceUri")

TENANT_ID = os.getenv("AZURE_TENANT_ID")
CLIENT_ID = os.getenv("az_sub_client_id")
CLIENT_SECRET = os.getenv("AZURE_CLIENT_SECRET")

DATAFACTORY_URL = os.getenv("DATAFACTORY_URL")
DATAFACTORY_SUBSCRIPTION_ID = os.getenv("DATAFACTORY_SUBSCRIPTION_ID")
DATABRICKS_URL = os.getenv("DATABRICKS_URL")
DATABRICKS_TOKEN = os.getenv("DATABRICKS_TOKEN")
DATABRICKS_SERVER_HOSTNAME = os.getenv("DATABRICKS_SERVER_HOSTNAME")
DATABRICKS_HTTP_PATH = os.getenv("DATABRICKS_HTTP_PATH")

WORKFLOW_STATUS_RUNNING = "Running"
WORKFLOW_STATUS_SUCCEEDED = "Succeeded"
WORKFLOW_STATUS_FAILED = "Failed"
WORKFLOW_STATUS_REJECTED = "Rejected"
WORKFLOW_STATUS_RERUN = "Rerun"
WORKFLOW_STATUS_PENDING_APPROVAL = "PendingApproval"
WORKFLOW_STATUS_PENDING_SCHEDULE_EXPIRATION = "PendingScheduleExpiration"

DATAHUB_CONFIGS_LOCATION = "metadata/datahub/configs/"
DATAHUB_JOURNALS_LOCATION = "metadata/datahub/journals/"

DATAHUB_CONFIGS_FILE_SUFFIX = "_datahub_config.json"
DUPLICATE_JOURNAL_FILE_SUFFIX = "_pickedup_journal.json"

WORKFLOW_IN_PROGRESS_DIRECTORY = "work/datahub/inprogress"
WORKFLOW_COMPLETED_DIRECTORY = "work/datahub/completed"

EMAIL_NOTIFICATION_URL = os.getenv("EMAIL_NOTIFIER_URL")
ORCHESTRATION_COMPLETE_EMAIL_TO = os.getenv("ORCHESTRATION_COMPLETE_EMAIL_TO")
UNHANDLED_ERROR_EMAIL_TO = os.getenv("UNHANDLED_ERROR_EMAIL_TO")

QUEUE_OBSERVABILITY_LOGGING_NAME = "cdh-observability-logging"
QUEUE_ORCHESTRATOR_START_NAME = "cdh-orchestrator-workflow-start"
QUEUE_ORCHESTRATOR_UPDATE_NAME = "cdh-orchestrator-workflow-update"

DATABRICKS_NB_PATH_PREFIX = os.getenv(
    "DATABRICKS_NB_PATH_PREFIX", default="azure/databricks/etl/notebooks"
)

DATABRICKS_CLUSTER_CONFIG_PASSTHROUGH_DEFAULT = "default"
DATABRICKS_CLUSTER_CONFIG_NON_PASSTHROUGH = "non-pass-through-creds"


def get_events_save_location(data_source: str, workflow_id: str):
    return f"{WORKFLOW_COMPLETED_DIRECTORY}/{data_source}/{workflow_id}/events"
