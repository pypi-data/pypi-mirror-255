"""
This Python module contains a set of functions designed to interact with Alation, an automated cataloging and data search platform, and Databricks/Synapse, which are Apache Spark-based analytics platforms. It involves downloading, uploading, and validating data manifests, and also getting schema and schema tables from the platforms.

The key functions in this module are:

    get_config(parameters): Returns the configuration for a given environment.

    test_download_manifest_json_databricks(): Downloads the schema manifest json file from Databricks and validates if the file is downloaded correctly.

    test_download_manifest_json_synapse(): Downloads the schema manifest json file from Synapse and validates if the file is downloaded correctly.

    test_get_excel_manifest_file_path(): Tests if the manifest excel file name is generated correctly.

    test_get_json_manifest_file_path(): Tests if the manifest json file name is generated correctly.

    test_download_manifest_excel_databricks(): Downloads the schema manifest excel file from Databricks and validates if the file is downloaded correctly.

    test_download_manifest_excel_synapse(): Downloads the schema manifest excel file from Synapse and validates if the file is downloaded correctly.

    test_upload_manifest_json_databricks(): Uploads the schema manifest json file to Databricks and validates if the file is uploaded correctly.

    test_upload_manifest_json_synapse(): Uploads the schema manifest json file to Synapse and validates if the file is uploaded correctly.

    test_fetch_schema_synapse(): Retrieves the schema details from Synapse and validates the retrieval.

    test_fetch_schema_databricks(): Retrieves the schema details from Databricks and validates the retrieval.

    test_fetch_schema_tables_databricks(): Retrieves the schema tables from Databricks and validates the retrieval.

    test_fetch_schema_tables_synapse(): Retrieves the schema tables from Synapse and validates the retrieval.

This module makes use of several packages including os, sys, json, pytest, dotenv and a set of custom modules for accessing Alation and Databricks/Synapse. It is designed to work in a 'dev' environment and the repository path is set to the current working directory. The script is written to be platform-independent, adjusting paths as needed for the underlying operating system.
"""

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

from cdh_dav_python.alation_service import (
    db_schema as alation_schema,
    db_table as alation_table,
)

import cdh_dav_python.alation_service.token as alation_token_endpoint
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
    "data_product_id": "wonder_metadata_dev",
    "data_product_id_root": "ocio",
    "data_product_id_individual": "CDH",
    "environment": "dev",
    "repository_path": REPOSITORY_PATH_DEFAULT,
}


def get_config(parameters, data_product_id, environment):
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

    config = environment_metadata.get_configuration_common(
        parameters, None, data_product_id, environment
    )

    return config


def test_download_manifest_json():
    """
    Tests the method `download_manifest_json` in the `alation_schema.Schema` class.def test_download_manifest_json_databricks():


    This test ensures that the method downloads the schema manifest JSON file successfully and that
    the file exists in the specified directory. The test is performed for a specific `alation_schema_id`
    with id `106788`.

    Steps:
        1. Change the current working directory to the project root directory.
        2. Get the common configuration.
        3. Download the schema manifest JSON file using the `download_manifest_json` method.
        4. Check that the returned file name string is not empty.
        5. Check that the file exists in the specified directory.

    Raises:
        AssertionError: If the returned file name string is empty or if the file doesn't exist in the specified directory.
    """
    # Change the current working directory to the project root directory
    os.chdir(project_root)

    data_product_id = "wonder_metadata"
    environment = "dev"

    config = get_config(parameters, data_product_id, environment)

    alation_schema_id = 106788
    schema = alation_schema.Schema()
    manifest_json_file = schema.download_manifest_json(alation_schema_id, config)
    print(f"manifest_json_file: {str(manifest_json_file)}")
    # Check that the method behaved as expected
    assert len(str(manifest_json_file)) > 0

    obj_file = cdc_env_file.EnvironmentFile()
    dbutils = None
    running_local = True
    manifest_file_exists = obj_file.file_exists(
        running_local, manifest_json_file, dbutils
    )
    assert manifest_file_exists is True


