"""
This module provides functions for retrieving and testing API keys for a service named 'Posit'.

The functions in this module retrieve API keys for the Posit service from environment variables 
and Azure Key Vault, then use those keys to interact with the service and test its functionality.

Functions:
    get_config(parameters): Returns configuration data for the environment.
    get_posit_api_key(): Retrieves the Posit service API key from Azure Key Vault.
    test_list_content(): Tests the Posit service by listing content using the API key.

This module uses the `dotenv`, `os`, and `pathlib` standard libraries, as well as several
custom modules such as `cdh_posit_connect`, `cdc_env_logging`, `cdh_az_key_vault`, 
and `cdc_env_metadata` from the `cdh_dav_python` package.

Environment variables are loaded from a .env file in the same directory as this module.
"""

from cdh_dav_python.cdc_metadata_service import (
    environment_metadata as cdc_env_metadata,
)
from cdh_dav_python.az_key_vault_service import (
    az_key_vault as cdh_az_key_vault,
)

from cdh_dav_python.cdc_admin_service.environment_logging import LoggerSingleton

import cdh_dav_python.cdc_tech_environment_service.environment_file as cdc_env_file

import os
import cdh_dav_python.posit_service.posit_connect as cdh_posit_connect
from dotenv import load_dotenv
from pathlib import Path
from datetime import datetime

dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(dotenv_path)

# Get the currently running file name
SERVICE_NAME = os.path.basename(__file__)
# Get the parent folder name of the running file
NAMESPACE_NAME = os.path.basename(os.path.dirname(__file__))


def get_config(parameters):
    environment_metadata = cdc_env_metadata.EnvironmentMetaData()

    config = environment_metadata.get_configuration_common(parameters, None)

    return config


def get_posit_api_key(data_product_id, environment):
    """
    Retrieves the POSIT API key and base URL from the configuration.

    Returns:
        tuple: A tuple containing the POSIT API key and base URL.
    """

    tracer, logger = LoggerSingleton.instance(
        NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
    ).initialize_logging_and_tracing()

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

    posit_connect_base_url = config.get("posit_connect_base_url")

    logger.info(f"posit_connect_base_url:{posit_connect_base_url}")
    az_sub_client_secret_key = config.get("az_sub_client_secret_key")
    az_sub_client_secret_key = az_sub_client_secret_key.replace("-", "_")
    client_secret = os.getenv(az_sub_client_secret_key)
    tenant_id = config.get("tenant_id")
    client_id = config.get("client_id")
    az_kv_key_vault_name = config.get("az_kv_key_vault_name")
    running_interactive = False
    if not client_secret:
        running_interactive = True

    az_key_vault = cdh_az_key_vault.AzKeyVault(
        tenant_id,
        client_id,
        client_secret,
        az_kv_key_vault_name,
        running_interactive,
    )

    az_kv_posit_connect_secret_key = config.get("az_kv_posit_connect_secret_key")

    cdh_databricks_kv_scope = config.get("cdh_databricks_kv_scope")
    az_kv_posit_connect_secret = az_key_vault.get_secret(
        az_kv_posit_connect_secret_key, cdh_databricks_kv_scope
    )

    return az_kv_posit_connect_secret, posit_connect_base_url


def test_list_content():
    # Make the GET API Call for the datasource
    posit_connect = cdh_posit_connect.PositConnect()
    posit_api_key, posit_connect_base_url = get_posit_api_key()
    (
        connect_status_code,
        connect_list_array,
        api_url,
    ) = posit_connect.list_content(posit_api_key, posit_connect_base_url)

    print(f"api_url: {api_url}")
    # Check that the method behaved as expected
    assert connect_status_code == 200
    print(len(connect_list_array))
    assert len(connect_list_array) > 0


def test_verify_api_key():
    # Make the GET API Call for the datasource
    posit_connect = cdh_posit_connect.PositConnect()
    posit_api_key, posit_connect_base_url = get_posit_api_key()
    (
        connect_status_code,
        connect_list_array,
        api_url,
    ) = posit_connect.verify_api_key(posit_api_key, posit_connect_base_url)

    print(f"api_url: {api_url}")
    # Check that the method behaved as expected
    assert connect_status_code == 200
    print(len(connect_list_array))
    assert len(connect_list_array) > 0


def test_generate_manifest():
    tracer, logger = LoggerSingleton.instance(
        NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
    ).initialize_logging_and_tracing()

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

    posit_connect_base_url = config.get("posit_connect_base_url")

    environment = config.get("environment")
    obj_file = cdc_env_file.EnvironmentFile()

    app_dir = os.path.dirname(os.path.abspath(__file__))

    manifest_path = app_dir + "/" + environment + "_posit_manifests/"

    swagger_path = app_dir + "/" + environment + "_swagger_manifests/"

    yyyy = str(datetime.now().year)
    dd = str(datetime.now().day).zfill(2)
    mm = str(datetime.now().month).zfill(2)

    json_extension = "_" + yyyy + "_" + mm + "_" + dd + ".json"
    manifest_json_file = manifest_path + "manifest" + json_extension
    # swagger_file = swagger_path + "swagger" + json_extension
    # use cached json file for now
    # having issues downloading
    swagger_file = swagger_path + "swagger_2023_06_22.json"
    connect_api_key = get_posit_api_key()
    requirements_file = app_dir + "/requirements.txt"

    # Make the GET API Call for the datasource
    posit_connect = cdh_posit_connect.PositConnect()
    posit_api_key, posit_connect_base_url = get_posit_api_key()
    (
        connect_status_code,
        connect_list_array,
        api_url,
    ) = posit_connect.generate_manifest(posit_api_key, posit_connect_base_url)

    print(f"api_url: {api_url}")
    # Check that the method behaved as expected
    assert connect_status_code == 200
    print(len(connect_list_array))
    assert len(connect_list_array) > 0
