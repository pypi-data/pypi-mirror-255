"""
This module interacts with Alation's data sources using the Alation API. It is designed to check, update, and get data from Alation's data sources in a controlled environment, particularly for the 'wonder_metadata_dev' project.

The module includes the following functions:

    get_config(parameters): This function retrieves configuration details based on the given parameters.

    test_check_datasource(): This function retrieves project parameters from environment variables, establishes a connection with Alation, and checks the existence of a particular data source. Asserts if the response status code is 200 (HTTP OK status - request has succeeded).

    test_update_datasource_title_description_databricks(): This function retrieves project parameters from environment variables, establishes a connection with Alation, updates the title and description of a particular data source and asserts if the response status code is 200.

    test_fetch_datasource_databricks(): This function retrieves project parameters from environment variables, establishes a connection with Alation, and retrieves the data source's details. It asserts if the response status code is 200 and if the title length of the data source is more than zero.

Dependencies:

    os, sys, dotenv, datetime, Path from pathlib: for environment and path manipulations.
    cdh_dav_python: a local module.
    alation_service from cdh_dav_python: a local module to interact with Alation.

Usage:

    Use the functions test_check_datasource(), test_update_datasource_title_description_databricks() and test_fetch_datasource_databricks() to interact with Alation's data sources.
    Ensure the '.env' file is properly set with required environment variables.

Note:

    This module requires environment variables to be properly set in the '.env' file.
    The functions in this module should be used for testing and development purposes only.
    """

import os
import sys
import pandas as pd

from pathlib import Path
from dotenv import load_dotenv
from cdh_dav_python.cdc_metadata_service import (
    environment_metadata as cdc_env_metadata,
)

import cdh_dav_python.alation_service.datasource as alation_datasource
import cdh_dav_python.alation_service.token as alation_token_endpoint

sys.path.append("..")

dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(dotenv_path)

ENVIRONMENT = "dev"


def get_config(parameters, data_product_id, environment):
    """
    Get the configuration for a specific data product and environment.

    Args:
        parameters (dict): A dictionary of parameters.
        data_product_id (str): The ID of the data product.
        environment (str): The environment to retrieve the configuration for.

    Returns:
        dict: The configuration for the specified data product and environment.
    """

    environment_metadata = cdc_env_metadata.EnvironmentMetaData()

    config = environment_metadata.get_configuration_common(
        parameters, None, data_product_id, environment
    )

    return config


def test_check_datasource():
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
    print(f"edc_alation_api_access_token_length: {str(len(edc_alation_api_token))}")
    print(f"api_refresh_token_length: {str(len(api_refresh_token))}")
    assert status_code == 200
    edc_alation_base_url = config.get("edc_alation_base_url")
    alation_datasource_id = 319

    datasource_name = "wonder_metadata_dev"

    # Make the POST API Call for the datasource
    datasource = alation_datasource.DataSource()
    datasource_result = datasource.check_datasource(
        edc_alation_api_token,
        edc_alation_base_url,
        alation_datasource_id,
        datasource_name,
    )

    status_code = datasource_result.status_code
    datasource_result.json = datasource_result.json()
    # Check that the method behaved as expected
    print(f"datasource_result: {str(datasource_result)}")
    assert status_code == 200


# def test_update_datasource_title_description_databricks():

#     # Retrieve the parameters from the environment variables
#     current_script_path = os.path.abspath(__file__)
#     project_root = os.path.dirname(os.path.dirname(current_script_path))
#     os.chdir(project_root)

#     repository_path_default = str(Path(os.getcwd()))
#     parameters = {
#         "data_product_id": "wonder_metadata_dev",
#         "data_product_id_root": "ocio",
#         "data_product_id_individual": "CDH",
#         "environment": "dev",
#         "repository_path": repository_path_default
#     }
#     config = get_config(parameters)