def test_download_manifest_json_synapse():
    """
    Tests the method `download_manifest_json` in the `alation_schema.Schema` class.

    This test ensures that the method downloads the schema manifest JSON file successfully and that
    the file exists in the specified directory. The test is performed for a specific `alation_schema_id`
    with id `1464`.

    Steps:
        1. Change the current working directory to the project root directory.
        2. Get the common configuration.
        3. Download the schema manifest JSON file using the `download_manifest_json` method.
        4. Check that the returned file name string is not empty.
        5. Check that the file exists in the specified directory.

    Raises:
        AssertionError: If the returned file name string is empty or if the file doesn't exist in the specified directory.
    """
    # Change the current working directory to the project root directory
    os.chdir(project_root)

    data_product_id = "wonder_metadata"
    environment = "dev"

    config = get_config(parameters, data_product_id, environment)

    alation_schema_id = 1464
    schema = alation_schema.Schema()
    manifest_json_file = schema.download_manifest_json(alation_schema_id, config)
    print(f"manifest_json_file: {str(manifest_json_file)}")
    # Check that the method behaved as expected
    assert len(str(manifest_json_file)) > 0

    obj_file = cdc_env_file.EnvironmentFile()
    dbutils = None
    running_local = True
    manifest_file_exists = obj_file.file_exists(
        running_local, manifest_json_file, dbutils
    )
    assert manifest_file_exists is True


def test_get_excel_manifest_file_path():
    """
    This function tests the `get_excel_manifest_file_path` method of the `alation_schema.Schema` class.

    The test is performed in the following steps:

    1. The current working directory is changed to the project root directory.
    2. Configuration parameters are retrieved.
    3. Test parameters are defined, such as environment, datasource_title, schema_name, alation_user_id, and repository_path.
    4. An instance of the `alation_schema.Schema` class is created.
    5. The `get_excel_manifest_file_path` method is called with the test parameters.
    6. The resulting manifest_excel_file is printed.
    7. An assertion checks if the length of the manifest_excel_file string is greater than 0.

    This function does not take any parameters or return any values. Its sole purpose is to perform the test and raise an exception if the test fails.
    """
    # Change the current working directory to the project root directory
    os.chdir(project_root)

    data_product_id = "wonder_metadata"
    environment = "dev"
    config = get_config(parameters, data_product_id, environment)

    environment = "dev"
    datasource_title = "datasource_test"
    schema_name = "schema_test"
    alation_user_id = 7
    repository_path = config.get("repository_path")

    schema = alation_schema.Schema()
    manifest_excel_file = schema.get_excel_manifest_file_path(
        "download",
        repository_path,
        datasource_title,
        schema_name,
        environment,
        alation_user_id,
        data_product_id,
    )

    print(f"manifest_excel_file: {str(manifest_excel_file)}")

    assert len(str(manifest_excel_file)) > 0


def test_get_json_manifest_file_path():
    """
    Tests the method `get_json_manifest_file_path` in the `alation_schema.Schema` class.

    This test ensures that the method generates a valid manifest JSON file name. The test uses
    a set of predefined parameters (environment, datasource title, schema name, Alation user ID,
    and repository path obtained from the configuration).

    Steps:
        1. Change the current working directory to the project root directory.
        2. Get the common configuration.
        3. Generate the manifest JSON file name using the `get_json_manifest_file_path` method.
        4. Check that the returned file name string is not empty.

    Raises:
        AssertionError: If the returned file name string is empty.
    """
    # Change the current working directory to the project root directory
    os.chdir(project_root)

    data_product_id = "wonder_metadata"
    environment = "dev"
    config = get_config(parameters, data_product_id, environment)

    environment = "dev"
    datasource_title = "datasource_test"
    schema_name = "schema_test"
    alation_user_id = 7
    repository_path = config.get("repository_path")

    schema = alation_schema.Schema()
    manifest_json_file = schema.get_json_manifest_file_path(
        "download",
        repository_path,
        datasource_title,
        schema_name,
        environment,
        alation_user_id,
    )

    print(f"manifest_json_file: {str(manifest_json_file)}")

    assert len(str(manifest_json_file)) > 0


def test_download_manifest_excel_databricks():
    """
    This function tests the `download_manifest_excel` method of the `alation_schema.Schema` class.

    The test procedure includes the following steps:

    1. The current working directory is changed to the project root directory.
    2. Configuration parameters are retrieved.
    3. An instance of the `alation_schema.Schema` class is created.
    4. The `download_manifest_excel` method is called with the test parameters.
    5. An assertion checks if the length of the returned file path string is greater than 1.

    This function does not take any parameters or return any values. Its sole purpose is to perform the test and raise an exception if the test fails.

    Parameters
    ----------
    None

    Returns
    -------
    None
    """

    # Change the current working directory to the project root directory
    os.chdir(project_root)

    config = get_config(parameters)

    alation_schema_id = 106788
    schema = alation_schema.Schema()

    # Get the file utility object
    obj_file = cdc_env_file.EnvironmentFile()

    # Get the manifest file
    app_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(app_dir)
    data_definition_path = parent_dir + "/" + ENVIRONMENT + "_data_definitions/"
    data_definition_path = obj_file.convert_to_current_os_dir(data_definition_path)
    # Make sure you have put a file in the uploads directory
    excel_data_definition_file = (
        data_definition_path + "excel_data_definition_for_schemas_sql.xlsx"
    )

    # Check if the expected results are available
    manifest_excel_file = schema.download_manifest_excel(
        alation_schema_id, config, excel_data_definition_file
    )

    assert len(str(manifest_excel_file)) > 1


