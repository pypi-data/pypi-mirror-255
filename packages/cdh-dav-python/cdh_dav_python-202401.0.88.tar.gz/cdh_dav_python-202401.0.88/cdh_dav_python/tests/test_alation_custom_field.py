import os
import sys
import json

from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
from cdh_dav_python.cdc_metadata_service import (
    environment_metadata as cdc_env_metadata,
)
from cdh_dav_python.alation_service import (
    custom_fields as alation_CustomFields,
    db_schema as alation_schema,
    db_table as alation_table,
    token as alation_token_endpoint,
)

sys.path.append("..")

dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(dotenv_path)

ENVIRONMENT = "dev"


def get_config(parameters):
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

    config = environment_metadata.get_configuration_common(parameters, None, data_product_id, environment)

    return config


def custom_field_update(
    object_type,
    alation_datasource_id,
    key,
    field_value,
    force_update,
    date_fields,
):
    """
    Updates a custom field for a given object in Alation.

    The function retrieves the necessary parameters from the environment variables and authenticates with the Alation API.
    It then calls the `update` method of the `CustomFields` class to update the custom field.

    Parameters
    ----------
    object_type : str
        The type of the object in Alation (e.g., 'schema', 'table', etc.).

    alation_datasource_id : int
        The ID of the Alation datasource where the object resides.

    key : str
        The key of the custom field to update.

    field_value : str
        The new value for the custom field.

    force_update : bool
        If True, the function will forcibly update the custom field even if it already has a value.

    Returns
    -------
    response_content : Response
        The response from the Alation API. This will include the status of the update operation and any relevant data.

    Raises
    ------
    AssertionError
        If the status code from the token endpoint is not 200, an AssertionError will be raised.
    """

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
    token_endpoint = alation_token_endpoint.TokenEndpoint(edc_alation_base_url)
    (
        status_code,
        edc_alation_api_token,
        api_refresh_token,
    ) = token_endpoint.get_api_token_from_config(config)
    print("status_code: ", status_code)
    custom_fields_endpoint = alation_CustomFields.CustomFields()

    editable_fields = ["description", "title", "Access Level"]
    response_content = custom_fields_endpoint.update(
        edc_alation_api_token,
        edc_alation_base_url,
        object_type,
        alation_datasource_id,
        key,
        field_value,
        force_update,
        editable_fields,
        date_fields,
    )
    return response_content


# def test_customfield_get_all():

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
#     token_endpoint = alation_token_endpoint.TokenEndpoint(edc_alation_base_url)
#     status_code, edc_alation_api_token, api_refresh_token = token_endpoint.get_api_token_from_config(
#         config)
#     print("status_code: ", status_code)
#     custom_fields_endpoint = alation_CustomFields.CustomFields()

#     response_content = custom_fields_endpoint.get_custom_fields(
#         edc_alation_api_token, edc_alation_base_url)

#     # Confirm results
#     response_status = response_content[0]['status']
#     response_message = response_content[0]['message']
#     response_content_json = response_content[1]
#     assert response_status == "success"
#     assert len(response_message) > 0
#     assert len(str(response_content_json)) > 0


def test_customfield_update_schema_title_description_synapse():
    """
    This function tests the update of the title and description custom fields for a schema object in a Synapse datasource.

    The test procedure includes the following steps:

    1. Retrieve the parameters from the environment variables.
    2. Define the Alation Datasource ID, the schema name, and the current time.
    3. Construct the title and description for the schema using HTML code.
    4. Call the `custom_field_update` function to update the title and description custom fields of the specified schema.
    5. Verify the results. Assert that the status of the response is "success", and that the response message and the JSON response content have a length greater than zero.

    This function does not take any parameters or return any values. Its sole purpose is to perform the test and raise an exception if the test fails.

    Parameters
    ----------
    None

    Returns
    -------
    None

    Raises
    ------
    AssertionError
        If the status of the response is not "success", or if the response message or the JSON response content are empty, an AssertionError will be raised.
    """

    current_script_path = os.path.abspath(__file__)
    project_root = os.path.dirname(os.path.dirname(current_script_path))
    os.chdir(project_root)
    alation_datasource_id = 150
    schema_name = "EDAV.alation"
    key = schema_name
    now = datetime.now()
    time_string = now.strftime("%Y-%m-%d %H:%M:%S")

    title = f"schema: {schema_name} - {time_string}"
    html_code = f"""
  <div class="instructions">
    <h2>Upload Metadata for schema: {schema_name}</h2>
    <p>Click the "Upload" button below to upload a metadata file.</p>
    <p>Please ensure the file follows the specified format and contains accurate metadata information.</p>
    <a href="http://127.0.0.1:5000/pages/upload" class="button">Upload</a>
  </div>

  <div class="instructions">
    <h2>Download Metadata for schema: {schema_name}</h2>
    <p>Click the "Download" button below to download the metadata file.</p>
    <p>The file contains essential metadata information for reference and analysis purposes.</p>
    <a href="http://127.0.0.1:5000/pages/download" class="button">Download</a>
  </div>
"""
    description = html_code
    field_value = {"title": title, "description": description}

    date_fields = []

    response_content = custom_field_update(
        "schema", alation_datasource_id, key, field_value, True, date_fields
    )

    # Confirm results
    response_status = response_content[0]["status"]
    response_message = response_content[0]["message"]
    response_content_json = response_content[1]
    assert response_status == "success"
    assert len(response_message) > 0
    assert len(str(response_content_json)) > 0


