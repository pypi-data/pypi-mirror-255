import os
import sys
import json
import pandas as pd

from pandas import json_normalize
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
from cdh_dav_python.cdc_metadata_service import (
    environment_metadata as cdc_env_metadata,
)
from cdh_dav_python.alation_service import (
    user as alation_user,
    token as alation_token_endpoint,
)

sys.path.append("..")

dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(dotenv_path)

ENVIRONMENT = "dev"


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


def test_get_user_list():
    # Retrieve the parameters from the environment variables
    current_script_path = os.path.abspath(__file__)
    project_root = os.path.dirname(os.path.dirname(current_script_path))
    os.chdir(project_root)

    repository_path_default = str(Path(os.getcwd()))
    parameters = {
        "data_product_id": "wonder_metadata_dev",
        "data_product_id_root": "ocio",
        "data_product_id_individual": "CDH",
        "environment": "dev",
        "repository_path": repository_path_default,
    }
    config = get_config(parameters)

    # Configure the Alation API Token and Parameters
    edc_alation_base_url = config.get("edc_alation_base_url")
    token_endpoint = alation_token_endpoint.TokenEndpoint(edc_alation_base_url)
    (
        status_code,
        edc_alation_api_token,
        api_refresh_token,
    ) = token_endpoint.get_api_token_from_config(config)
    print(f"edc_alation_api_access_token_length: {str(len(edc_alation_api_token))}")
    print(f"api_refresh_token_length: {str(len(api_refresh_token))}")
    assert status_code == 200
    edc_alation_base_url = config.get("edc_alation_base_url")

    user_id_json = [
        {"otype": "user", "oid": 15},
        {"otype": "user", "oid": 99},
        {"otype": "user", "oid": 110},
    ]

    # Make the POST API Call for the datasource
    user = alation_user.User()
    user_list_result = user.get_user_list_from_user_ids_json(
        user_id_json, edc_alation_api_token, edc_alation_base_url
    )

    status_code = user_list_result.status_code
    user_list_result_json = user_list_result.json()

    df_user_list = json_normalize(user_list_result_json)

    # Check that the method behaved as expected
    # Set display options
    pd.set_option("display.max_columns", None)  # or 1000
    pd.set_option("display.max_rows", None)  # or 1000
    pd.set_option("display.expand_frame_repr", False)
    pd.set_option("display.width", None)  # or 1000

    print(df_user_list)
    assert status_code == 200