def test_download_manifest_excel_synapse():
    """
    This function tests the `download_manifest_excel` method of the `alation_schema.Schema` class
    for the Synapse platform.

    The test procedure is as follows:

    1. The current working directory is changed to the project root directory.
    2. Configuration parameters are retrieved.
    3. An instance of the `alation_schema.Schema` class is created.
    4. The `download_manifest_excel` method is called with the test parameters.
    5. An assertion checks if the length of the returned file path string is greater than 1.

    This function does not take any parameters or return any values. Its sole purpose is to perform the test
    and raise an exception if the test fails.

    Parameters
    ----------
    None

    Returns
    -------
    None
    """

    # Change the current working directory to the project root directory
    os.chdir(project_root)

    config = get_config(parameters)

    alation_schema_id = 1464
    schema = alation_schema.Schema()

    # Get the file utility object
    obj_file = cdc_env_file.EnvironmentFile()

    # Get the manifest file
    app_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(app_dir)
    data_definition_path = parent_dir + "/" + ENVIRONMENT + "_data_definitions/"
    data_definition_path = obj_file.convert_to_current_os_dir(data_definition_path)
    # Make sure you have put a file in the uploads directory
    excel_data_definition_file = (
        data_definition_path + "excel_data_definition_for_schemas_sql.xlsx"
    )

    # Check if the expected results are available
    manifest_excel_file = schema.download_manifest_excel(
        alation_schema_id, config, excel_data_definition_file
    )

    assert len(str(manifest_excel_file)) > 1


def test_download_manifest_excel_dcipher():
    """
    This function tests the `test_download_manifest_excel_dcipher` method of the `alation_schema.Schema` class
    for the dCipher platform.

    The test procedure is as follows:

    1. The current working directory is changed to the project root directory.
    2. Configuration parameters are retrieved.
    3. An instance of the `alation_schema.Schema` class is created.
    4. The `download_manifest_excel` method is called with the test parameters.
    5. An assertion checks if the length of the returned file path string is greater than 1.

    This function does not take any parameters or return any values. Its primary objective is to perform the test
    and raise an exception if the test does not pass.

    Parameters
    ----------
    None

    Returns
    -------
    None
    """

    # Change the current working directory to the project root directory
    os.chdir(project_root)

    config = get_config(parameters)

    alation_schema_id = 2649
    schema = alation_schema.Schema()

    # Get the file utility object
    obj_file = cdc_env_file.EnvironmentFile()

    # Get the manifest file
    app_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(app_dir)
    data_definition_path = parent_dir + "/" + ENVIRONMENT + "_data_definitions/"
    data_definition_path = obj_file.convert_to_current_os_dir(data_definition_path)
    # Make sure you have put a file in the uploads directory
    excel_data_definition_file = (
        data_definition_path + "excel_data_definition_for_schemas_sql.xlsx"
    )

    data_product_id = "wonder_metadata"
    environment = "dev"

    # Check if the expected results are available
    manifest_excel_file = schema.download_manifest_excel(
        alation_schema_id,
        config,
        excel_data_definition_file,
        data_product_id,
        environment,
    )

    assert len(str(manifest_excel_file)) > 1


def test_upload_manifest_json_databricks_zfi4():
    """
    Tests the method `upload_manifest_json` in the `alation_schema.Schema` class.

    This test ensures that the method uploads the schema manifest JSON file successfully. The test uses
    a file from the specified manifest directory (`ENVIRONMENT + "_manifest_downloads/"`) and uploads it using the
    `upload_manifest_json` method.

    Steps:
        1. Change the current working directory to the project root directory.
        2. Get the latest file from the manifest directory.
        3. Get the common configuration.
        4. Check if the file is a valid JSON file.
        5. Load the JSON data from the file.
        6. Upload the schema manifest JSON file using the `upload_manifest_json` method.
        7. Check that the response from the upload method is not an empty string.

    Raises:
        AssertionError: If the response from the upload method is an empty string.
    """

    # Change the current working directory to the project root directory
    os.chdir(project_root)

    obj_file = cdc_env_file.EnvironmentFile()
    app_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(app_dir)
    manifest_path = parent_dir + "/" + ENVIRONMENT + "_manifest_downloads/"
    manifest_file = obj_file.get_latest_file(manifest_path, "json")

    config = get_config(parameters)

    print(f"manifest_file: {str(manifest_file)}")
    valid_json = obj_file.is_valid_json(manifest_file)

    print(f"valid_json: {str(valid_json)}")

    with open(manifest_file, "r", encoding="utf-8") as f_manifest:
        metadata_json_data = json.load(f_manifest)

    schema = alation_schema.Schema()
    (
        content_result,
        authorized_tables_count,
        unauthorized_table_count,
    ) = schema.upload_manifest_json(metadata_json_data, config, "zfi4@cdc.gov")
    print(f"content_result: {str(content_result)}")
    # Check that the method behaved as expected
    assert len(str(content_result)) > 1