def test_customfield_update_schema_title_description_databricks():
    """
    This function tests the update of the title and description custom fields for a schema object in a Databricks datasource.

    The test procedure includes the following steps:

    1. Define the Alation Datasource ID, the schema name, and the current time.
    2. Check if the schema name contains a period. If it does, encode the schema name by adding double quotes around it.
    3. Construct the title and description for the schema using HTML code.
    4. Call the `custom_field_update` function to update the title and description custom fields of the specified schema.
    5. Verify the results. Assert that the status of the response is "success", and that the response message and the JSON response content have a length greater than zero.

    This function does not take any parameters or return any values. Its sole purpose is to perform the test and raise an exception if the test fails.

    Parameters
    ----------
    None

    Returns
    -------
    None

    Raises
    ------
    AssertionError
        If the status of the response is not "success", or if the response message or the JSON response content are empty, an AssertionError will be raised.
    """

    # Retrieve the parameters from the environment variables
    alation_datasource_id = 319
    schema_name = "wonder_metadata_dev"
    encode_period = True
    key = schema_name
    now = datetime.now()
    time_string = now.strftime("%Y-%m-%d %H:%M:%S")

    if encode_period and "." in schema_name:
        encoded_schema_name = f'"{schema_name}"'
    else:
        encoded_schema_name = schema_name

    key = encoded_schema_name
    title = f"schema: {schema_name}: {time_string}"
    html_code = f"""
  <div class="instructions">
    <h2>Upload Metadata for schema: {schema_name}</h2>
    <p>Click the "Upload" button below to upload a metadata file.</p>
    <p>Please ensure the file follows the specified format and contains accurate metadata information.</p>
    <a href="http://127.0.0.1:5000/pages/upload" class="button">Upload</a>
  </div>

  <div class="instructions">
    <h2>Download Metadata for schema: {schema_name}</h2>
    <p>Click the "Download" button below to download the metadata file.</p>
    <p>The file contains essential metadata information for reference and analysis purposes.</p>
    <a href="http://127.0.0.1:5000/pages/download" class="button">Download</a>
  </div>
"""

    description = html_code
    field_value = {"title": title, "description": description}

    date_fields = []

    response_content = custom_field_update(
        "schema", alation_datasource_id, key, field_value, True, date_fields
    )

    # Confirm Results
    response_status = response_content[0]["status"]
    response_message = response_content[0]["message"]
    response_content_json = response_content[1]
    assert response_status == "success"
    assert len(response_message) > 0
    assert len(str(response_content_json)) > 0


def test_customfield_update_table_title_description_batch_two_synapse():
    """
    This function tests the update of the title and description custom fields for two tables in a Synapse datasource.

    The test procedure includes the following steps:

    1. Define the Alation Datasource ID and the current time.
    2. Construct a JSON string for two tables with their keys, names, titles, and descriptions.
    3. Retrieve the parameters from the environment variables.
    4. Configure the Alation API Token and Parameters.
    5. Assert that the status code is 200.
    6. Load the JSON data and initialize a dictionary to hold the tables.
    7. Loop over each table in the dictionary, updating the table structure and custom fields for each table.
    8. Verify that the number of items in the dictionary is greater than zero.

    This function does not take any parameters or return any values. Its sole purpose is to perform the test and raise an exception if the test fails.

    Parameters
    ----------
    None

    Returns
    -------
    None

    Raises
    ------
    AssertionError
        If the status code is not 200, or if the number of items in the dictionary is not greater than zero, an AssertionError will be raised.
    """

    alation_datasource_id = 150
    # Get current time
    now = datetime.now()
    time_string = now.strftime("%Y %m %d %H %M %S")

    json_data = f"""[
        {{
            "key": "150.EDAV.alation.customers",
            "name": "customers",
            "title": "Customers {time_string}",
            "description": "Customers {time_string}"
        }},
        {{
            "key": "150.EDAV.alation.orders",
            "name": "orders",
            "title": "Orders {time_string}",
            "description": "Orders {time_string}"
        }}
    ]"""

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
    if status_code == 200 or status_code == 201:
        print(f"edc_alation_api_access_token_length: {str(len(edc_alation_api_token))}")
        print(f"api_refresh_token_length: {str(len(api_refresh_token))}")
    assert status_code == 200

    # Load the JSON data
    data_definition_file_path = config.get("edc_json_schema_location")
    table_dict = json.loads(json_data)

    total_items = len(table_dict)
    tables = {
        table.name: table
        for table in map(
            lambda t: alation_table.Table(t, data_definition_file_path),
            table_dict,
        )
    }

    # reinit endpoint
    obj_custom_fields_endpoint = alation_CustomFields.CustomFields()
    schema_name = "EDAV.alation"

    editable_fields = ["description", "title"]
    date_fields = ["Metadata Last Updated", "Last Update"]

    for idx, (key, table) in enumerate(tables.items()):
        # Check if my_object is of type 'Table'
        if isinstance(table, alation_table.Table):
            table = vars(table)

        # If key exists and table name is not set, set the table name from key
        if "key" in table:
            # Split the key to get the last part
            key_parts = table["key"].split(".")
            table_name = key_parts[-2]
        elif "table_name" in table:
            # Use the object table_name if it exists
            if table.table_name:
                table_name = table.table_name
            else:
                table_name = table.name
        else:
            # Use the dictionary key as the table name
            table_name = key

        # Add "table_name" to the dictionary if it does not exist
        table.setdefault("table_name", table_name)
        table.setdefault("name", table_name)

        force_submit = idx == total_items - 1
        schema = alation_schema.Schema()
        table_result = table.update_table_structure(
            edc_alation_api_token,
            edc_alation_base_url,
            alation_datasource_id,
            schema_name,
            table,
            force_submit=force_submit,
            obj_custom_fields_endpoint=obj_custom_fields_endpoint,
            editable_fields=editable_fields,
            table_name=table_name,
            date_fields=date_fields,
        )
        print(f"table_result: {table_result}")
    assert total_items > 0


