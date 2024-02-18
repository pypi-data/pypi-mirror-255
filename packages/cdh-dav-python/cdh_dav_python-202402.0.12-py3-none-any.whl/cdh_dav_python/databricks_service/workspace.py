import requests
import os
import json
import requests
import sys, os


OS_NAME = os.name
sys.path.append("../..")

# spark
from pyspark.sql import SparkSession

from cdh_dav_python.cdc_admin_service.environment_logging import LoggerSingleton


# Get the currently running file name
NAMESPACE_NAME = os.path.basename(os.path.dirname(__file__))
# Get the parent folder name of the running file
SERVICE_NAME = os.path.basename(__file__)


class Workspace:
    @classmethod
    def list_workspaces(
        cls,
        token,
        databricks_instance_id,
    ):
        """
        Retrieves a list of workspaces from the Databricks workspace API.

        Args:
            cls: The class object.
            token (str): The access token for authentication.
            databricks_instance_id (str): The ID of the Databricks instance.

        Returns:
            dict: A JSON response containing the list of workspaces.
        """
        running_local = ("dbutils" in locals() or "dbutils" in globals()) is not True

        if running_local is True:
            spark = SparkSession.builder.appName("cdc_data_ecosystem").getOrCreate()

        api_url = "https://<YOUR-DATABRICKS-WORKSPACE-URL>"
        TOKEN = "Bearer <YOUR-ACCESS-TOKEN>"

        headers = {
            "Authorization": TOKEN,
        }

        response = requests.get(
            f"{BASE_URL}/api/2.0/workspace/list",
            headers=headers,
            params={"path": "/"},  # List the root directory
            timeout=60,  # Add a timeout argument to prevent indefinite hanging
        )

        if response.status_code == 200:
            print(response.json())
        else:
            print("Failed to list workspaces:", response.content)

        return response.json()