def test_upload_manifest_json_synapse_zfi4():
    """
    This function tests the `fetch_schema` method of the `alation_schema.Schema` class.

    The test procedure is as follows:

    1. The current working directory is changed to the project root directory.
    2. Configuration parameters are retrieved.
    3. An `alation_token_endpoint.TokenEndpoint` object is created and the `get_api_token_from_config` method is called.
    4. The lengths of the API access token and the refresh token are printed, and it is asserted that the status code is 200.
    5. The `fetch_schema` method of the `alation_schema.Schema` class is called.
    6. The status code and the results of the `fetch_schema` method are printed.
    7. It is asserted that the status code is 200.

    This function does not take any parameters or return any values. Its sole purpose is to perform the test and raise an exception if the test fails.

    Parameters
    ----------
    None

    Returns
    -------
    None
    """

    # Change the current working directory to the project root directory
    os.chdir(project_root)

    config = get_config(parameters)

    # Set the schema id
    alation_schema_id = 1464
    edc_alation_base_url = config.get("edc_alation_base_url")

    # Get the api token
    token_endpoint = alation_token_endpoint.TokenEndpoint(edc_alation_base_url)
    (
        status_code,
        edc_alation_api_token,
        api_refresh_token,
    ) = token_endpoint.get_api_token_from_config(config)
    print(f"api_refresh_token_length: {str(len(api_refresh_token))}")
    print(f"status_code: {str(status_code)}")

    # Get the schema object and name
    schema = alation_schema.Schema()
    # Get the schema and datasource details
    schema_result, datasource_result = schema.fetch_schema(
        edc_alation_api_token, edc_alation_base_url, alation_schema_id
    )

    # Get the file utility object
    obj_file = cdc_env_file.EnvironmentFile()

    # Set the schema name, datasource title and datasource_id

    schema_result_json = schema_result.json()
    schema_name = schema_result_json[0].get("name")
    datasource_title = datasource_result.get("title")
    prefix = (
        obj_file.scrub_file_name(datasource_title)
        + "_"
        + obj_file.scrub_file_name(schema_name)
    )

    # Get the manifest file
    app_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(app_dir)
    manifest_path = parent_dir + "/" + ENVIRONMENT + "_manifest_uploads/"
    manifest_path = obj_file.convert_to_current_os_dir(manifest_path)
    # Make sure you have put a file in the uploads directory
    manifest_file = obj_file.get_latest_file(manifest_path, "input.json", prefix)

    print(f"manifest_file: {str(manifest_file)}")
    valid_json = obj_file.is_valid_json(manifest_file)

    print(f"valid_json: {str(valid_json)}")

    with open(manifest_file, "r", encoding="utf-8") as f_manifest:
        metadata_json_data = json.load(f_manifest)

    (
        content_result,
        authorized_tables_count,
        unauthorized_table_count,
    ) = schema.upload_manifest_json(metadata_json_data, config, "zfi4@cdc.gov")

    assert len(content_result) > 0
    print(f"content_result: {str(content_result)}")
    # Check that the method behaved as expected


