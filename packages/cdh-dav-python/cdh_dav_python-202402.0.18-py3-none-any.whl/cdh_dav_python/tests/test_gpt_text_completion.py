import os
import unittest
from dotenv import load_dotenv
from pathlib import Path

from cdh_dav_python.gpt_service import (
    text_completion as gpt_text_completion,
)

from cdh_dav_python.cdc_metadata_service import (
    environment_metadata as cdc_env_metadata,
)

from cdh_dav_python.az_key_vault_service import (
    az_key_vault as cdh_az_key_vault,
)


dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(dotenv_path)

# Get the currently running file name
SERVICE_NAME = os.path.basename(__file__)
# Get the parent folder name of the running file
NAMESPACE_NAME = os.path.basename(os.path.dirname(__file__))

# Get the absolute path of the current script
current_script_path = os.path.abspath(__file__)

# Get the project root directory by going up one or more levels
project_root = os.path.dirname(os.path.dirname(current_script_path))

# Change the current working directory to the project root directory
os.chdir(project_root)

REPOSITORY_PATH_DEFAULT = str(Path(os.getcwd()))


def get_secret(secret_key, config):
    # Try to get the secret from the environment variable
    secret_key = secret_key.replace("-", "_")
    requested_secret = os.getenv(secret_key)

    if requested_secret is None:
        running_interactive = False

        az_sub_client_secret_key = config.get("az_sub_client_secret_key")
        az_sub_client_secret_key = az_sub_client_secret_key.replace("-", "_")

        client_secret = os.getenv(az_sub_client_secret_key)

        tenant_id = config.get("tenant_id")
        client_id = config.get("client_id")
        az_kv_key_vault_name = config.get("az_kv_key_vault_name")

        az_key_vault = cdh_az_key_vault.AzKeyVault(
            tenant_id,
            client_id,
            client_secret,
            az_kv_key_vault_name,
            running_interactive,
        )

        cdh_databricks_kv_scope = config.get("cdh_databricks_kv_scope")

        secret_key = secret_key.replace("_", "-")
        requested_secret = az_key_vault.get_secret(secret_key, cdh_databricks_kv_scope)

    return requested_secret


def get_config(parameters):
    environment_metadata = cdc_env_metadata.EnvironmentMetaData()

    config = environment_metadata.get_configuration_common(parameters, None)

    return config


def get_gpt_api_key():
    parameters = {
        "data_product_id": "wonder_metadata_dev",
        "data_product_id_root": "ocio",
        "data_product_id_individual": "CDH",
        "environment": "dev",
        "repository_path": REPOSITORY_PATH_DEFAULT,
    }
    config = get_config(parameters)

    az_kv_gpt_client_secret_key = config.get("az_kv_gpt_client_secret_key")

    az_kv_gpt_client_secret = get_secret(az_kv_gpt_client_secret_key, config)

    return az_kv_gpt_client_secret


def test_create_docstring_for_table():
    columns = ["id INT", "applicant_name VARCHAR(100)", "email VARCHAR(100)"]
    table_name = "job_candidates"

    gpt_api_key = get_gpt_api_key()

    text_completion = gpt_text_completion.TextCompletion()

    output = text_completion.create_docstring_for_table(
        gpt_api_key, table_name, columns
    )
    print(f"output: {output}")
    assert len(output) > 0


if __name__ == "__main__":
    unittest.main()
