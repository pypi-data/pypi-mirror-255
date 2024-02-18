from dotenv import load_dotenv, find_dotenv, set_key
from cdh_dav_python.cdc_metadata_service.environment_metadata import (
    EnvironmentMetaData,
)
from cdh_dav_python.github_service.github_secret import GitHubSecret
from pathlib import Path
import os
import sys

from unittest.mock import patch
from requests.exceptions import RequestException

sys.path.append("..")

dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(dotenv_path)


def get_config(parameters):
    environment_metadata = EnvironmentMetaData()
    config = environment_metadata.get_configuration_common(parameters, None)
    return config


# def test_get_github_secret_interactive_success():

#     path = Path(os.getcwd())
#     repository_path_default = str(path)

#     parameters = {
#         "data_product_id": "wonder_metadata_dev",
#         "data_product_id_root": "ocio",
#         "data_product_id_individual": "CDH",
#         "environment": "dev",
#         "az_sub_client_secret_key": "OCIO-CDH-DEV-AZ-CLIENT-SECRET",
#         "repository_path": repository_path_default,
#         "running_local": True,
#     }

#     # Get the virtual environment path
#     venv_path = os.getenv('VIRTUAL_ENV')

#     # Extract the virtual environment name from the path
#     if venv_path:
#         venv_name = os.path.basename(venv_path)
#         print(f"Virtual environment name: {venv_name}")
#     else:
#         print("Not running inside a virtual environment.")

#     # Print all environment variables
#     #    for key, value in os.environ.items():
#     #        print(f"{key}: {value}")

#     config = get_config(parameters)

#     gh_owner_name = config.get("gh_owner_name")
#     gh_repository_name = config.get("gh_repository_name")
#     gh_secret_name = config.get("gh_az_sub_client_secret_key")

#     az_kv_gh_client_secret_key = config.get("az_kv_gh_client_secret_key")
#     gh_secret_env_var_key = az_kv_gh_client_secret_key.replace("-", "_")
#     print(f"gh_secret_env_var_key: {gh_secret_env_var_key}")

#     az_sub_client_secret_key = config.get("az_sub_client_secret_key")
#     azure_client_secret_env_var_key = az_sub_client_secret_key.replace("-", "_")
#     print(
#         f"azure_client_secret_env_var_key: {azure_client_secret_env_var_key}")
#     expected_value = os.environ.get(azure_client_secret_env_var_key)
#     if expected_value is None:
#         expected_value = ""
#         expected_value_length = 0
#     else:
#         expected_value_length = len(expected_value)
#     print(f"expected_value_length: {expected_value_length}")
#     assert expected_value_length > 0

#     print(f"gh_owner_name: {gh_owner_name}")
#     print(f"gh_repository_name: {gh_repository_name}")
#     print(f"gh_secret_name: {gh_secret_name}")

#     with patch("requests.get") as mock_get:
#         mock_get.return_value.status_code = 200
#         mock_get.return_value.json.return_value = {
#             "secret": {
#                 "value": expected_value
#             }
#         }

#         status_code, response_content, api_url = GitHubSecret.get_github_secret_interactive(
#             gh_owner_name, gh_repository_name, gh_secret_name
#         )

#         print(f"response_content: {response_content}")

#         secret_value = response_content.get('secret', {}).get('value')

#         assert status_code == 200
#         assert secret_value == expected_value
#         assert len(secret_value) > 0
#         assert api_url == f"https://api.github.com/repos/{gh_owner_name}/{gh_repository_name}/actions/secrets/{gh_secret_name}"


def test_get_github_secret_success():
    path = Path(os.getcwd())
    repository_path_default = str(path)

    parameters = {
        "data_product_id": "wonder_metadata_dev",
        "data_product_id_root": "ocio",
        "data_product_id_individual": "CDH",
        "environment": "dev",
        "az_sub_client_secret_key": "OCIO-CDH-DEV-AZ-CLIENT-SECRET",
        "repository_path": repository_path_default,
        "running_local": True,
    }

    # Get the virtual environment path
    venv_path = os.getenv("VIRTUAL_ENV")

    # Extract the virtual environment name from the path
    if venv_path:
        venv_name = os.path.basename(venv_path)
        print(f"Virtual environment name: {venv_name}")
    else:
        print("Not running inside a virtual environment.")

    # Print all environment variables
    #    for key, value in os.environ.items():
    #        print(f"{key}: {value}")

    config = get_config(parameters)

    gh_owner_name = config.get("gh_owner_name")
    gh_repository_name = config.get("gh_repository_name")
    gh_secret_name = config.get("gh_az_sub_client_secret_key")

    az_kv_gh_client_secret_key = config.get("az_kv_gh_client_secret_key")
    gh_secret_env_var_key = az_kv_gh_client_secret_key.replace("-", "_")

    print(f"gh_secret_env_var_key: {gh_secret_env_var_key}")
    gh_access_token = os.environ.get(gh_secret_env_var_key)
    if gh_access_token is None:
        gh_access_token = ""
        gh_access_token_length = 0
    else:
        gh_access_token_length = len(gh_access_token)
    print(f"gh_access_token_length: {gh_access_token_length}")
    assert gh_access_token_length > 0

    az_sub_client_secret_key = config.get("az_sub_client_secret_key")
    azure_client_secret_env_var_key = az_sub_client_secret_key.replace("-", "_")
    print(f"azure_client_secret_env_var_key: {azure_client_secret_env_var_key}")
    expected_value = os.environ.get(azure_client_secret_env_var_key)
    if expected_value is None:
        expected_value = ""
        expected_value_length = 0
    else:
        expected_value_length = len(expected_value)
    print(f"expected_value_length: {expected_value_length}")
    assert expected_value_length > 0

    print(f"gh_owner_name: {gh_owner_name}")
    print(f"gh_repository_name: {gh_repository_name}")
    print(f"gh_secret_name: {gh_secret_name}")

    with patch("requests.get") as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {"secret": {"value": expected_value}}

        (
            status_code,
            response_content,
            api_url,
        ) = GitHubSecret.get_github_secret(
            gh_access_token, gh_owner_name, gh_repository_name, gh_secret_name
        )

        print(f"response_content: {response_content}")
        mock_get.assert_called_with(
            f"https://api.github.com/repos/{gh_owner_name}/{gh_repository_name}/actions/secrets/{gh_secret_name}",
            headers={
                "Accept": "application/vnd.github.v3+json",
                "Authorization": f"Bearer {gh_access_token}",
            },
        )

        secret_value = response_content.get("secret", {}).get("value")

        assert status_code == 200
        assert secret_value == expected_value
        assert len(secret_value) > 0
        assert (
            api_url
            == f"https://api.github.com/repos/{gh_owner_name}/{gh_repository_name}/actions/secrets/{gh_secret_name}"
        )