def get_property_name(data):
    if isinstance(data, dict):
        if "table_name" in data:
            return "table_name"
        elif "name" in data:
            return "name"
        elif "key" in data:
            return "key"
    else:  # Assuming data is an object
        if hasattr(data, "table_name"):
            return "table_name"
        elif hasattr(data, "name"):
            return "name"
        elif hasattr(data, "key"):
            return "key"
    return None


def get_table_key_value(table, table_key):
    if isinstance(table, dict):
        return table[table_key]
    elif hasattr(table, table_key):
        return getattr(table, table_key)
    else:
        raise ValueError(f"'{table_key}' not found in the object or dictionary.")


def test_customfield_update_table_title_description_batch_two_no_name_synapse():
    """
    This function tests the update of the title and description custom fields for two tables in a Synapse datasource.

    The test procedure includes the following steps:

    1. Define the Alation Datasource ID and the current time.
    2. Construct a JSON string for two tables with their keys, names, titles, and descriptions.
    3. Retrieve the parameters from the environment variables.
    4. Configure the Alation API Token and Parameters.
    5. Assert that the status code is 200.
    6. Load the JSON data and initialize a dictionary to hold the tables.
    7. Loop over each table in the dictionary, updating the table structure and custom fields for each table.
    8. Verify that the number of items in the dictionary is greater than zero.

    This function does not take any parameters or return any values. Its sole purpose is to perform the test and raise an exception if the test fails.

    Parameters
    ----------
    None

    Returns
    -------
    None

    Raises
    ------
    AssertionError
        If the status code is not 200, or if the number of items in the dictionary is not greater than zero, an AssertionError will be raised.
    """

    alation_datasource_id = 150
    # Get current time
    now = datetime.now()
    time_string = now.strftime("%Y %m %d %H %M %S")

    json_data = f"""[
        {{
            "key": "150.EDAV.alation.customers",
            "title": "Customers {time_string}",
            "description": "Customers {time_string}"
        }},
        {{
            "key": "150.EDAV.alation.orders",
            "title": "Orders {time_string}",
            "description": "Orders {time_string}"
        }}
    ]"""

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
    if status_code == 200 or status_code == 201:
        print(f"edc_alation_api_access_token_length: {str(len(edc_alation_api_token))}")
        print(f"api_refresh_token_length: {str(len(api_refresh_token))}")
    assert status_code == 200

    # Load the JSON data
    data_definition_file_path = config.get("edc_json_schema_location")
    table_dict = json.loads(json_data)
    total_items = len(table_dict)

    table_key = get_property_name(table_dict[0])

    tables = {
        get_table_key_value(table, table_key): table
        for table in map(
            lambda t: alation_table.Table(t, data_definition_file_path),
            table_dict,
        )
    }

    # reinit endpoint
    obj_custom_fields_endpoint = alation_CustomFields.CustomFields()
    schema_name = "EDAV.alation"

    editable_fields = ["description", "title"]
    date_fields = ["Metadata Last Updated", "Last Update"]

    for idx, (key, table) in enumerate(tables.items()):
        table_name = key

        # If key exists and table name is not set, set the table name from key
        if isinstance(table, dict) and "key" in table:
            # Split the key to get the last part
            key_parts = table["key"].split(".")
            table_name = key_parts[-2]
        elif isinstance(table, alation_table.Table):
            # Use the object table_name if it exists
            if hasattr(table, "table_name") and table.table_name is not None:
                table_name = table.table_name
            elif (
                hasattr(table, "name")
                and table.name is not None
                and table.table_name is None
            ):
                table_name = table.name

            table = vars(table)
        else:
            # Use the dictionary key as the table name
            table_name = key

        if not table_name:
            table_name = key

        # Add "table_name" to the dictionary if it does not exist
        table.setdefault("table_name", table_name)
        table.setdefault("name", table_name)

        force_submit = idx == total_items - 1
        schema = alation_schema.Schema()
        table_result = table.update_table_structure(
            edc_alation_api_token,
            edc_alation_base_url,
            alation_datasource_id,
            schema_name,
            table,
            force_submit=force_submit,
            obj_custom_fields_endpoint=obj_custom_fields_endpoint,
            editable_fields=editable_fields,
            table_name=table_name,
            date_fields=date_fields,
        )
        print(f"table_result: {table_result}")
    assert total_items > 0