#     # Configure the Alation API Token and Parameters
#     edc_alation_base_url = config.get("edc_alation_base_url")
#     token_endpoint = alation_token_endpoint.TokenEndpoint(edc_alation_base_url)
#     status_code, edc_alation_api_token, api_refresh_token = token_endpoint.get_api_token_from_config(
#         config)
#     print(
#         f"edc_alation_api_access_token_length: {str(len(edc_alation_api_token))}")
#     print(f"api_refresh_token_length: {str(len(api_refresh_token))}")
#     assert status_code == 200
#     edc_alation_base_url = config.get("edc_alation_base_url")
#     alation_datasource_id = 319

#     # Get current time
#     now = datetime.now()

#     # Format time
#     time_string = now.strftime("%Y-%m-%d %H:%M:%S")
#     title = "DEV_CDH_PREMIER_EXPLORATORY (DataBricks)"
#     description = """<div>
# 	<div id="isPasted">
# 		<div>

# 			<h2>Upload Metadata for schema: wonder_metadata_dev</h2>

# 			<p>Click the &quot;Upload&quot; button below to upload a metadata file.</p>

# 			<p>Please ensure the file follows the specified format and contains accurate metadata information.</p><a href="http://127.0.0.1:5000/files/upload">Upload</a></div>
# 		<div>

# 			<h2>Download Metadata for schema: wonder_metadata_dev</h2>

# 			<p>Click the &quot;Download&quot; button below to download the metadata file.</p>

# 			<p>The file contains essential metadata information for reference and analysis purposes.</p><a href="http://127.0.0.1:5000/files/download" rel="noopener noreferrer" target="_blank">Download</a></div></div></div>"""

#     datasource_title = title + time_string
#     datasource_description = description + time_string

#     # Make the POST API Call for the datasource
#     datasource = alation_datasource.DataSource()
#     datasource_result = datasource.update_datasource(
#         edc_alation_api_token, edc_alation_base_url, alation_datasource_id, datasource_title, datasource_description)

#     status_code = datasource_result.status_code
#     # Check that the method behaved as expected
#     print(f"datasource_result: {str(datasource_result)}")
#     assert status_code == 200


def test_fetch_datasources():
    # Retrieve the parameters from the environment variables
    current_script_path = os.path.abspath(__file__)
    project_root = os.path.dirname(os.path.dirname(current_script_path))
    os.chdir(project_root)

    app_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(app_dir)

    query_download_path = parent_dir + "/" + ENVIRONMENT + "_query_downloads/"

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
    alation_datasource_id = -1

    # Make the GET API Call for the datasource
    datasource = alation_datasource.DataSource()
    df_datasources = datasource.fetch_datasources(
        edc_alation_api_token, edc_alation_base_url, alation_datasource_id
    )

    # Set download file path
    download_file_path = f"{query_download_path}/datasource_list_api.xlsx"

    # Sort by 'title' column
    # df_sorted = df_datasources.sort_values(by='title')
    df_sorted = df_datasources

    # Export to Excel
    with pd.ExcelWriter(download_file_path, engine="openpyxl") as writer:
        df_sorted.to_excel(writer, index=False, sheet_name="datasource_list")
        worksheet = writer.sheets["datasource_list"]

        # Assuming title is the first column, set its width to 150px
        # Approximate width of an Excel column is 1/7th the pixel width
        worksheet.column_dimensions["A"].width = 350 / 7

    # Check that the method behaved as expected
    print(f"df_datasources: {str(df_datasources)}")
    assert len(str(df_datasources)) > 0


def test_fetch_datasource_databricks():
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
    alation_datasource_id = 319

    # Make the GET API Call for the datasource
    datasource = alation_datasource.DataSource()
    datasource_result = datasource.fetch_datasource(
        edc_alation_api_token, edc_alation_base_url, alation_datasource_id
    )

    # Check that the method behaved as expected
    print(f"datasource_result: {str(datasource_result)}")
    status_code = datasource_result.status_code
    datasource_result_json = datasource_result.json()
    datasource_title = datasource_result_json.get("title")
    assert len(datasource_title) > 0
    assert status_code == 200