def test_upload_manifest_excel_synapse_knu1():
    """
    This function tests the `fetch_schema` method of the `alation_schema.Schema` class.

    The test procedure is as follows:

    1. The current working directory is changed to the project root directory.
    2. Configuration parameters are retrieved.
    3. An `alation_token_endpoint.TokenEndpoint` object is created and the `get_api_token_from_config` method is called.
    4. The lengths of the API access token and the refresh token are printed, and it is asserted that the status code is 200.
    5. The `fetch_schema` method of the `alation_schema.Schema` class is called.
    6. The status code and the results of the `fetch_schema` method are printed.
    7. It is asserted that the status code is 200.

    This function does not take any parameters or return any values. Its sole purpose is to perform the test and raise an exception if the test fails.

    Parameters
    ----------
    None

    Returns
    -------
    None
    """

    # Change the current working directory to the project root directory
    os.chdir(project_root)

    config = get_config(parameters)

    # Set the schema id
    alation_schema_id = 1464
    edc_alation_base_url = config.get("edc_alation_base_url")

    # Get the api token
    token_endpoint = alation_token_endpoint.TokenEndpoint(edc_alation_base_url)
    (
        status_code,
        edc_alation_api_token,
        api_refresh_token,
    ) = token_endpoint.get_api_token_from_config(config)
    print(f"api_refresh_token_length: {str(len(api_refresh_token))}")
    print(f"status_code: {str(status_code)}")

    # Get the schema object and name
    schema = alation_schema.Schema()
    # Get the schema and datasource details
    schema_result, datasource_result = schema.fetch_schema(
        edc_alation_api_token, edc_alation_base_url, alation_schema_id
    )

    # Get the file utility object
    obj_file = cdc_env_file.EnvironmentFile()

    # Set the schema name, datasource title and datasource_id

    schema_result_json = schema_result.json()
    schema_name = schema_result_json[0].get("name")
    datasource_title = datasource_result.get("title")
    prefix = (
        obj_file.scrub_file_name(datasource_title)
        + "_"
        + obj_file.scrub_file_name(schema_name)
    )

    # Get the manifest file
    app_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(app_dir)
    manifest_path = parent_dir + "/" + ENVIRONMENT + "_manifest_uploads/"
    manifest_path = obj_file.convert_to_current_os_dir(manifest_path)
    # Make sure you have put a file in the uploads directory
    manifest_excel_file = obj_file.get_latest_file(manifest_path, "input.xlsx", prefix)

    data_definition_path = parent_dir + "/" + ENVIRONMENT + "_data_definitions/"
    data_definition_path = obj_file.convert_to_current_os_dir(data_definition_path)
    json_data_definition_file_path = os.path.join(
        data_definition_path, "manifest.schema.json"
    )
    (
        content_result,
        authorized_tables_count,
        unauthorized_table_count,
    ) = schema.upload_manifest_excel(
        manifest_excel_file,
        config,
        json_data_definition_file_path,
        "sax5@cdc.gov",
    )

    assert len(content_result) > 0
    assert authorized_tables_count > 0
    assert unauthorized_table_count > 0
    print(f"content_result: {str(content_result)}")
    # Check that the method behaved as expected


def test_upload_manifest_excel_synapse_zfi4():
    """
    This function tests the `fetch_schema` method of the `alation_schema.Schema` class.

    The test procedure is as follows:

    1. The current working directory is changed to the project root directory.
    2. Configuration parameters are retrieved.
    3. An `alation_token_endpoint.TokenEndpoint` object is created and the `get_api_token_from_config` method is called.
    4. The lengths of the API access token and the refresh token are printed, and it is asserted that the status code is 200.
    5. The `fetch_schema` method of the `alation_schema.Schema` class is called.
    6. The status code and the results of the `fetch_schema` method are printed.
    7. It is asserted that the status code is 200.

    This function does not take any parameters or return any values. Its sole purpose is to perform the test and raise an exception if the test fails.

    Parameters
    ----------
    None

    Returns
    -------
    None
    """

    # Change the current working directory to the project root directory
    os.chdir(project_root)

    config = get_config(parameters)

    # Set the schema id
    alation_schema_id = 1464
    edc_alation_base_url = config.get("edc_alation_base_url")

    # Get the api token
    token_endpoint = alation_token_endpoint.TokenEndpoint(edc_alation_base_url)
    (
        status_code,
        edc_alation_api_token,
        api_refresh_token,
    ) = token_endpoint.get_api_token_from_config(config)
    print(f"api_refresh_token_length: {str(len(api_refresh_token))}")
    print(f"status_code: {str(status_code)}")

    # Get the schema object and name
    schema = alation_schema.Schema()
    # Get the schema and datasource details
    schema_result, datasource_result = schema.fetch_schema(
        edc_alation_api_token, edc_alation_base_url, alation_schema_id
    )

    # Get the file utility object
    obj_file = cdc_env_file.EnvironmentFile()

    # Set the schema name, datasource title and datasource_id

    schema_result_json = schema_result.json()
    schema_name = schema_result_json[0].get("name")
    datasource_title = datasource_result.get("title")
    prefix = (
        obj_file.scrub_file_name(datasource_title)
        + "_"
        + obj_file.scrub_file_name(schema_name)
    )

    # Get the manifest file
    app_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(app_dir)
    manifest_path = parent_dir + "/" + ENVIRONMENT + "_manifest_uploads/"
    manifest_path = obj_file.convert_to_current_os_dir(manifest_path)
    # Make sure you have put a file in the uploads directory
    manifest_excel_file = obj_file.get_latest_file(manifest_path, "input.xlsx", prefix)

    data_definition_path = parent_dir + "/" + ENVIRONMENT + "_data_definitions/"
    data_definition_path = obj_file.convert_to_current_os_dir(data_definition_path)
    json_data_definition_file_path = os.path.join(
        data_definition_path, "manifest.schema.json"
    )
    (
        content_result,
        authorized_tables_count,
        unauthorized_table_count,
    ) = schema.upload_manifest_excel(
        manifest_excel_file,
        config,
        json_data_definition_file_path,
        "zfi4@cdc.gov",
    )

    assert len(content_result) > 0
    print(f"content_result: {str(content_result)}")
    assert authorized_tables_count > 0
    assert unauthorized_table_count > 0


