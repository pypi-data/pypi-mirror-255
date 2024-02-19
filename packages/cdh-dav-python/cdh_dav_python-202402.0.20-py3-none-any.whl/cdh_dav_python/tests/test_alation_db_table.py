# if you get an error, on the command line type pip install requests
import os
import requests
import pandas as pd
import pytest

from pandas import json_normalize
from pathlib import Path

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

REPOSITORY_PATH_DEFAULT = str(Path(os.getcwd()))

parameters = {
    "data_product_id": "wonder_metadata_dev",
    "data_product_id_root": "ocio",
    "data_product_id_individual": "CDH",
    "environment": "dev",
    "repository_path": REPOSITORY_PATH_DEFAULT,
}


def get_config(parameters):
    environment_metadata = cdc_env_metadata.EnvironmentMetaData()

    config = environment_metadata.get_configuration_common(
        parameters, None, data_product_id, environment
    )

    return config


def test_fetch_schema_tables_synapse():
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
    config = get_config(parameters)
    alation_datasource_id = 150
    alation_schema_id = 1464
    pd.set_option("display.max_columns", None)

    edc_alation_base_url = config.get("edc_alation_base_url")
    token_endpoint = alation_token_endpoint.TokenEndpoint(edc_alation_base_url)
    (
        status_code,
        edc_alation_api_token,
        api_refresh_token,
    ) = token_endpoint.get_api_token_from_config(config)

    schema = alation_schema.Schema()

    schema_results, datasource_result = schema.fetch_schema(
        edc_alation_api_token, edc_alation_base_url, alation_schema_id
    )

    df_tables, tables_dict = table.fetch_schema_tables(
        edc_alation_api_token,
        edc_alation_base_url,
        alation_datasource_id,
        alation_schema_id,
        schema_results,
    )

    print(f"tables:{len(df_tables)}")
    assert len(df_tables) > 0
    # Printing columns of the DataFrame
    print(f"columns:{df_tables.columns}")
    # Printing columns of the DataFrame

    # Check and print custom fields
    if "custom_fields" in df_tables.columns:
        custom_fields = df_tables["custom_fields"]
        print(f"custom_fields: {str(custom_fields)}")
    else:
        print("custom_fields column does not exist.")

    num_columns = len(df_tables.columns)
    # ensure custom fields are included
    assert num_columns > 17


def test_fetch_schema_tables_databricks():
    """
    This function tests the `fetch_schema_tables` method of the `alation_schema.Schema` class for the Databricks platform.

    The test procedure includes the following steps:

    1. The current working directory is changed to the project root directory.
    2. Configuration parameters are retrieved.
    3. An `alation_token_endpoint.TokenEndpoint` object is created and the `get_api_token_from_config` method is called.
    4. The lengths of the API access token and the refresh token are printed.
    5. The `fetch_schema_tables` method of the `alation_schema.Schema` class is called.
    6. The returned tables dictionary is printed.
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

    # Print the length of the API access token and the refresh token
    print(f"api_refresh_token_length: {str(len(api_refresh_token))}")

    # Set the data source ID and the schema ID
    edc_alation_base_url = config.get("edc_alation_base_url")
    alation_datasource_id = 319
    alation_schema_id = 106788

    # Create a Schema object
    schema = alation_schema.Schema()

    edc_alation_base_url = config.get("edc_alation_base_url")
    token_endpoint = alation_token_endpoint.TokenEndpoint(edc_alation_base_url)
    (
        status_code,
        edc_alation_api_token,
        api_refresh_token,
    ) = token_endpoint.get_api_token_from_config(config)

    environment = config.get("environment")
    repository_path = config.get("repository_path")

    excel_data_definition_file = schema.get_excel_data_definition_file_path(
        repository_path, environment
    )

    table = alation_table.Table(None, excel_data_definition_file)

    schema = alation_schema.Schema()

    data_product_id = "wonder_metadata"

    schema_results, datasource_result = schema.fetch_schema(
        edc_alation_api_token,
        edc_alation_base_url,
        alation_schema_id,
        data_product_id,
        environment,
    )

    # Get the tables dictionary
    tables_dict = table.fetch_schema_tables(
        edc_alation_api_token,
        edc_alation_base_url,
        alation_datasource_id,
        alation_schema_id,
        schema_results,
    )

    # Print the tables dictionary
    print(f"tables_dict: {str(tables_dict)}")

    # Check that the method behaved as expected
    assert status_code == 200


def test_fetch_schema_tables_synapse2():
    """
    This function test_fetch_schema_tables_synapse() is a test method intended to validate the fetch_schema_tables method of the Schema class in the Alation module.

    This function first changes the current working directory to the project root directory and then retrieves the configuration parameters. It then uses these parameters to construct an TokenEndpoint object and makes a call to get_api_token_from_config method to get API tokens.

    Next, the function retrieves the base url for the Alation EDC from the configuration and uses these details to create a Schema object. A method call to fetch_schema_tables of the Schema object is then made with the API token, the base url, a hard-coded data source ID and a hard-coded schema ID.

    The function then prints out the resulting tables dictionary, which is a dictionary that maps table IDs to table names. Finally, it checks that the status code returned by the get_api_token_from_config method was 200, indicating a successful API call.

    Parameters:
    None

    Returns:
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

    print(f"api_refresh_token_length: {str(len(api_refresh_token))}")
    print(f"api_refresh_token_length: {str(len(api_refresh_token))}")

    # Call the method under test
    edc_alation_base_url = config.get("edc_alation_base_url")
    alation_datasource_id = 150
    alation_schema_id = 1464
    os.chdir(project_root)
    obj_file = cdc_env_file.EnvironmentFile()
    app_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(app_dir)
    data_definition_path = parent_dir + "/" + ENVIRONMENT + "_data_definitions/"
    data_definition_path = obj_file.convert_to_current_os_dir(data_definition_path)

    schema = alation_schema.Schema()

    schema_results, datasource_result = schema.fetch_schema(
        edc_alation_api_token,
        edc_alation_base_url,
        alation_schema_id,
        data_product_id,
        environment,
    )

    excel_data_definition_file = (
        data_definition_path + "excel_data_definition_for_tables_sql.xlsx"
    )
    table = alation_table.Table(None, excel_data_definition_file)
    tables_dict = table.fetch_schema_tables(
        edc_alation_api_token,
        edc_alation_base_url,
        alation_datasource_id,
        alation_schema_id,
        schema_results,
    )

    print(f"tables_dict: {str(tables_dict)}")
    # Check that the method behaved as expected
    assert status_code == 200