def test_customfield_update_attribute_title_description_batch_two_synapse():
    """
    This function tests the update of the title and description custom fields for two tables in a Synapse datasource.

    The test procedure includes the following steps:

    1. Define the Alation Datasource ID and the current time.
    2. Construct a JSON string for two tables with their keys, names, titles, and descriptions.
    3. Retrieve the parameters from the environment variables.
    4. Configure the Alation API Token and Parameters.
    5. Assert that the status code is 200.
    6. Load the JSON data and initialize a dictionary to hold the tables.
    7. Loop over each table in the dictionary, updating the table structure and custom fields for each table.
    8. Verify that the number of items in the dictionary is greater than zero.

    This function does not take any parameters or return any values. Its sole purpose is to perform the test and raise an exception if the test fails.

    Parameters
    ----------
    None

    Returns
    -------
    None

    Raises
    ------
    AssertionError
        If the status code is not 200, or if the number of items in the dictionary is not greater than zero, an AssertionError will be raised.
    """

    alation_datasource_id = 150
    # Get current time
    now = datetime.now()

    json_data = f"""[
        {{"key":"150.EDAV.alation.orders.title","title":"Orders 2023-08-03 06:30:35"}},
        {{"key":"150.EDAV.alation.orders.description","description":"Orders description"}}
    ]"""

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
    if status_code == 200 or status_code == 201:
        print(f"edc_alation_api_access_token_length: {str(len(edc_alation_api_token))}")
        print(f"api_refresh_token_length: {str(len(api_refresh_token))}")
    assert status_code == 200

    # Load the JSON data
    data_definition_file_path = config.get("edc_json_schema_location")
    table_dict = json.loads(json_data)

    # Update the list with a new field "field_name" containing the last part of the key
    for item in table_dict:
        # Split the key to get the last part
        key_parts = item["key"].split(".")
        table_name = key_parts[-2]

        # Add "table_name" to the dictionary if it does not exist
        item.setdefault("table_name", table_name)
        item.setdefault("name", table_name)

    total_items = len(table_dict)
    tables = {
        table.name: table
        for table in map(
            lambda t: alation_table.Table(t, data_definition_file_path),
            table_dict,
        )
    }

    # reinit endpoint
    obj_custom_fields_endpoint = alation_CustomFields.CustomFields()
    schema_name = "EDAV.alation"

    editable_fields = ["description", "title"]
    date_fields = []

    for idx, (table_name, table) in enumerate(tables.items()):
        force_submit = idx == total_items - 1
        schema = alation_schema.Schema()

        table_result = table.update_table_structure(
            edc_alation_api_token,
            edc_alation_base_url,
            alation_datasource_id,
            schema_name,
            table,
            force_submit=force_submit,
            obj_custom_fields_endpoint=obj_custom_fields_endpoint,
            editable_fields=editable_fields,
            table_name=table_name,
            date_fields=date_fields,
        )

        print(f"table_result: {table_result}")
    assert total_items > 0


def test_customfield_update_table_title_description_batch_two_databricks():
    """
    This function tests the update of the title and description custom fields for two tables in a Databricks datasource.

    The test procedure includes the following steps:

    1. Define the Alation Datasource ID and the schema name.
    2. Construct a JSON string for two tables with their keys, names, titles, and descriptions.
    3. Retrieve the parameters from the environment variables.
    4. Configure the Alation API Token and Parameters.
    5. Assert that the status code is 200.
    6. Load the JSON data and initialize a dictionary to hold the tables.
    7. Loop over each table in the dictionary, updating the table structure and custom fields for each table.
    8. Verify that the response content is not empty.

    This function does not take any parameters or return any values. Its sole purpose is to perform the test and raise an exception if the test fails.

    Parameters
    ----------
    None

    Returns
    -------
    None

    Raises
    ------
    AssertionError
        If the status code is not 200, or if the response content is empty, an AssertionError will be raised.
    """

    alation_datasource_id = 319
    schema_name = "wonder_metadata_dev"

    json_data = """[
        {"key": "319.wonder_metadata_dev.bronze_phvs_translation_valuesets", "title": "title -  2023-07-05 11:51", "description": "<p>description -  2023-07-05 11:51</p>"},
        {"key": "319.wonder_metadata_dev.bronze_cns_fips_county_population", "title": "title -  2023-07-05 11:51", "description": "<p>description -  2023-07-05 11:51</p>"}
        ]"""

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
    obj_custom_fields_endpoint = alation_CustomFields.CustomFields()

    token_endpoint = alation_token_endpoint.TokenEndpoint(edc_alation_base_url)
    (
        status_code,
        edc_alation_api_token,
        api_refresh_token,
    ) = token_endpoint.get_api_token_from_config(config)
    if status_code == 200 or status_code == 201:
        print(f"edc_alation_api_access_token_length: {str(len(edc_alation_api_token))}")
        print(f"api_refresh_token_length: {str(len(api_refresh_token))}")
    assert status_code == 200

    data_definition_file_path = config.get("edc_json_schema_location")
    # Load the JSON data

    table_dict = json.loads(json_data)
    # Update the list with a new field "field_name" containing the last part of the key
    for item in table_dict:
        key_parts = item["key"].split(".")
        item["table_name"] = key_parts[-1]
        item["name"] = key_parts[-1]

    tables = {
        table.name: table
        for table in map(
            lambda t: alation_table.Table(t, data_definition_file_path),
            table_dict,
        )
    }

    date_fields = []
    editable_fields = ["description", "title"]
    for idx, (table_name, table) in enumerate(tables.items()):
        schema = alation_schema.Schema()
        is_last = idx == len(table_dict) - 1
        response_content = schema.update_table_structure(
            edc_alation_api_token,
            edc_alation_base_url,
            alation_datasource_id,
            schema_name,
            table,
            force_submit=is_last,
            obj_custom_fields_endpoint=obj_custom_fields_endpoint,
            editable_fields=editable_fields,
            table_name=table_name,
            date_fields=date_fields,
        )
        print(f"response_content: {response_content}")
    assert len(response_content) > 0


def test_customfield_update_table_access_level_single_synapse():
    """
    This function tests the update of the title and description custom fields for a single table in a Synapse datasource.

    The test procedure includes the following steps:

    1. Define the Alation Datasource ID and the key for the table.
    2. Get the current time and format it.
    3. Construct the title and description fields using the key and the formatted time.
    4. Call the custom_field_update function to update the title and description fields for the table.
    5. Extract the status, message, and content from the response.
    6. Assert that the status is "success", and that the message and content are not empty.

    This function does not take any parameters or return any values. Its sole purpose is to perform the test and raise an exception if the test fails.

    Parameters
    ----------
    None

    Returns
    -------
    None

    Raises
    ------
    AssertionError
        If the status is not "success", or if the message or content are empty, an AssertionError will be raised.
    """

    alation_datasource_id = 150
    key = "EDAV.alation.customers"
    access_level = "non-public"
    date_fields = []

    # Add to description
    field_value = {"Access Level": access_level}
    object_type = "table"
    response_content = custom_field_update(
        object_type, alation_datasource_id, key, field_value, True, date_fields
    )
    response_status = response_content[0]["status"]
    response_message = response_content[0]["message"]
    response_content_json = response_content[1]
    assert response_status == "success"
    assert len(response_message) > 0
    assert len(str(response_content_json)) > 0


