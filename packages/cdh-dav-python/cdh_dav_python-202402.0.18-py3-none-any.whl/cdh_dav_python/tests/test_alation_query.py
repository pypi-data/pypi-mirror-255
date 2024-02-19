import os
import sys
import json
import pandas as pd

from pandas import json_normalize
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
from cdh_dav_python.cdc_metadata_service import (
    environment_metadata as cdc_env_metadata,
)
from cdh_dav_python.alation_service import (
    query as alation_query,
    token as alation_token_endpoint,
)
from cdh_dav_python.cdc_tech_environment_service import (
    environment_file as cdc_env_file,
)

sys.path.append("..")

dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(dotenv_path)

ENVIRONMENT = "dev"


def get_config(parameters, data_product_id, environment):
    """
    Retrieve the configuration based on the given parameters.

    Args:
        parameters (list or dict): The parameters used to determine the configuration.

    Returns:
        dict: The configuration retrieved based on the parameters.

    Raises:
        None

    Example:
        >>> params = [1, 2, 3]
        >>> get_config(params)
        {'param1': 1, 'param2': 2, 'param3': 3}
    """
    environment_metadata = cdc_env_metadata.EnvironmentMetaData()

    config = environment_metadata.get_configuration_common(
        parameters, None, data_product_id, environment
    )

    return config


def test_get_query_results_ocio_cdh_silver_user_group_membership():
    # Retrieve the parameters from the environment variables
    current_script_path = os.path.abspath(__file__)
    project_root = os.path.dirname(os.path.dirname(current_script_path))
    os.chdir(project_root)

    data_product_id = "wonder_metadata"
    data_product_id_root = "wonder"
    data_product_individual = "metadata"
    repository_path_default = str(Path(os.getcwd()))
    environment = "dev"

    parameters = {
        "data_product_id": data_product_id,
        "data_product_id_root": data_product_id_root,
        "data_product_id_individual": data_product_individual,
        "environment": environment,
        "repository_path": repository_path_default,
    }
    config = get_config(parameters, data_product_id, environment)

    # Change the current working directory to the project root directory
    os.chdir(project_root)

    app_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(app_dir)

    query_download_path = parent_dir + "/" + ENVIRONMENT + "_query_downloads/"

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
    # Alation analytics
    alation_datasource_id = 27
    query_id = 305  # ocio_cdh_silver_user_group_membership

    # Make the POST API Call for the datasource
    query = alation_query.Query()
    df_user_results = query.get_query_results(
        edc_alation_api_token,
        edc_alation_base_url,
        alation_datasource_id,
        query_id,
    )

    # Check that the method behaved as expected
    # Set display options
    pd.set_option("display.max_columns", None)  # or 1000
    pd.set_option("display.max_rows", None)  # or 1000
    pd.set_option("display.expand_frame_repr", False)
    pd.set_option("display.width", None)  # or 1000

    df_filtered = df_user_results

    # Set download file path
    download_file_path = f"{query_download_path}/alation_analytics_ocio_cdh_silver_user_group_membership.xlsx"

    # Export to Excel
    with pd.ExcelWriter(download_file_path, engine="openpyxl") as writer:
        df_filtered.to_excel(writer, index=False, sheet_name="query_list")
        worksheet = writer.sheets["query_list"]

        # Assuming title is the first column, set its width to 150px
        # Approximate width of an Excel column is 1/7th the pixel width
        worksheet.column_dimensions["A"].width = 350 / 7

    print(df_filtered)
    assert len(df_filtered) > 0


def test_get_query_results_ocio_cdh_silver_datasources():
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

    # Change the current working directory to the project root directory
    os.chdir(project_root)

    app_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(app_dir)

    query_download_path = parent_dir + "/" + ENVIRONMENT + "_query_downloads/"

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
    # Alation analytics
    alation_datasource_id = 27
    query_id = 283  # ocio_cdh_silver_users

    # Make the POST API Call for the datasource
    query = alation_query.Query()
    df_user_results = query.get_query_results(
        edc_alation_api_token,
        edc_alation_base_url,
        alation_datasource_id,
        query_id,
    )

    # Check that the method behaved as expected
    # Set display options
    pd.set_option("display.max_columns", None)  # or 1000
    pd.set_option("display.max_rows", None)  # or 1000
    pd.set_option("display.expand_frame_repr", False)
    pd.set_option("display.width", None)  # or 1000

    df_filtered = df_user_results

    # Set download file path
    download_file_path = (
        f"{query_download_path}/alation_analytics_ocio_cdh_silver_datasources.xlsx"
    )

    # Export to Excel
    with pd.ExcelWriter(download_file_path, engine="openpyxl") as writer:
        df_filtered.to_excel(writer, index=False, sheet_name="datasource_list")
        worksheet = writer.sheets["datasource_list"]

        # Assuming title is the first column, set its width to 150px
        # Approximate width of an Excel column is 1/7th the pixel width
        worksheet.column_dimensions["A"].width = 350 / 7

    print(df_filtered)
    assert len(df_filtered) > 0