def test_fetch_schema_tables_dcipher():
    """
    This function, test_fetch_schema_tables_dcipher(), is a test method intended to validate
    the fetch_schema_tables method of the Schema class in the Alation module for the dCipher database.

    Initially, the function sets the current working directory to the project root and fetches
    the configuration parameters. With these parameters, it constructs a TokenEndpoint object
    and invokes the get_api_token_from_config method to obtain API tokens.

    Subsequently, the function fetches the base URL for the Alation EDC from the configuration
    and employs these details to instantiate a Schema object. A call to the fetch_schema_tables
    method of the Schema object is made, passing the API token, the base URL, a predefined
    data source ID, and a schema ID.

    The function outputs the resulting tables dictionary, which maps table IDs to table names.
    In the end, it verifies that the status code from the get_api_token_from_config method is
    200, signifying a successful API call.


    Note unlike the schema.fetch_table_and_columns method call which returns the full list of column metadata,
    this method returns only the table metadata explicity returned by Alation and does not populate missing
    custom fields in the case of null values.

    Parameters:
    None

    Returns:
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

    print(f"api_refresh_token_length: {str(len(api_refresh_token))}")

    # Call the method under test
    edc_alation_base_url = config.get("edc_alation_base_url")
    alation_datasource_id = 200
    alation_schema_id = 2649
    schema = alation_schema.Schema()
    environment = config.get("environment")
    os.chdir(project_root)
    obj_file = cdc_env_file.EnvironmentFile()
    app_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(app_dir)

    data_definition_path = parent_dir + "/" + ENVIRONMENT + "_data_definitions/"
    # Convert 'data_definition_path' to the current OS directory format
    data_definition_path = obj_file.convert_to_current_os_dir(data_definition_path)

    # Join the directory path and the filename using 'os.path.join()'
    json_excel_data_definition_file = os.path.join(
        data_definition_path, "manifest.schema.json"
    )
    table = alation_table.Table(None, json_excel_data_definition_file)

    data_product_id = config.get("data_product_id")
    environment = config.get("environment")

    schema_results, datasource_result = schema.fetch_schema(
        edc_alation_api_token,
        edc_alation_base_url,
        alation_schema_id,
        data_product_id,
        environment,
    )

    ds_tables, tables_dict = table.fetch_schema_tables(
        edc_alation_api_token,
        edc_alation_base_url,
        alation_datasource_id,
        alation_schema_id,
        schema_results,
    )

    print(f"tables_dict: {str(tables_dict)}")
    # Check that the method behaved as expected
    assert status_code == 200


def test_fetch_schema_tables_extended_synapse():
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
    config = get_config(parameters)

    edc_alation_base_url = config.get("edc_alation_base_url")
    token_endpoint = alation_token_endpoint.TokenEndpoint(edc_alation_base_url)
    (
        status_code,
        edc_alation_api_token,
        api_refresh_token,
    ) = token_endpoint.get_api_token_from_config(config)

    alation_datasource_id = 150
    alation_schema_id = 1464

    schema = alation_schema.Schema()

    schema_result, datasource_result = schema.fetch_schema(
        edc_alation_api_token, edc_alation_base_url, alation_schema_id
    )

    (
        df_tables_for_excel,
        hidden_fields,
        df_table_fields_data_definition,
    ) = table.fetch_schema_tables_extended(
        edc_alation_api_token,
        edc_alation_base_url,
        alation_datasource_id,
        alation_schema_id,
        schema_result,
    )
    pd.set_option("display.max_columns", None)
    print(df_tables_for_excel)
    assert len(df_tables_for_excel) > 0
    num_columns = len(df_tables_for_excel.columns)
    # ensure custom fields are included
    assert num_columns > 17


def test_fetch_schema_tables_extended_dcipher():
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
    config = get_config(parameters)

    edc_alation_base_url = config.get("edc_alation_base_url")
    token_endpoint = alation_token_endpoint.TokenEndpoint(edc_alation_base_url)
    (
        status_code,
        edc_alation_api_token,
        api_refresh_token,
    ) = token_endpoint.get_api_token_from_config(config)

    alation_datasource_id = 200
    alation_schema_id = 2649

    schema = alation_schema.Schema()

    schema_result, datasource_result = schema.fetch_schema(
        edc_alation_api_token, edc_alation_base_url, alation_schema_id
    )

    (
        df_tables_for_excel,
        hidden_fields,
        df_table_fields_data_definition,
    ) = table.fetch_schema_tables_extended(
        edc_alation_api_token,
        edc_alation_base_url,
        alation_datasource_id,
        alation_schema_id,
        schema_result,
    )
    pd.set_option("display.max_columns", None)
    print(df_tables_for_excel)
    assert len(df_tables_for_excel) > 0
    num_columns = len(df_tables_for_excel.columns)
    # ensure custom fields are included
    assert num_columns > 17


def test_fetch_table_definitions():
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
        df_fields_excel_table,
        excel_excel_data_definition_file,
    ) = table.fetch_table_definitions()
    print(df_fields_excel_table)


def test_get_editable_fields_from_data_definition_synapse():
    os.chdir(project_root)
    obj_file = cdc_env_file.EnvironmentFile()
    app_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(app_dir)

    data_definition_path = parent_dir + "/" + ENVIRONMENT + "_data_definitions/"
    # Convert 'data_definition_path' to the current OS directory format
    data_definition_path = obj_file.convert_to_current_os_dir(data_definition_path)

    # Join the directory path and the filename using 'os.path.join()'
    json_excel_data_definition_file = os.path.join(
        data_definition_path, "manifest.schema.json"
    )
    table = alation_table.Table(None, json_excel_data_definition_file)
    alation_datasource_id = 150
    alation_schema_id = 1464

    config = get_config(parameters)

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

    schema = alation_schema.Schema()
    data_product_id = config.get("data_product_id")
    environment = config.get("environment")

    schema_result, datasource_result = schema.fetch_schema(
        edc_alation_api_token,
        edc_alation_base_url,
        alation_schema_id,
        data_product_id,
        environment,
    )

    df_tables, tables_dict = table.fetch_schema_tables(
        edc_alation_api_token,
        edc_alation_base_url,
        alation_datasource_id,
        alation_schema_id,
        schema_result,
    )

    repository_path = config.get("repository_path")
    environment = config.get("environment")

    schema = alation_schema.Schema()
    excel_data_definition_file = schema.get_excel_data_definition_file_path(
        repository_path, environment
    )
    df_table_fields_data_definition = pd.read_excel(excel_data_definition_file)

    editable_fields = table.fetch_editable_fields(
        df_tables, df_table_fields_data_definition
    )
    print(editable_fields)
    assert len(editable_fields) > 0


def test_get_table_synapse():
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

    # setting the base_url so that all we need to do is swap API endpoints
    base_url = edc_alation_base_url
    # api access key
    api_key = edc_alation_api_token
    # setting up this access key to be in the headers
    headers = {"token": api_key}
    # api for tables
    api = "/integration/v2/table/"

    # Table Name to match
    target_table_name = "sdoh_education"

    limit = 500
    skip = 0

    # Create a dictionary to hold the parameters
    params = {}
    params["limit"] = limit
    params["skip"] = skip
    params["schema_id"] = 1464
    params["ds_id"] = 150

    # make the API call
    res = requests.get(base_url + api, headers=headers, params=params)
    # convert the response to a python dict.
    tables = res.json()

    table_key = ""
    table_id = 0

    # would recommend creating a function for this action
    # vs what we're doing in this guide
    for table in tables:
        # matching on Title to find the one that starts with what we need
        if table["name"].startswith(target_table_name):
            table_key = table["key"]
            table_id = table["id"]
            print('The Table key for "{}" is {}'.format(target_table_name, table_key))
            print('The Table id for "{}" is {}'.format(target_table_name, table_id))
            break

    print("Done with this section!")
    assert table_key != ""
    assert table_id != 0


if __name__ == "__main__":
    pytest.main()
