from dotenv import load_dotenv, find_dotenv, set_key
import cdh_dav_python.cdc_tech_environment_service.environment_core as cdh_env_core
import pytest
from unittest.mock import patch
from typing import Tuple
import os
from pathlib import Path
import sys
import os

sys.path.append("..")

dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(dotenv_path)

# And here's a test for it using pytest


@pytest.fixture
def mock_getenv():
    with patch("os.getenv") as mock:
        yield mock


def test_get_environment_name(mock_getenv):
    # Let's assume your virtual environment path is `/path/to/myproject_dev`
    mock_getenv.return_value = "/path/to/ncezid_hamlet_dev"

    environment_core = cdh_env_core.EnvironmentCore()

    # Now when you call the function, it will use the above path as the `VIRTUAL_ENV`
    (
        app_environment,
        data_product_id,
        virtual_env,
    ) = environment_core.get_environment_name()

    # Check that the function returns the correct values
    assert app_environment == "dev"
    assert data_product_id == "ncezid_hamlet"
    assert virtual_env == "ncezid_hamlet_dev"

    # Test for when there is no virtual environment
    mock_getenv.return_value = None

    result = environment_core.get_environment_name()
    assert result == (None, None, None)


@patch("os.getenv")
def test_get_environment_name_special_case(mock_getenv):
    # Let's assume your virtual environment path is `/path/to/wonder_metadata_dev`
    mock_getenv.return_value = "/path/to/wonder_metadata_dev"

    # Now when you call the function, it will use the above path as the `VIRTUAL_ENV`
    environment_core = cdh_env_core.EnvironmentCore()
    result = environment_core.get_environment_name()
    (
        environment,
        data_product_id,
        virtual_env,
    ) = environment_core.get_environment_name()

    # Check that the function returns the correct values
    assert environment == "dev"
    assert data_product_id == "wonder_metadata"
    assert virtual_env == "wonder_metadata_dev"
