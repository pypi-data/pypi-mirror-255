import unittest
import tempfile
import os
from unittest.mock import patch, mock_open
from cdh_dav_python.npm_service.npm_client import (
    NpmClient,
)  # Replace with your actual module name


class TestNpmClient(unittest.TestCase):
    """
    Unit tests for the NpmClient class.
    """

    def test_create_npmrc_file(self):
        """
        Test case for the create_npmrc_file method of NpmClient class.
        """

        with tempfile.TemporaryDirectory() as tempdir:
            file_path = os.path.join(tempdir, ".npmrc")
            registry_url = "http://registry.url"
            auth_token = "authToken123"
            data_product_id = "dp123"
            environment = "test"

            # Execute
            NpmClient.create_npmrc_file(
                file_path, registry_url, auth_token, data_product_id, environment
            )

            # Verify file contents
            with open(file_path, "r", "utf-8") as file:
                content = file.read()
                self.assertIn(f"registry={registry_url}", content)
                self.assertIn(f"//{registry_url}/:_authToken={auth_token}", content)


if __name__ == "__main__":
    unittest.main()
