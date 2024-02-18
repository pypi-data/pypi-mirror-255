"""
This module contains various tests that are used to ensure the functionality of the CDC Data Hub LAVA Python. The tests focus on creating and manipulating Excel files, as well as interacting with the Alation API.

Dependencies:

    os, sys, pandas: Basic Python libraries used for system interaction, data manipulation, and testing.
    dotenv: Used for loading environment variables.
    environment_file and environment_metadata: Custom modules used to manage environment-specific information.
    alation_service.manifest_excel and alation_service.token: Custom modules used to interact with the Alation API.

Functions:

    get_config(parameters): Helper function to get the configuration from the environment metadata.

Test cases:

    test_generate_excel_file(): Test that an Excel file can be correctly generated.
    test_generate_excel_file_data_csvs(): Test that the function can correctly generate data and save it as CSV files.
    test_generate_excel_from_file_data_csvs(): Test that the function can correctly generate an Excel file from CSV data.
    """

import os
import sys
from pathlib import Path
import pandas as pd

from dotenv import load_dotenv

from cdh_dav_python.cdc_tech_environment_service import (
    environment_file as cdc_env_file,
)

from cdh_dav_python.cdc_metadata_service import (
    environment_metadata as cdc_env_metadata,
)

from cdh_dav_python.alation_service import (
    db_schema as alation_schema,
    db_table as alation_table,
    excel_manifest as alation_manifest_excel,
    token as alation_token_endpoint,
)


sys.path.append("..")

dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(dotenv_path)

ENVIRONMENT = "dev"


def get_config(parameters):
    environment_metadata = cdc_env_metadata.EnvironmentMetaData()

    config = environment_metadata.get_configuration_common(parameters, None)

    return config


def test_generate_excel_file_synapse():
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
    print(f"api_access_token_length: {str(len(edc_alation_api_token))}")
    print(f"api_refresh_token_length: {str(len(api_refresh_token))}")
    assert status_code == 200
    edc_alation_base_url = config.get("edc_alation_base_url")
    alation_schema_id = 1464

    os.chdir(project_root)
    obj_file = cdc_env_file.EnvironmentFile()
    app_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(app_dir)

    data_definition_path = parent_dir + "/" + ENVIRONMENT + "_data_definitions/"
    data_definition_path = obj_file.convert_to_current_os_dir(data_definition_path)
    excel_data_definition_file = (
        data_definition_path + "excel_data_definition_for_tables_sql.xlsx"
    )

    manifest_excel = alation_manifest_excel.ManifestExcel()
    (
        df_schema,
        df_tables,
        manifest_excel_file,
        hidden_fields,
        df_table_fields_data_definition,
        df_columns,
    ) = manifest_excel.generate_excel_file_data(
        alation_schema_id, config, excel_data_definition_file
    )

    table = alation_table.Table(None, excel_data_definition_file)
    df_status, excel_data_definition_file = table.fetch_valueset("Status of Dataset")
    df_access_level, excel_data_definition_file = table.fetch_valueset("Access Level")
    df_format, excel_data_definition_file = table.fetch_valueset("Format")
    df_language, excel_data_definition_file = table.fetch_valueset("Language")
    df_steward, excel_data_definition_file = table.fetch_valueset("steward")
    df_update_frequency, excel_data_definition_file = table.fetch_valueset(
        "update_frequency"
    )

    hidden_fields = []
    manifest_excel = alation_manifest_excel.ManifestExcel()
    manifest_excel_file = manifest_excel.create_excel_from_data(
        config,
        hidden_fields,
        df_tables,
        manifest_excel_file,
        df_status,
        df_steward,
        df_access_level,
        df_language,
        df_update_frequency,
        df_format,
        df_table_fields_data_definition,
    )

    assert manifest_excel_file is not None
    assert os.path.exists(manifest_excel_file) == True


def test_generate_excel_file_databricks():
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
    print(f"api_access_token_length: {str(len(edc_alation_api_token))}")
    print(f"api_refresh_token_length: {str(len(api_refresh_token))}")
    assert status_code == 200
    edc_alation_base_url = config.get("edc_alation_base_url")
    alation_schema_id = 106788

    os.chdir(project_root)
    obj_file = cdc_env_file.EnvironmentFile()
    app_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(app_dir)

    data_definition_path = parent_dir + "/" + ENVIRONMENT + "_data_definitions/"
    data_definition_path = obj_file.convert_to_current_os_dir(data_definition_path)
    excel_data_definition_file = (
        data_definition_path + "excel_data_definition_for_tables_sql.xlsx"
    )

    manifest_excel = alation_manifest_excel.ManifestExcel()
    (
        df_schema,
        df_tables,
        manifest_excel_file,
        hidden_fields,
        df_table_fields_data_definition,
        df_columns,
    ) = manifest_excel.generate_excel_file_data(
        alation_schema_id, config, excel_data_definition_file
    )

    table = alation_table.Table(None, excel_data_definition_file)
    df_status, excel_data_definition_file = table.fetch_valueset("Status of Dataset")
    df_access_level, excel_data_definition_file = table.fetch_valueset("Access Level")
    df_format, excel_data_definition_file = table.fetch_valueset("Format")
    df_language, excel_data_definition_file = table.fetch_valueset("Language")
    df_steward, excel_data_definition_file = table.fetch_valueset("steward")
    df_update_frequency, excel_data_definition_file = table.fetch_valueset(
        "update_frequency"
    )

    manifest_excel = alation_manifest_excel.ManifestExcel()
    manifest_excel_file = manifest_excel.create_excel_from_data(
        config,
        df_schema,
        df_tables,
        manifest_excel_file,
        df_status,
        df_steward,
        df_access_level,
        df_language,
        df_update_frequency,
        df_format,
        df_table_fields_data_definition,
    )

    assert manifest_excel_file is not None
    assert os.path.exists(manifest_excel_file) == True
