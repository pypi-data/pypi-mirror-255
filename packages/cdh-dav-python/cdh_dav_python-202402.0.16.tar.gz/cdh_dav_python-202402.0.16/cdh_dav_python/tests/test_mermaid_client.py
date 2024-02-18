import subprocess
import unittest
import os
from io import StringIO
from unittest.mock import patch
from cdh_dav_python.mermaid_service.mermaid_client import MermaidClient
from pathlib import Path


class TestMermaidClient(unittest.TestCase):
    """
    Unit test class for testing the MermaidClient class.
    """

    def test_add_mermaid_to_path(self):
        """
        Test case to verify the functionality of adding Mermaid to the path.

        This test case performs the following steps:
        1. Sets up the expected output.
        2. Creates an instance of the MermaidClient class.
        3. Calls the add_mermaid_to_path method.
        4. Asserts that the actual output matches the expected output.

        """

        # Arrange
        expected_output = "current_working_dir:/path/to/current/working/dir\n"
        expected_output += "b'1.1.0\\n': poetry version succeeded"

        # Act
        obj_mermaid_client = MermaidClient()
        actual_output = obj_mermaid_client.add_mermaid_to_path()

        # Assert
        self.assertEqual(actual_output, expected_output)

    def test_install_mermaid(self):
        """
        Test case for the install_mermaid method of the MermaidClient class.

        This test verifies that the install_mermaid method correctly installs Mermaid
        and produces the expected output.

        Steps:
        1. Arrange the expected output.
        2. Create an instance of the MermaidClient class.
        3. Call the install_mermaid method.
        4. Assert that the output matches the expected output.
        """
        # Arrange
        expected_output = "current_working_dir:/path/to/current/working/dir\n"
        expected_output += "b'1.1.0\\n': poetry version succeeded"

        # Act
        obj_mermaid_client = MermaidClient()
        actual_output = obj_mermaid_client.install_mermaid()

        # Assert
        self.assertEqual(actual_output, expected_output)

    def test_export_mermaid_erd_to_png(self):
        """
        Test case for the install_mermaid method of the MermaidClient class.

        This test verifies that the install_mermaid method correctly installs Mermaid
        and produces the expected output.

        Steps:
        1. Arrange the expected output.
        2. Create an instance of the MermaidClient class.
        3. Call the install_mermaid method.
        4. Assert that the output matches the expected output.
        """
        # Arrange
        expected_output = "current_working_dir:/path/to/current/working/dir\n"
        expected_output += "b'1.1.0\\n': poetry version succeeded"

        # Get the current working directory as a Path object
        cwd = Path.cwd()

        # Find the 'cdh_dav' part in the path
        cdh_dav_part = None
        for part in cwd.parts:
            lowercase_part = part.lower()
            if lowercase_part == "cdh-dav":
                cdh_dav_part = part
                break

        # Truncate the path up to 'cdh_dav' and append the new segment
        if cdh_dav_part:
            new_path_index = cwd.parts.index(cdh_dav_part) + 1
            diagram_path = (
                Path(*cwd.parts[:new_path_index])
                / "docs"
                / "mermaid_environment_cls.mmd"
            )
            diagram_path = str(diagram_path)
        else:
            print("The directory 'cdh_dav' was not found in the current path.")
            diagram_path = None

        # Print the new path
        if diagram_path:
            print(diagram_path)

        # Change the extension from mmd to .png
        diagram_png_path = os.path.splitext(diagram_path)[0] + ".png"

        # Act
        obj_mermaid_client = MermaidClient()
        actual_output = obj_mermaid_client.export_mermaid(
            diagram_path, diagram_png_path
        )

        # Assert
        self.assertEqual(actual_output, expected_output)

    def test_show_help(self):
        """
        Test case for the show_help method of the MermaidClient class.

        This test verifies that the show_help method returns the expected output.

        Steps:
        1. Arrange the expected output.
        2. Create an instance of the MermaidClient class.
        3. Call the show_help method.
        4. Assert that the actual output matches the expected output.
        """

        # Arrange
        expected_output = "current_working_dir:/path/to/current/working/dir\n"
        expected_output += "b'1.1.0\\n': poetry version succeeded"

        # Act
        obj_mermaid_client = MermaidClient()
        actual_output = obj_mermaid_client.show_help()

        # Assert
        self.assertEqual(actual_output, expected_output)


if __name__ == "__main__":
    unittest.main()
