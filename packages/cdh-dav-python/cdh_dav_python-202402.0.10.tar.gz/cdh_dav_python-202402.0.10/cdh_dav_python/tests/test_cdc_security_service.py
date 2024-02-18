from dotenv import load_dotenv, find_dotenv, set_key
import pytest
from unittest.mock import patch
import sys
import os
import sys
from unittest.mock import Mock
from azure.identity import ClientSecretCredential
from azure.core.exceptions import ClientAuthenticationError
from pathlib import Path
from dotenv import load_dotenv

sys.path.append("..")
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from cdh_dav_python.cdc_metadata_service.environment_metadata import (
    EnvironmentMetaData,
)

import cdh_dav_python.cdc_security_service.security_core as cdh_security_core

dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(dotenv_path)


def get_config(parameters, data_product_id, environment):
    environment_metadata = EnvironmentMetaData()
    config = environment_metadata.get_configuration_common(
        parameters, None, data_product_id, environment
    )
    return config


def test_verify_az_sub_client_secret_valid_password():
    """
    Test case to verify the validity of Azure subscription client secret password.

    This test case retrieves the necessary configuration parameters, such as tenant ID, client ID,
    and client secret, from the environment or configuration file. It then calls the
    `cdh_security_core.SecurityCore.verify_az_sub_client_secret` function to verify the validity
    of the client secret password. The expected result is a status code of 200 and a message
    indicating that the service principal password is valid.
    """

    # Get the absolute path of the current script
    current_script_path = os.path.abspath(__file__)

    # Get the project root directory by going up one or more levels
    project_root = os.path.dirname(os.path.dirname(current_script_path))

    # Change the current working directory to the project root directory
    os.chdir(project_root)

    repository_path_default = str(Path(os.getcwd()))

    data_product_id = "wonder_metadata"
    data_product_root = "wonder"
    data_product_individual = "metadata"
    environment = "dev"

    parameters = {
        "data_product_id": data_product_id,
        "data_product_id_root": data_product_root,
        "data_product_id_individual": data_product_individual,
        "environment": environment,
        "repository_path": repository_path_default,
    }

    config = get_config(parameters, data_product_id, environment)

    az_sub_tenant_id = config.get("az_sub_tenant_id")
    az_sub_client_id = config.get("az_sub_client_id")
    az_sub_client_secret_key = config.get("az_sub_client_secret_key")
    az_kv_az_sub_client_env_secret_key = az_sub_client_secret_key.replace("-", "_")
    az_kv_az_sub_client_env_secret = os.environ.get(az_kv_az_sub_client_env_secret_key)
    print(f"az_sub_tenant_id: {az_sub_tenant_id}")
    print(f"az_sub_client_id: {az_sub_client_id}")
    # Call the function under test
    (
        status_code,
        message,
    ) = cdh_security_core.SecurityCore.verify_az_sub_client_secret(
        az_sub_tenant_id,
        az_sub_client_id,
        az_kv_az_sub_client_env_secret,
        data_product_id,
        environment,
    )

    # Assert the result
    assert status_code == 200
    assert message == "Service principal password is valid."


def test_verify_az_sub_client_secret_invalid_password():
    """
    Test case to verify the behavior of the 'verify_az_sub_client_secret' function
    when an invalid client secret password is provided.
    """

    # Get the absolute path of the current script
    current_script_path = os.path.abspath(__file__)

    # Get the project root directory by going up one or more levels
    project_root = os.path.dirname(os.path.dirname(current_script_path))

    # Change the current working directory to the project root directory
    os.chdir(project_root)

    repository_path_default = str(Path(os.getcwd()))

    data_product_id = "wonder_metadata"
    data_product_root = "wonder"
    data_product_individual = "metadata"
    environment = "dev"

    parameters = {
        "data_product_id": data_product_id,
        "data_product_id_root": data_product_root,
        "data_product_id_individual": data_product_individual,
        "environment": environment,
        "repository_path": repository_path_default,
    }

    config = get_config(parameters, data_product_id, environment)

    # Get the absolute path of the current script
    current_script_path = os.path.abspath(__file__)

    # Get the project root directory by going up one or more levels
    project_root = os.path.dirname(os.path.dirname(current_script_path))

    # Change the current working directory to the project root directory
    os.chdir(project_root)

    repository_path_default = str(Path(os.getcwd()))

    config = get_config(parameters, data_product_id, environment)

    az_sub_tenant_id = config.get("az_sub_tenant_id")
    az_sub_client_id = config.get("az_sub_client_id")
    client_secret = "invalid_password"

    # Call the function under test
    (
        status_code,
        message,
    ) = cdh_security_core.SecurityCore.verify_az_sub_client_secret(
        az_sub_tenant_id, az_sub_client_id, client_secret, data_product_id, environment
    )

    # Assert the result
    assert status_code == 500
    print(f"message: {message}")


if __name__ == "__main__":
    pytest.main()