def fetch_schema_definitions():
    """
    Reads an Excel file containing a schema for SQL schemas from a specific location in the file system.

    The function first changes the current working directory to the project root directory, and then creates
    an instance of the EnvironmentFile class. It constructs a path to the file location based on the current
    environment and checks whether the file exists. The function reads the Excel file into a pandas DataFrame
    and returns the DataFrame and the file path.

    The function raises an AssertionError if the file does not exist.

    Returns:
        tuple: A tuple containing a pandas DataFrame representing the content of the Excel file and the path
        to the file.
    """
    # Change the current working directory to the project root directory
    os.chdir(project_root)
    # Get the file utility object
    obj_file = cdc_env_file.EnvironmentFile()

    # Get the manifest file
    app_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(app_dir)
    data_definition_path = parent_dir + "/" + ENVIRONMENT + "_data_definitions/"
    data_definition_path = obj_file.convert_to_current_os_dir(data_definition_path)
    # Make sure you have put a file in the uploads directory
    excel_data_definition_file = (
        data_definition_path + "excel_data_definition_for_schemas_sql.xlsx"
    )
    file_exists = obj_file.file_exists(True, excel_data_definition_file, None)
    assert file_exists is True
    # read the excel file
    df_table_fields_data_definition = pd.read_excel(excel_data_definition_file)
    return df_table_fields_data_definition, excel_data_definition_file


def test_fetch_schema_definitions():
    """
    Tests the function fetch_schema_definitions.

    The function first calls fetch_schema_definitions to obtain a DataFrame and the path of
    the Excel file. It then prints the DataFrame to the console. The main purpose of this test is to
    check if the function fetch_schema_definitions is running without errors and is able to read
    the Excel file and transform its content into a DataFrame.

    Note: This is a simple test and doesn't verify the correctness of the data in the DataFrame. You might
    want to add assertions to check the content of the DataFrame or the file path.
    """
    os.chdir(project_root)
    obj_file = cdc_env_file.EnvironmentFile()
    app_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(app_dir)
    data_definition_path = parent_dir + "/" + ENVIRONMENT + "_data_definitions/"
    data_definition_path = obj_file.convert_to_current_os_dir(data_definition_path)
    excel_data_definition_file = (
        data_definition_path + "excel_data_definition_for_tables_sql.xlsx"
    )
    table = alation_table.Table(None, excel_data_definition_file)
    (
        df_table_fields_data_definition,
        excel_data_definition_file,
    ) = table.fetch_table_definitions()
    print(df_table_fields_data_definition)


