from dotenv import load_dotenv, find_dotenv, set_key

import cdh_dav_python.cdc_admin_service.sequence_diagram as cdc_sequence_diagram
import cdh_dav_python.cdc_tech_environment_service.environment_file as cdc_env_file

import pytest
from unittest.mock import patch
import sys
import os
from unittest.mock import Mock
from pathlib import Path
import unittest
from cdh_dav_python.cdc_metadata_service.environment_metadata import (
    EnvironmentMetaData,
)

sys.path.append("..")

# Get the currently running file name
NAMESPACE_NAME = os.path.basename(os.path.dirname(__file__))
# Get the parent folder name of the running file
SERVICE_NAME = os.path.basename(__file__)


# Get the absolute path of the current script
current_script_path = os.path.abspath(__file__)

# Get the project root directory by going up one or more levels
project_root = os.path.dirname(os.path.dirname(current_script_path))

# Change the current working directory to the project root directory
os.chdir(project_root)

REPOSITORY_PATH_DEFAULT = str(Path(os.getcwd()))
DATA_PRODUCT_ID = "wonder_metadata"
ENVIRONMENT = "dev"

PARAMETERS = {
    "data_product_id": DATA_PRODUCT_ID,
    "data_product_id_root": "wonder",
    "data_product_id_individual": "metadata",
    "environment": ENVIRONMENT,
    "repository_path": REPOSITORY_PATH_DEFAULT,
}


dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(dotenv_path)