def test_customfield_update_table_title_description_single_synapse():
    """
    This function tests the update of the title and description custom fields for a single table in a Synapse datasource.

    The test procedure includes the following steps:

    1. Define the Alation Datasource ID and the key for the table.
    2. Get the current time and format it.
    3. Construct the title and description fields using the key and the formatted time.
    4. Call the custom_field_update function to update the title and description fields for the table.
    5. Extract the status, message, and content from the response.
    6. Assert that the status is "success", and that the message and content are not empty.

    This function does not take any parameters or return any values. Its sole purpose is to perform the test and raise an exception if the test fails.

    Parameters
    ----------
    None

    Returns
    -------
    None

    Raises
    ------
    AssertionError
        If the status is not "success", or if the message or content are empty, an AssertionError will be raised.
    """

    alation_datasource_id = 150
    # Get current time
    now = datetime.now()

    # Format time
    time_string = now.strftime("%Y-%m-%d %H:%M:%S")

    key = "EDAV.alation.customers"

    # Add to title
    title = f"{key} title - {time_string}"

    date_fields = []

    # Add to description
    description = f"{key} description - {time_string}"
    field_value = {"title": title, "description": description}
    object_type = "table"
    response_content = custom_field_update(
        object_type, alation_datasource_id, key, field_value, True, date_fields
    )
    response_status = response_content[0]["status"]
    response_message = response_content[0]["message"]
    response_content_json = response_content[1]
    assert response_status == "success"
    assert len(response_message) > 0
    assert len(str(response_content_json)) > 0


def test_customfield_update_table_title_description_single_databricks():
    alation_datasource_id = 319
    # Get current time
    now = datetime.now()

    # Format time
    time_string = now.strftime("%Y-%m-%d %H:%M:%S")

    # Add to title
    title = f"bronze_config_datasets title - {time_string}"

    # Add to description
    description = f"bronze_config_datasets description - {time_string}"

    date_fields = []

    key = "wonder_metadata_dev.bronze_config_datasets"
    field_value = {"title": title, "description": description}
    object_type = "table"
    response_content = custom_field_update(
        object_type, alation_datasource_id, key, field_value, True, date_fields
    )
    response_status = response_content[0]["status"]
    response_message = response_content[0]["message"]
    response_content_json = response_content[1]
    assert response_status == "success"
    assert len(response_message) > 0
    assert len(str(response_content_json)) > 0


def test_customfield_update_attribute_title_description_single():
    alation_datasource_id = 319

    # Get current time
    now = datetime.now()

    # Format time
    time_string = now.strftime("%Y-%m-%d %H:%M:%S")

    date_fields = []

    # Add to title
    title = f"compare_table title - {time_string}"
    description = f"compare_table description - {time_string}"
    key = "wonder_metadata_dev.bronze_config_datasets.compare_table"
    field_value = {"title": title, "description": description}
    object_type = "attribute"
    response_content = custom_field_update(
        object_type, alation_datasource_id, key, field_value, True, date_fields
    )
    response_status = response_content[0]["status"]
    response_message = response_content[0]["message"]
    response_content_json = response_content[1]
    assert response_status == "success"
    assert len(response_message) > 0
    assert len(str(response_content_json)) > 0


def test_customfield_update_attribute_title_description_single_special_chars_databricks():
    alation_datasource_id = 319

    alation_datasource_id = 319

    # Get current time
    now = datetime.now()
    time_string = now.strftime("%Y-%m-%d %H:%M:%S")

    # Set key to update
    schema_name = "wonder_metadata_dev"
    encode_period = True
    if encode_period:
        encoded_schema_name = f'"{schema_name}"'
    else:
        encoded_schema_name = schema_name

    table_name = "bronze_cns_fips_county_population"
    if encode_period:
        encoded_table_name = table_name.replace(".", "%2E")
    else:
        encoded_table_name = table_name

    column_name = "annotation_of_estimate!!hispanic_or_latino_and_race!!total_population!!hispanic_or_latino_of_any_race!!other_hispanic_or_latino"
    if encode_period:
        encoded_column_name = column_name.replace(".", "%2E")
    else:
        encoded_column_name = column_name

    key = f"{encoded_schema_name}.{encoded_table_name}.{encoded_column_name}"

    date_fields = []

    # Add to title
    title = f"updated title - {time_string}"
    description = f"updated description - {time_string}"
    field_value = {"title": title, "description": description}
    object_type = "attribute"
    response_content = custom_field_update(
        object_type, alation_datasource_id, key, field_value, True, date_fields
    )
    response_status = response_content[0]["status"]
    response_message = response_content[0]["message"]
    response_content_json = response_content[1]
    assert response_status == "success"
    assert len(response_message) > 0
    assert len(str(response_content_json)) > 0


