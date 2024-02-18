import os
import sys
import json

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
from cdh_dav_python.databricks_service import workspace as databricks_workspace

from cdh_dav_python.cdc_metadata_service import environment_metadata as cdc_env_metadata

sys.path.append("..")

dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(dotenv_path)

ENVIRONMENT = "exploratory"


def get_config(parameters):
    """
    Retrieve the configuration based on the given parameters.

    Args:
        parameters (list or dict): The parameters used to determine the configuration.

    Returns:
        dict: The configuration retrieved based on the parameters.

    Raises:
        None

    Example:
        >>> params = [1, 2, 3]
        >>> get_config(params)
        {'param1': 1, 'param2': 2, 'param3': 3}
    """
    environment_metadata = cdc_env_metadata.EnvironmentMetaData()

    config = environment_metadata.get_configuration_common(parameters, None)

    return config


def test_get_workspaces():
    current_script_path = os.path.abspath(__file__)
    project_root = os.path.dirname(os.path.dirname(current_script_path))
    os.chdir(project_root)

    repository_path_default = str(Path(os.getcwd()))
    parameters = {
        "data_product_id": "cdh_premier_exploratory",
        "data_product_id_root": "cdh",
        "data_product_id_individual": "premier",
        "environment": "exploratory",
        "repository_path": repository_path_default,
    }
    config = get_config(parameters)

    # Call the function under test
    workspace_json = databricks_workspace.Workspace.list_workspaces(config)