# def test_get_github_secret_request_error():
#     path = Path(os.getcwd())
#     repository_path_default = str(path)

#     parameters = {
#         "data_product_id": "wonder_metadata_dev",
#         "data_product_id_root": "ocio",
#         "data_product_id_individual": "CDH",
#         "environment": "dev",
#         "az_sub_client_secret_key": "OCIO-CDH-DEV-AZ-CLIENT-SECRET",
#         "repository_path": repository_path_default,
#         "running_local": True,
#     }

#     # Get the virtual environment path
#     venv_path = os.getenv('VIRTUAL_ENV')

#     # Extract the virtual environment name from the path
#     if venv_path:
#         venv_name = os.path.basename(venv_path)
#         print(f"Virtual environment name: {venv_name}")
#     else:
#         print("Not running inside a virtual environment.")

#     # Print all environment variables
#     #    for key, value in os.environ.items():
#     #        print(f"{key}: {value}")

#     config = get_config(parameters)

#     gh_owner_name = config.get("gh_owner_name")
#     gh_repository_name = config.get("gh_repository_name")
#     gh_secret_name = config.get("gh_az_sub_client_secret_key")

#     az_kv_gh_client_secret_key = config.get("az_kv_gh_client_secret_key")
#     gh_secret_env_var_key = az_kv_gh_client_secret_key.replace("-", "_")

#     print(f"gh_secret_env_var_key: {gh_secret_env_var_key}")
#     gh_access_token = os.environ.get(gh_secret_env_var_key)
#     if gh_access_token is None:
#         gh_access_token = ""
#         gh_access_token_length = 0
#     else:
#         gh_access_token_length = len(gh_access_token)
#     print(f"gh_access_token_length: {gh_access_token_length}")
#     assert gh_access_token_length > 0

#     az_sub_client_secret_key = config.get("az_sub_client_secret_key")
#     azure_client_secret_env_var_key = az_sub_client_secret_key.replace("-", "_")
#     print(
#         f"azure_client_secret_env_var_key: {azure_client_secret_env_var_key}")
#     expected_value = os.environ.get(azure_client_secret_env_var_key)
#     if expected_value is None:
#         expected_value = ""
#         expected_value_length = 0
#     else:
#         expected_value_length = len(expected_value)
#     print(f"expected_value_length: {expected_value_length}")
#     assert expected_value_length > 0

#     az_sub_client_secret_key = az_sub_client_secret_key + "_invalid"

#     print(f"gh_owner_name: {gh_owner_name}")
#     print(f"gh_repository_name: {gh_repository_name}")
#     print(f"gh_secret_name: {gh_secret_name}")

#     with patch("requests.get") as mock_get:
#         mock_get.return_value.status_code = 200
#         mock_get.return_value.json.return_value = {
#             "secret": {
#                 "value": expected_value
#             }
#         }

#         status_code, response_content, api_url = GitHubSecret.get_github_secret(gh_access_token,
#                                                                                 gh_owner_name, gh_repository_name, gh_secret_name
#                                                                                 )

#         print(f"response_content: {response_content}")
#         mock_get.assert_called_with(
#             f"https://api.github.com/repos/{gh_owner_name}/{gh_repository_name}/actions/secrets/{gh_secret_name}",
#             headers={
#                 "Accept": "application/vnd.github.v3+json",
#                 "Authorization": f"Bearer {gh_access_token}"
#             }
#         )

#         secret_value = response_content.get('secret', {}).get('value')

#         assert status_code == 500
#         assert secret_value != expected_value
#         assert len(secret_value) == 0
#         assert api_url == f"https://api.github.com/repos/{gh_owner_name}/{gh_repository_name}/actions/secrets/{gh_secret_name}"