class TestCDCAdminSequenceDiagram(unittest.TestCase):
    """
    Unit tests for the CDC Admin Sequence Diagram module.
    """

    def get_config(self, parameters):
        """
        Get the configuration based on the given parameters.

        Parameters:
        - parameters (dict): The configuration parameters.

        Returns:
        - config (dict): The configuration.
        """
        environment_metadata = EnvironmentMetaData()
        config = environment_metadata.get_configuration_common(
            parameters, None, DATA_PRODUCT_ID, ENVIRONMENT
        )
        return config

    def test_generate_timeline_from_trace_log_json(self):
        """
        Test case for generating timeline from an Excel file and printing the timeline string.

        This test case performs the following steps:
        1. Changes the current working directory to the project root directory.
        2. Retrieves the configuration parameters.
        3. Gets the file utility object.
        4. Gets the manifest file path.
        5. Generates a timeline from the Excel file using the sequence diagram module.
        6. Prints the generated timeline string.

        Note: Make sure you have put a file in the uploads directory.

        Parameters:
        None

        Returns:
        None
        """

        sequence_diagram = cdc_sequence_diagram.SequenceDiagram()
        timeline_string = sequence_diagram.generate_timeline_from_trace_log_json(
            DATA_PRODUCT_ID, ENVIRONMENT
        )
        print(f"timeline_string: {timeline_string}")
        assert timeline_string is not None

    def test_generate_timeline_download_manifest_excel_synapse(self):
        """
        Test case for generating timeline from an Excel file and printing the timeline string.

        This test case performs the following steps:
        1. Changes the current working directory to the project root directory.
        2. Retrieves the configuration parameters.
        3. Gets the file utility object.
        4. Gets the manifest file path.
        5. Generates a timeline from the Excel file using the sequence diagram module.
        6. Prints the generated timeline string.

        Note: Make sure you have put a file in the uploads directory.

        Parameters:
        None

        Returns:
        None
        """
        # Change the current working directory to the project root directory
        os.chdir(project_root)

        # Get the file utility object
        obj_file = cdc_env_file.EnvironmentFile()

        # Get the directory of the current script
        app_dir = os.path.dirname(os.path.abspath(__file__))
        # Go up one directory
        parent_dir = os.path.dirname(app_dir)
        # Go up another directory (two levels up from the script)
        grandparent_dir = os.path.dirname(parent_dir)

        log_path = grandparent_dir + "/" + ENVIRONMENT + "_log_trace_sequence/"
        log_path = obj_file.convert_to_current_os_dir(
            log_path, DATA_PRODUCT_ID, ENVIRONMENT
        )

        file_name = "download_manifest_excel_synapse.xlsx"
        # Make sure you have put a file in the uploads directory
        print(f"log_path: {log_path}")
        print(f"file_name: {file_name}")

        sequence_diagram = cdc_sequence_diagram.SequenceDiagram()
        timeline_string = sequence_diagram.generate_timeline_from_excel(
            DATA_PRODUCT_ID, ENVIRONMENT, log_path=log_path, file_name=file_name
        )
        print(f"timeline_string: {timeline_string}")
        assert timeline_string is not None

    def test_generate_timeline_download_manifest_excel_dcipher(self):
        """
        Test case for generating timeline from an Excel file and printing the timeline string.

        This test case performs the following steps:
        1. Changes the current working directory to the project root directory.
        2. Gets the file utility object.
        3. Gets the manifest file path.
        4. Generates a timeline from the Excel file using the sequence diagram module.
        5. Prints the generated timeline string.

        Note: Make sure you have put a file in the uploads directory.

        Parameters:
        None

        Returns:
        None
        """
        # Change the current working directory to the project root directory
        os.chdir(project_root)

        # Get the file utility object
        obj_file = cdc_env_file.EnvironmentFile()

        # Get the directory of the current script
        app_dir = os.path.dirname(os.path.abspath(__file__))
        # Go up one directory
        parent_dir = os.path.dirname(app_dir)
        # Go up another directory (two levels up from the script)
        grandparent_dir = os.path.dirname(parent_dir)
        log_path = grandparent_dir + "/" + ENVIRONMENT + "_log_trace_sequence/"
        log_path = obj_file.convert_to_current_os_dir(
            log_path, DATA_PRODUCT_ID, DATA_PRODUCT_ID
        )
        # Make sure you have put a file in the uploads directory

        sequence_diagram = cdc_sequence_diagram.SequenceDiagram()
        timeline_string = sequence_diagram.generate_timeline_from_excel(
            DATA_PRODUCT_ID,
            DATA_PRODUCT_ID,
            log_path=log_path,
            file_name="download_manifest_excel_dcipher.xlsx",
        )
        print(f"timeline_string: {timeline_string}")

    def test_generate_diagram_from_excel(self):
        """
        Test case for generating a diagram from a log file and printing the diagram string.

        This test case performs the following steps:
        1. Changes the current working directory to the project root directory.
        2. Retrieves the configuration parameters.
        3. Gets the file utility object.
        4. Gets the manifest file path.
        5. Generates a diagram from the log file using the sequence diagram module.
        6. Prints the generated diagram string.

        Note: Make sure you have put a file in the uploads directory.

        Parameters:
        None

        Returns:
        None
        """
        # Change the current working directory to the project root directory
        os.chdir(project_root)

        data_product_id = "wonder_metadata"
        environment = "dev"

        # Get the file utility object
        obj_file = cdc_env_file.EnvironmentFile()

        # Get the manifest file
        # Get the directory of the current script
        app_dir = os.path.dirname(os.path.abspath(__file__))
        # Go up one directory
        parent_dir = os.path.dirname(app_dir)
        # Go up another directory (two levels up from the script)
        grandparent_dir = os.path.dirname(parent_dir)
        log_path = grandparent_dir + "/" + ENVIRONMENT + "_log_trace_sequence/"
        log_path = obj_file.convert_to_current_os_dir(
            log_path, data_product_id, environment
        )
        # Make sure you have put a file in the uploads directory
        file_name = "download_manifest_excel_dcipher.xlsx"

        sequence_diagram = cdc_sequence_diagram.SequenceDiagram()
        mermaid_diagram_string = sequence_diagram.generate_diagram_from_excel(
            data_product_id, environment, log_path, file_name
        )
        print(mermaid_diagram_string)


if __name__ == "__main__":
    pytest.main()