def test_fetch_schema_synapse():
    """
    This function tests the `fetch_schema` method of the `alation_schema.Schema` class for the Synapse platform.

    The test procedure is as follows:

    1. The current working directory is changed to the project root directory.
    2. Configuration parameters are retrieved.
    3. An `alation_token_endpoint.TokenEndpoint` object is created and the `get_api_token_from_config` method is called.
    4. The lengths of the API access token and the refresh token are printed, and it is asserted that the status code is 200.
    5. The `fetch_schema` method of the `alation_schema.Schema` class is called.
    6. The status code and the results of the `fetch_schema` method are printed.
    7. It is asserted that the status code is 200.

    This function does not take any parameters or return any values. Its sole purpose is to perform the test and raise an exception if the test fails.

    Parameters
    ----------
    None

    Returns
    -------
    None
    """

    # Change the current working directory to the project root directory
    os.chdir(project_root)

    config = get_config(parameters)

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

    # Call the method under test
    edc_alation_base_url = config.get("edc_alation_base_url")
    alation_schema_id = 1464
    schema = alation_schema.Schema()
    schema_result, datasource_result = schema.fetch_schema(
        edc_alation_api_token, edc_alation_base_url, alation_schema_id
    )

    schema_result_json = schema_result.json()
    custom_fields = schema_result_json[0].get("custom_fields")
    output_str, df_custom_fields = get_custom_fields_formatted(custom_fields)

    # Print the output string and the custom fields DataFrame
    print(output_str)
    print(df_custom_fields)

    # Creating DataFrame from the list of dictionaries
    df_fields_flat = pd.DataFrame(schema_result_json)

    # Convert the first row of the DataFrame to a list of tuples (name-value pairs)
    df_fields_list = list(df_fields_flat.iloc[0].items())

    # Create the DataFrame from the list of tuples
    df_fields = pd.DataFrame(df_fields_list, columns=["field_name", "field_value"])

    # Find the index of rows where 'field_name' is 'custom_fields'
    index_to_remove = df_fields[df_fields["field_name"] == "custom_fields"].index

    # Remove the rows with the specified index from the DataFrame in place
    df_fields.drop(index=index_to_remove, inplace=True)

    # Reset the index of the DataFrame in place
    print(f"status_code: {str(status_code)}")
    print(f"schema_result: {str(schema_result)}")
    print(f"datasource_result: {str(datasource_result)}")

    # Get the schema name, datasource title and datasource_id
    (
        df_table_fields_data_definition,
        excel_data_definition_file,
    ) = fetch_schema_definitions()

    # Print fields excel schema
    print(df_table_fields_data_definition)

    # Check that the method behaved as expected
    df_merged = df_fields.merge(
        df_table_fields_data_definition,
        left_on="field_name",
        right_on="column_name",
        how="left",
    )

    # Assert that the merged dataframe is not empty
    assert len(df_merged) > 0
    assert len(df_table_fields_data_definition) > 0

    df_merged.to_excel(
        excel_data_definition_file.replace(".xlsx", "_merged.xlsx"),
        index=False,
    )


def get_custom_fields_formatted(custom_fields):
    """
    Formats the custom fields from a schema result into a readable string.

    This function loops over the custom fields and builds a string that includes the keys and values of the fields.
    If a field's value is a list, the function enumerates over the list and includes the index in the key.

    The function then splits the resulting string into lines and loops over the lines. If a line represents a group profile,
    the function adds the group profile to a list. Otherwise, the line represents a field property and the function adds
    the property to a field information dictionary.

    The function then formats the field information and group profiles as a string and returns the string.

    Parameters
    ----------
    custom_fields : list
        A list of dictionaries, each representing a custom field from a schema result. Each dictionary includes a
        'field_id', 'field_name', and 'value' key.

    Returns
    -------
    str
        A string that represents the custom fields in a readable format. Each field is represented by its ID, name,
        and value, and each group profile is represented by its type and ID.
    """

    output_str = []
    custom_fields_list = []

    for field in custom_fields:
        result_str = ""  # initialize an empty string
        group_profiles = []

        # Initialize a new dictionary for each field in custom_fields
        field_info = {"field_id": "", "field_name": "", "value": None}

        # Process the field items
        for key, value in field.items():
            if isinstance(value, list):
                for i, item in enumerate(value):
                    result_str += f"Key: {key}[{i}], Value: {item}\n"
            else:
                result_str += f"Key: {key}, Value: {value}\n"

        # Split the input string into lines
        lines = result_str.split("\n")

        # Loop over the lines
        for line in lines:
            if not line.strip():  # Skip blank lines
                continue

            try:
                # Split the line into a key and a value
                key, value = line.split(", Value: ")
            except ValueError:
                output_str.append(f"Could not split line: {line}")
                continue

            # If this line represents a group profile value, add the group profile to the list
            if "value[0]" in key:
                try:
                    field_info[key] = eval(value)
                    group_profiles.append(eval(value))
                except Exception as e:
                    output_str.append(
                        f"Could not evaluate group profile: {value}. Error: {e}"
                    )
                    continue
            else:
                # Otherwise, this line represents a field property. Add the property to the field information dictionary.
                key = key.split("Key: ")[1]
                if (
                    "{" in value and "}" in value
                ):  # If value is a dict, use eval to parse it
                    try:
                        field_info[key] = eval(value)
                    except Exception as e:
                        output_str.append(
                            f"Could not evaluate dictionary: {value}. Error: {e}"
                        )
                        continue
                else:
                    # If value is not a dict, store it as a string
                    field_info[key] = value

        # After all parts of the field have been processed, append the field information to output_str
        output_str.append("")
        output_str.append(f"Field ID: {field_info['field_id']}")
        output_str.append(f"Field Name: {field_info['field_name']}")

        if field_info["value"] is None:
            # If the field value is None, add the array values to the output string
            gp_str = []
            for gp_array in group_profiles:
                gp_value = (
                    f"Group Profile - Type: {gp_array['otype']}, ID: {gp_array['oid']}"
                )
                output_str.append(gp_value)
                gp_str.append(gp_value)
            gp_str = "\n".join(gp_str)
            field_info["value"] = gp_str

            # Removing keys with '0' in the key name
            field_info = {
                key: value for key, value in field_info.items() if "0" not in key
            }

        else:
            # If the field value is not None, add it to the output string
            output_str.append(f"Value: {field_info['value']}")

        custom_fields_list.append(field_info)

    # Creating DataFrame from the list of dictionaries
    df_fields = pd.DataFrame(custom_fields_list)

    # Rename the 'old_column_name' to 'new_column_name'
    df_fields.rename(columns={"value": "field_value"}, inplace=True)

    # Remove the 'field_id' column from the DataFrame in place
    df_fields.drop(columns="field_id", inplace=True)

    # Join the parts of the output string with newline characters
    output_str = "\n".join(output_str)
    return output_str, df_fields


