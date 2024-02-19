"""
This module contains unit tests for the SecretScope functionality.

The TestSecretScope class defines test cases for the SecretScope class methods.
"""

import os
import unittest

from cdh_dav_python.databricks_service.dbx_secret_scope import DbxSecretScope
from cdh_dav_python.cdc_metadata_service.environment_metadata import EnvironmentMetaData
from pathlib import Path

if __name__ == "__main__":
    unittest.main()


class TestDbxSecretScope(unittest.TestCase):
    """
    A test class for the DbxSecretScope functionality.
    """

    def get_config(self, parameters: str, data_product_id, environment):
        """
        Retrieves the configuration based on the given parameters.

        Args:
            parameters (dict): A dictionary containing the parameters.

        Returns:
            dict: The configuration retrieved based on the parameters.
        """

        environment_metadata = EnvironmentMetaData()

        config = environment_metadata.get_configuration_common(
            parameters, None, data_product_id, environment
        )

        return config

    def test_list_secret_scopes(self):
        """
        Test case for the list_secret_scopes method of DbxSecretScope class.

        Args:
            mocker: The mocker object used for mocking the dbutils object.

        Returns:
            None

        Raises:
            AssertionError: If the result is not equal to the expected list of secret scopes.
        """

        # Create an instance of DbxSecretScope
        obj_secret_scope = DbxSecretScope()

        # Call the function under test
        dbutils = None
        json_data = obj_secret_scope.list_secret_scopes(dbutils)

        assert "Scope" in json_data[0], "First element does not have a 'Scope' field"

        # Start with the header
        markdown_table = "| Scope | Backend |\n| --- | --- |\n"

        # Add each row
        for item in json_data:
            markdown_table += f"| {item['Scope']} | {item['Backend']} |\n"

        print(markdown_table, end="")  # Print each row on a new line without showing \n

    def test_list_reference_dev_secrets(self):
        """
        Test case for the list_secrets function.

        This function tests the functionality of the list_secrets function in the DbxSecretScope class.
        It creates an instance of DbxSecretScope, calls the list_secrets function with a scope name and dbutils object,
        and verifies that the returned JSON data contains the expected fields.
        It also generates a markdown table from the JSON data and prints it.

        Returns:
            None
        """

        # Current working directory
        current_path = Path(os.getcwd())

        # Go up two directories
        up_two_directories = current_path.parent

        # Navigate down to 'cdh/cdh_reference/'
        repository_path_default = up_two_directories

        # Convert Path object to string, if necessary
        repository_path_default = str(current_path)

        data_product_id = "cdh_reference"
        environment = "dev"

        parameters = {
            "data_product_id": data_product_id,
            "data_product_id_root": "cdh",
            "data_product_id_individual": "reference",
            "environment": environment,
            "running_local": True,
            "repository_path": repository_path_default,
        }

        config = self.get_config(parameters, data_product_id, environment)

        scope = config["cdh_databricks_kv_scope"]
        # Create an instance of DbxSecretScope
        obj_secret_scope = DbxSecretScope()

        # Call the function under test
        dbutils = None
        json_data = obj_secret_scope.list_secrets(scope, dbutils)

        assert (
            "SecretMetadata" in json_data[0]
        ), "First element does not have a 'SecretMetadata' field"

        # Start with the header
        markdown_table = obj_secret_scope.generate_secret_markdown_table(json_data)

        print(markdown_table, end="")  # Print each row on a new line without showing \n
