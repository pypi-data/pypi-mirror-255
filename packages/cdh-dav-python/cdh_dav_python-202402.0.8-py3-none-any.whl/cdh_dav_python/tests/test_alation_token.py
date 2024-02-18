import os
import sys
import json
import pytest

from unittest import mock
from datetime import datetime
from dotenv import load_dotenv
from cdh_dav_python.cdc_metadata_service import (
    environment_metadata as cdc_env_metadata,
)

import cdh_dav_python.alation_service.datasource as alation_datasource
import cdh_dav_python.alation_service.token as alation_token_endpoint

from pathlib import Path

sys.path.append("..")

dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(dotenv_path)

ENVIRONMENT = "dev"


def get_config(parameters):
    environment_metadata = cdc_env_metadata.EnvironmentMetaData()

    config = environment_metadata.get_configuration_common(parameters, None)

    return config


def test_get_api_token_from_config():
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
    edc_alation_base_url = config.get("edc_alation_base_url")
    token_endpoint = alation_token_endpoint.TokenEndpoint(edc_alation_base_url)
    token_result = token_endpoint.get_api_token_from_config(config)
    assert len(token_result) > 0