def test_customfield_update_attribute_title_description_batch_two_specials_chars_synapse():
    alation_datasource_id = 150
    # Get current time
    now = datetime.now()
    time_string = now.strftime("%Y-%m-%d %H:%M:%S")

    json_data = f"""[
        {{"key":"150.EDAV.alation.sdoh_race.title","title":"Race Demo  - 2"}},
        {{"key":"150.EDAV.alation.sdoh_race.description","description":"Race description - 3"}}
        ]
    """

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
    if status_code == 200 or status_code == 201:
        print(f"edc_alation_api_access_token_length: {str(len(edc_alation_api_token))}")
        print(f"api_refresh_token_length: {str(len(api_refresh_token))}")
    assert status_code == 200

    # Load the JSON data
    table_dict = json.loads(json_data)
    total_items = len(table_dict)
    # reinit endpoint
    obj_custom_fields_endpoint = alation_CustomFields.CustomFields()
    schema_name = "EDAV.alation"
    data_definition_file_path = config.get("edc_json_schema_location")
    tables = {
        table.name: table
        for table in map(
            lambda t: alation_table.Table(t, data_definition_file_path),
            table_dict,
        )
    }

    editable_fields = ["description", "title"]
    date_fields = []

    for idx, (table_name, table) in enumerate(tables.items()):
        force_submit = idx == total_items - 1
        schema = alation_schema.Schema()
        table_result = schema.update_table_structure(
            edc_alation_api_token,
            edc_alation_base_url,
            alation_datasource_id,
            schema_name,
            table,
            force_submit=force_submit,
            obj_custom_fields_endpoint=obj_custom_fields_endpoint,
            editable_fields=editable_fields,
            table_name=table_name,
            date_fields=date_fields,
        )
        print(f"table_result: {table_result}")

    assert total_items > 0


def test_customfield_update_table_title_description_batch_single_specials_chars_synapse():
    alation_datasource_id = 150
    # Get current time
    now = datetime.now()
    time_string = now.strftime("%Y-%m-%d %H:%M:%S")

    json_data = f"""[
        {{
            "key": "150.EDAV.alation.sdoh_education",
            "name": "sdoh_education",
            "title": "sdoh_education: {time_string}",
            "description": ""
        }}
    ]"""

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
    if status_code == 200 or status_code == 201:
        print(f"edc_alation_api_access_token_length: {str(len(edc_alation_api_token))}")
        print(f"api_refresh_token_length: {str(len(api_refresh_token))}")
    assert status_code == 200

    # Load the JSON data
    table_dict = json.loads(json_data)
    total_items = len(table_dict)
    # reinit endpoint
    obj_custom_fields_endpoint = alation_CustomFields.CustomFields()
    schema_name = "EDAV.alation"
    data_definition_file_path = config.get("edc_json_schema_location")
    tables = {
        table.name: table
        for table in map(
            lambda t: alation_table.Table(t, data_definition_file_path),
            table_dict,
        )
    }

    date_fields = []
    editable_fields = ["description", "title"]

    table = alation_table.Table(None, data_definition_file_path)

    for idx, (table_name, table) in enumerate(tables.items()):
        force_submit = idx == total_items - 1

        table_result = table.update_table_structure(
            edc_alation_api_token,
            edc_alation_base_url,
            alation_datasource_id,
            schema_name,
            table,
            force_submit=force_submit,
            obj_custom_fields_endpoint=obj_custom_fields_endpoint,
            editable_fields=editable_fields,
            table_name=table_name,
            date_fields=date_fields,
        )
        print(f"table_result: {table_result}")

    assert total_items > 0


def test_customfield_update_attribute_title_description_batch_single_simple_synapse():
    alation_datasource_id = 150
    # Get current time
    now = datetime.now()
    time_string = now.strftime("%Y-%m-%d %H:%M:%S")

    json_data = f"""[
        {{
            "key": "150.EDAV.alation.customers",
            "name": "customers",
            "title": "Customers {time_string}",
            "description": ""
        }}
    ]"""

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
    if status_code == 200 or status_code == 201:
        print(f"edc_alation_api_access_token_length: {str(len(edc_alation_api_token))}")
        print(f"api_refresh_token_length: {str(len(api_refresh_token))}")
    assert status_code == 200

    # Load the JSON data
    table_dict = json.loads(json_data)
    total_items = len(table_dict)
    # reinit endpoint
    obj_custom_fields_endpoint = alation_CustomFields.CustomFields()
    schema_name = "EDAV.alation"
    data_definition_file_path = config.get("edc_json_schema_location")
    tables = {
        table.name: table
        for table in map(
            lambda t: alation_table.Table(t, data_definition_file_path),
            table_dict,
        )
    }

    editable_fields = ["description", "title"]
    date_fields = []

    for idx, (table_name, table) in enumerate(tables.items()):
        force_submit = idx == total_items - 1
        schema = alation_schema.Schema()
        table_result = schema.update_table_structure(
            edc_alation_api_token,
            edc_alation_base_url,
            alation_datasource_id,
            schema_name,
            table,
            force_submit=force_submit,
            obj_custom_fields_endpoint=obj_custom_fields_endpoint,
            editable_fields=editable_fields,
            table_name=table_name,
            date_fields=date_fields,
        )
        print(f"table_result: {table_result}")

    assert total_items > 0


def test_customfield_update_attribute_title_description_batch_single_html_synapse():
    alation_datasource_id = 150
    # Get current time
    now = datetime.now()
    time_string = now.strftime("%Y-%m-%d %H:%M:%S")

    json_data = f"""[
        {{
            "key": "150.EDAV.alation.orders",
            "name": "orders",
            "title": "Orders {time_string}",
            "description": "<p>Orders description{time_string}</p>"
        }}
    ]"""

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
    if status_code == 200 or status_code == 201:
        print(f"edc_alation_api_access_token_length: {str(len(edc_alation_api_token))}")
        print(f"api_refresh_token_length: {str(len(api_refresh_token))}")
    assert status_code == 200

    # Load the JSON data
    table_dict = json.loads(json_data)
    total_items = len(table_dict)
    # reinit endpoint
    obj_custom_fields_endpoint = alation_CustomFields.CustomFields()
    schema_name = "EDAV.alation"
    data_definition_file_path = config.get("edc_json_schema_location")
    tables = {
        table.name: table
        for table in map(
            lambda t: alation_table.Table(t, data_definition_file_path),
            table_dict,
        )
    }

    editable_fields = ["description", "title"]
    date_fields = []

    for idx, (table_name, table) in enumerate(tables.items()):
        force_submit = idx == total_items - 1
        schema = alation_schema.Schema()
        table_result = schema.update_table_structure(
            edc_alation_api_token,
            edc_alation_base_url,
            alation_datasource_id,
            schema_name,
            table,
            force_submit=force_submit,
            obj_custom_fields_endpoint=obj_custom_fields_endpoint,
            editable_fields=editable_fields,
            table_name=table_name,
            date_fields=date_fields,
        )
        print(f"table_result: {table_result}")
    assert total_items > 0