def test_get_query_results_ocio_cdh_silver_users():
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

    # Change the current working directory to the project root directory
    os.chdir(project_root)

    app_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(app_dir)

    query_download_path = parent_dir + "/" + ENVIRONMENT + "_query_downloads/"

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
    # Alation analytics
    alation_datasource_id = 27
    query_id = 302  # ocio_cdh_silver_users

    # Make the POST API Call for the datasource
    query = alation_query.Query()
    df_user_results = query.get_query_results(
        edc_alation_api_token,
        edc_alation_base_url,
        alation_datasource_id,
        query_id,
    )

    # Check that the method behaved as expected
    # Set display options
    pd.set_option("display.max_columns", None)  # or 1000
    pd.set_option("display.max_rows", None)  # or 1000
    pd.set_option("display.expand_frame_repr", False)
    pd.set_option("display.width", None)  # or 1000

    df_filtered = df_user_results

    # Set download file path
    download_file_path = (
        f"{query_download_path}/alation_analytics_ocio_cdh_silver_users.xlsx"
    )

    # Export to Excel
    with pd.ExcelWriter(download_file_path, engine="openpyxl") as writer:
        df_filtered.to_excel(writer, index=False, sheet_name="query_list")
        worksheet = writer.sheets["query_list"]

        # Assuming title is the first column, set its width to 150px
        # Approximate width of an Excel column is 1/7th the pixel width
        worksheet.column_dimensions["A"].width = 350 / 7

    print(df_filtered)
    assert len(df_filtered) > 0


def test_get_query_results_ocio_cdh_silver_field_mapping_to_table():
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

    # Change the current working directory to the project root directory
    os.chdir(project_root)

    app_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(app_dir)

    query_download_path = parent_dir + "/" + ENVIRONMENT + "_query_downloads/"

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
    # Alation analytics
    alation_datasource_id = 27
    query_id = 298  # ocio_cdh_silver_users

    # Make the POST API Call for the datasource
    query = alation_query.Query()
    df_user_results = query.get_query_results(
        edc_alation_api_token,
        edc_alation_base_url,
        alation_datasource_id,
        query_id,
    )

    # Check that the method behaved as expected
    # Set display options
    pd.set_option("display.max_columns", None)  # or 1000
    pd.set_option("display.max_rows", None)  # or 1000
    pd.set_option("display.expand_frame_repr", False)
    pd.set_option("display.width", None)  # or 1000

    df_filtered = df_user_results

    # Set download file path
    download_file_path = f"{query_download_path}/alation_analytics_ocio_cdh_silver_field_mapping_to_table.xlsx"

    # Export to Excel
    with pd.ExcelWriter(download_file_path, engine="openpyxl") as writer:
        df_filtered.to_excel(writer, index=False, sheet_name="table_list")
        worksheet = writer.sheets["table_list"]

        # Assuming title is the first column, set its width to 150px
        # Approximate width of an Excel column is 1/7th the pixel width
        worksheet.column_dimensions["A"].width = 350 / 7

    print(df_filtered)
    assert len(df_filtered) > 0


def test_get_query_list():
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

    # Change the current working directory to the project root directory
    os.chdir(project_root)

    app_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(app_dir)

    query_download_path = parent_dir + "/" + ENVIRONMENT + "_query_downloads/"

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
    # Alation analytics
    alation_datasource_id = 27

    # Make the POST API Call for the datasource
    query = alation_query.Query()
    query_list_result_json = query.get_query_list(
        edc_alation_api_token, edc_alation_base_url, alation_datasource_id
    )

    df_query_list = json_normalize(query_list_result_json)
    # Filter rows where 'title' starts with 'ocio_cdh'
    df_filtered = df_query_list[df_query_list["title"].str.contains("ocio_cdh")]

    # Check that the method behaved as expected
    # Set display options
    pd.set_option("display.max_columns", None)  # or 1000
    pd.set_option("display.max_rows", None)  # or 1000
    pd.set_option("display.expand_frame_repr", False)
    pd.set_option("display.width", None)  # or 1000

    # Reorder columns to make 'title' the first column
    cols = df_filtered.columns.tolist()
    cols.insert(0, cols.pop(cols.index("title")))
    df_filtered = df_filtered[cols]

    # Filter rows where 'saved' is True
    # df_filtered = df_filtered[df_filtered['saved']]

    # Set download file path
    download_file_path = (
        f"{query_download_path}/query_list_alation_analytics_ocio_cdh.xlsx"
    )

    # Sort DataFrame by 'title'
    df_filtered = df_filtered.sort_values("title")

    # Sort by 'title' column
    df_sorted = df_filtered.sort_values(by="title")

    # Export to Excel
    with pd.ExcelWriter(download_file_path, engine="openpyxl") as writer:
        df_sorted.to_excel(writer, index=False, sheet_name="query_list")
        worksheet = writer.sheets["query_list"]

        # Assuming title is the first column, set its width to 150px
        # Approximate width of an Excel column is 1/7th the pixel width
        worksheet.column_dimensions["A"].width = 350 / 7

    print(df_filtered[["datasource_id", "id", "url", "title", "description", "saved"]])
    assert len(query_list_result_json) > 0