def test_fetch_schema_databricks():
    """
    This function tests the `fetch_schema` method of the `alation_schema.Schema` class for the Databricks platform.

    The test procedure includes the following steps:

    1. The current working directory is changed to the project root directory.
    2. Configuration parameters are retrieved.
    3. An `alation_token_endpoint.TokenEndpoint` object is created and the `get_api_token_from_config` method is called.
    4. The lengths of the API access token and the refresh token are printed, and it is asserted that the status code is 200.
    5. The `fetch_schema` method of the `alation_schema.Schema` class is called.
    6. The results of the `fetch_schema` method are printed.
    7. The custom fields from the schema result are extracted and printed in a human-readable format.
    8. It is asserted that the status code is 200 and the length of the datasource result is greater than 0.

    This function does not take any parameters or return any values. Its sole purpose is to perform the test and raise an exception if the test fails.

    Parameters
    ----------
    None

    Returns
    -------
    None
    """

    # Change the current working directory to the project root directory
    os.chdir(project_root)
    config = get_config(parameters)

    edc_alation_base_url = config.get("edc_alation_base_url")
    token_endpoint = alation_token_endpoint.TokenEndpoint(edc_alation_base_url)
    (
        status_code,
        edc_alation_api_token,
        api_refresh_token,
    ) = token_endpoint.get_api_token_from_config(config)

    # Check that the method behaved as expected
    assert status_code == 200

    # Print the length of the API access token and the refresh token
    print(f"edc_alation_api_access_token_length: {str(len(edc_alation_api_token))}")
    print(f"api_refresh_token_length: {str(len(api_refresh_token))}")

    # Set the parameters
    edc_alation_base_url = config.get("edc_alation_base_url")
    alation_schema_id = 106788
    schema = alation_schema.Schema()

    environment = config.get("environment")
    data_product_id = config.get("data_product_id")

    # Get the schema and datasource details
    schema_result, datasource_result = schema.fetch_schema(
        edc_alation_api_token,
        edc_alation_base_url,
        alation_schema_id,
        data_product_id,
        environment,
    )
    schema_result_json = schema_result.json()

    # Print the results
    print(f"schema_result: {str(schema_result)}")
    print(f"datasource_result: {str(datasource_result)}")

    # Set the option to display all columns
    pd.set_option("display.max_columns", None)

    # Get the custom fields from the schema result
    custom_fields = schema_result_json[0].get("custom_fields")
    output_str, df_custom_fields = get_custom_fields_formatted(custom_fields)

    # Print the custom fields
    print(output_str)
    print(df_custom_fields)

    # Creating DataFrame from the list of dictionaries
    df_fields_flat = pd.DataFrame(schema_result_json)

    # Convert the first row of the DataFrame to a list of tuples (name-value pairs)
    df_fields_list = list(df_fields_flat.iloc[0].items())

    # Create the DataFrame from the list of tuples
    df_fields = pd.DataFrame(df_fields_list, columns=["field_name", "field_value"])

    # Find the index of rows where 'field_name' is 'custom_fields'
    index_to_remove = df_fields[df_fields["field_name"] == "custom_fields"].index

    # Remove the rows with the specified index from the DataFrame in place
    df_fields.drop(index=index_to_remove, inplace=True)

    # Print the dataframe
    print(df_fields)

    # Check that the method behaved as expected
    assert status_code == 200
    assert len(str(datasource_result)) > 0


if __name__ == "__main__":
    pytest.main()