def test_customfield_update_attribute_title_description_batch_small_synapse():
    alation_datasource_id = 150
    # Get current time
    now = datetime.now()
    time_string = now.strftime("%Y-%m-%d %H:%M:%S")

    json_data = f"""[
        {{
            "key": "150.EDAV.alation.customers",
            "name": "customers",
            "title": "Customers {time_string}",
            "description": ""
        }},
        {{
            "key": "150.EDAV.alation.orders",
            "name": "orders",
            "title": "Orders {time_string}",
            "description": "<p>Orders description{time_string}</p>"
        }},
        {{
            "key": "150.EDAV.alation.books",
            "name": "books",
            "title": "Books {time_string}",
            "description": "<p>Something something something {time_string}</p>"
        }},
        {{
            "key": "150.EDAV.alation.authors",
            "name": "authors",
            "title": "Authors {time_string}",
            "description": ""
        }},
        {{
            "key": "150.EDAV.alation.sdoh_education",
            "name": "sdoh_education",
            "title": "sdoh_education: {time_string}",
            "description": ""
        }},
        {{
            "key": "150.EDAV.alation.sdoh_maritalstatus",
            "name": "sdoh_maritalstatus",
            "title": "{time_string}",
            "description": ""
        }},
        {{
            "key": "150.EDAV.alation.sdoh_race",
            "name": "sdoh_race",
            "title": "RACE {time_string}",
            "description": "<p>RACE DESC {time_string}</p>"
        }},
        {{
            "key": "150.EDAV.alation.sdoh_ethnicity",
            "name": "sdoh_ethnicity",
            "title": "{time_string}",
            "description": ""
        }}
    ]"""

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
    if status_code == 200 or status_code == 201:
        print(f"edc_alation_api_access_token_length: {str(len(edc_alation_api_token))}")
        print(f"api_refresh_token_length: {str(len(api_refresh_token))}")
    assert status_code == 200

    # Load the JSON data
    table_dict = json.loads(json_data)
    total_items = len(table_dict)
    # reinit endpoint
    obj_custom_fields_endpoint = alation_CustomFields.CustomFields()
    schema_name = "EDAV.alation"
    data_definition_file_path = config.get("edc_json_schema_location")
    tables = {
        table.name: table
        for table in map(
            lambda t: alation_table.Table(t, data_definition_file_path),
            table_dict,
        )
    }

    editable_fields = ["description", "title"]
    date_fields = []

    for idx, (table_name, table) in enumerate(tables.items()):
        force_submit = idx == total_items - 1
        schema = alation_schema.Schema()
        table_result = schema.update_table_structure(
            edc_alation_api_token,
            edc_alation_base_url,
            alation_datasource_id,
            schema_name,
            table,
            force_submit=force_submit,
            obj_custom_fields_endpoint=obj_custom_fields_endpoint,
            editable_fields=editable_fields,
            table_name=table_name,
            date_fields=date_fields,
        )
        print(f"table_result: {table_result}")
    assert total_items > 0


