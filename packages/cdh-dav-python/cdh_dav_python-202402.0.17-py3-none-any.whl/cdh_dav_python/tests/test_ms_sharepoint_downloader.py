import os
import sys
import json
from pathlib import Path
import pytest
import pandas as pd

from dotenv import load_dotenv
from cdh_dav_python.cdc_metadata_service import (
    environment_metadata as cdc_env_metadata,
)

from cdh_dav_python.ms_sharepoint_service import (
    sharepoint_downloader as ms_sharepoint_downloader,
)

import cdh_dav_python.cdc_tech_environment_service.environment_file as cdc_env_file

ENVIRONMENT = "dev"

# Get the absolute path of the current script
current_script_path = os.path.abspath(__file__)

# Get the project root directory by going up one or more levels
project_root = os.path.dirname(os.path.dirname(current_script_path))

# Change the current working directory to the project root directory
os.chdir(project_root)

sys.path.append("..")

dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(dotenv_path)


REPOSITORY_PATH_DEFAULT = str(Path(os.getcwd()))

parameters = {
    "data_product_id": "cdh_premier_exploratory",
    "data_product_id_root": "cdh",
    "data_product_id_individual": "premier_exploratory",
    "environment": "dev",
    "repository_path": REPOSITORY_PATH_DEFAULT,
}


def get_config(parameters):
    """
    Retrieves the configuration common to the given parameters from the environmental metadata.

    Args:
        parameters (dict): A dictionary of parameters used to obtain the common configuration.

    Returns:
        dict: A dictionary containing the configuration common to the given parameters.

    Raises:
        Any exceptions raised by the `get_configuration_common` method of `EnvironmentMetaData` class.

    Note:
        The specific structure and content of the input `parameters` and the returned configuration dictionary
        depend on the implementation of the `get_configuration_common` method in `EnvironmentMetaData` class.
    """

    environment_metadata = cdc_env_metadata.EnvironmentMetaData()

    config = environment_metadata.get_configuration_common(parameters, None)

    return config


def test_download_sharepoint_file():
    # Change the current working directory to the project root directory

    os.chdir(project_root)

    config = get_config(parameters)

    alation_schema_id = 2649
    sharepoint_downloader = ms_sharepoint_downloader.SharepointDownloader()

    # Get the file utility object
    obj_file = cdc_env_file.EnvironmentFile()

    # Get the manifest file
    app_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(app_dir)
    data_definition_path = (
        parent_dir + "/" + ENVIRONMENT + "_data_definitions/"
    )
    data_definition_path = obj_file.convert_to_current_os_dir(
        data_definition_path
    )
    # Make sure you have put a file in the uploads directory
    excel_data_definition_file = (
        data_definition_path + "excel_data_definition_for_schemas_sql.xlsx"
    )

    # Check if the expected results are available
    manifest_excel_file = schema.download_manifest_excel(
        alation_schema_id, config, excel_data_definition_file
    )

    assert len(str(manifest_excel_file)) > 1