def test_customfield_update_attribute_title_description_batch_small_databricks():
    alation_datasource_id = 319
    schema_name = "wonder_metadata_dev"

    json_data = """[
        {"name":"gold_scrta_nndss_2020_confirmed_hepatitisb_hepatitiscacute_nedss_netss_nndss_perinatalinfection_probable_wonder_20200121", "key": "319.wonder_metadata_dev.gold_scrta_nndss_2020_confirmed_hepatitisb_hepatitiscacute_nedss_netss_nndss_perinatalinfection_probable_wonder_20200121.__meta_ingress_file_path", "title": "title -  2023-07-05 11:51", "description": "<p>description -  2023-07-05 11:51</p>"},
        {"name":"gold_scrta_nndss_2020_confirmed_hepatitisb_hepatitiscacute_nedss_netss_nndss_perinatalinfection_probable_wonder_20200121", "key": "319.wonder_metadata_dev.gold_scrta_nndss_2020_confirmed_hepatitisb_hepatitiscacute_nedss_netss_nndss_perinatalinfection_probable_wonder_20200121.hepatitis_b__perinatal_infection__cum_2019_", "title": "title -  2023-07-05 11:51", "description": "<p>description -  2023-07-05 11:51</p>"},
        {"name":"gold_scrta_nndss_2020_confirmed_hepatitisb_hepatitiscacute_nedss_netss_nndss_perinatalinfection_probable_wonder_20200121", "key": "319.wonder_metadata_dev.gold_scrta_nndss_2020_confirmed_hepatitisb_hepatitiscacute_nedss_netss_nndss_perinatalinfection_probable_wonder_20200121.hepatitis_b__perinatal_infection__cum_2019___flag", "title": "title -  2023-07-05 11:51", "description": "<p>description -  2023-07-05 11:51</p>"},
        {"name":"gold_scrta_nndss_2020_confirmed_hepatitisb_hepatitiscacute_nedss_netss_nndss_perinatalinfection_probable_wonder_20200121", "key": "319.wonder_metadata_dev.gold_scrta_nndss_2020_confirmed_hepatitisb_hepatitiscacute_nedss_netss_nndss_perinatalinfection_probable_wonder_20200121.hepatitis_b__perinatal_infection__cum_2020_", "title": "title -  2023-07-05 11:51", "description": "<p>description -  2023-07-05 11:51</p>"},
        {"name":"gold_scrta_nndss_2020_confirmed_hepatitisb_hepatitiscacute_nedss_netss_nndss_perinatalinfection_probable_wonder_20200121", "key": "319.wonder_metadata_dev.gold_scrta_nndss_2020_confirmed_hepatitisb_hepatitiscacute_nedss_netss_nndss_perinatalinfection_probable_wonder_20200121.hepatitis_b__perinatal_infection__cum_2020___flag", "title": "title -  2023-07-05 11:51", "description": "<p>description -  2023-07-05 11:51</p>"},
        {"name":"gold_scrta_nndss_2020_confirmed_hepatitisb_hepatitiscacute_nedss_netss_nndss_perinatalinfection_probable_wonder_20200121", "key": "319.wonder_metadata_dev.gold_scrta_nndss_2020_confirmed_hepatitisb_hepatitiscacute_nedss_netss_nndss_perinatalinfection_probable_wonder_20200121.hepatitis_b__perinatal_infection__current_week", "title": "title -  2023-07-05 11:51", "description": "<p>description -  2023-07-05 11:51</p>"},
        {"name":"gold_scrta_nndss_2020_confirmed_hepatitisb_hepatitiscacute_nedss_netss_nndss_perinatalinfection_probable_wonder_20200121", "key": "319.wonder_metadata_dev.gold_scrta_nndss_2020_confirmed_hepatitisb_hepatitiscacute_nedss_netss_nndss_perinatalinfection_probable_wonder_20200121.hepatitis_b__perinatal_infection__current_week__flag", "title": "title -  2023-07-05 11:51", "description": "<p>description -  2023-07-05 11:51</p>"},
        {"name":"gold_scrta_nndss_2020_confirmed_hepatitisb_hepatitiscacute_nedss_netss_nndss_perinatalinfection_probable_wonder_20200121", "key": "319.wonder_metadata_dev.gold_scrta_nndss_2020_confirmed_hepatitisb_hepatitiscacute_nedss_netss_nndss_perinatalinfection_probable_wonder_20200121.hepatitis_b__perinatal_infection__previous_52_weeks_max_", "title": "title -  2023-07-05 11:51", "description": "<p>description -  2023-07-05 11:51</p>"},
        {"name":"gold_scrta_nndss_2020_confirmed_hepatitisb_hepatitiscacute_nedss_netss_nndss_perinatalinfection_probable_wonder_20200121", "key": "319.wonder_metadata_dev.gold_scrta_nndss_2020_confirmed_hepatitisb_hepatitiscacute_nedss_netss_nndss_perinatalinfection_probable_wonder_20200121.hepatitis_b__perinatal_infection__previous_52_weeks_max____flag", "title": "title -  2023-07-05 11:51", "description": "<p>description -  2023-07-05 11:51</p>"}
        ]"""

    # Load the JSON data
    data = json.loads(json_data)

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
    obj_custom_fields_endpoint = alation_CustomFields.CustomFields()

    token_endpoint = alation_token_endpoint.TokenEndpoint(edc_alation_base_url)
    (
        status_code,
        edc_alation_api_token,
        api_refresh_token,
    ) = token_endpoint.get_api_token_from_config(config)
    if status_code == 200 or status_code == 201:
        print(f"edc_alation_api_access_token_length: {str(len(edc_alation_api_token))}")
        print(f"api_refresh_token_length: {str(len(api_refresh_token))}")
    assert status_code == 200

    data_definition_file_path = config.get("edc_json_schema_location")

    editable_fields = ["description", "title"]
    date_fields = ["Metadata Last Updated", "Last Update"]
    # Load the JSON data
    table_dict = json.loads(json_data)
    tables = {
        table.name: table
        for table in map(
            lambda t: alation_table.Table(t, data_definition_file_path),
            table_dict,
        )
    }

    for idx, (table_name, table) in enumerate(tables.items()):
        schema = alation_schema.Schema()
        is_last = idx == len(data) - 1
        response_content = schema.update_table_structure(
            edc_alation_api_token,
            edc_alation_base_url,
            alation_datasource_id,
            schema_name,
            table,
            force_submit=is_last,
            obj_custom_fields_endpoint=obj_custom_fields_endpoint,
            editable_fields=editable_fields,
            table_name=table_name,
            date_fields=date_fields,
        )
        print(f"response_content: {response_content}")
    assert len(response_content) > 0


def test_customfield_update_attribute_title_description_batch_large_databricks():
    alation_datasource_id = 319

    current_script_path = os.path.abspath(__file__)
    current_dir_path = os.path.dirname(current_script_path)
    json_file_path = f"{current_dir_path}/batch_large.json"

    # Get the project root directory by going up one or more levels
    project_root = os.path.dirname(os.path.dirname(current_script_path))

    # Change the current working directory to the project root directory
    os.chdir(project_root)

    # Open the file in read mode
    with open(json_file_path, "r", encoding="utf-8-sig") as file:
        # Read the file content
        file_content = file.read()

        # Parse the JSON data
        json_data = json.loads(file_content)

        date_fields = []

        # Loop through the values
        for item in json_data:
            key = item["key"]
            key = key.replace(str(alation_datasource_id) + ".", "")
            title = item["title"]
            description = item["description"]
            field_value = {"title": title, "description": description}
            object_type = "attribute"
            response_content = custom_field_update(
                object_type,
                alation_datasource_id,
                key,
                field_value,
                False,
                date_fields,
            )

            response_status = response_content[0]["status"]
            response_message = response_content[0]["message"]
            response_content_json = response_content[1]
            assert response_status == "success"
            assert len(response_message) > 0
            assert len(str(response_content_json)) > 0
