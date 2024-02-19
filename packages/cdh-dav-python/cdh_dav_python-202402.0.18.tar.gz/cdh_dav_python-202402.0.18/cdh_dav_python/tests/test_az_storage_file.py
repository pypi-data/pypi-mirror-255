import unittest
from unittest.mock import patch, MagicMock
from cdh_dav_python.az_storage_service.az_storage_file import AzStorageFile


class TestAzStorageFile(unittest.TestCase):
    @patch("your_module.DataLakeServiceClient")  # Mock the DataLakeServiceClient
    def test_get_file_size(self, mock_service_client):
        # Setup mock
        mock_file_client = MagicMock()
        mock_file_client.get_file_properties.return_value.size = 1024
        mock_file_system_client = MagicMock()
        mock_file_system_client.get_file_client.return_value = mock_file_client
        mock_service_client.return_value.get_file_system_client.return_value = (
            mock_file_system_client
        )

        # Call the method
        size = AzStorageFile.get_file_size(
            account_url="https://example.dfs.core.windows.net",
            tenant_id="tenant-id",
            client_id="client-id",
            client_secret="client-secret",
            storage_container="container",
            file_path="path/to/file",
            data_product_id="data-product-id",
            environment="environment",
        )

        # Assert the result
        self.assertEqual(size, 1024)
        mock_file_client.get_file_properties.assert_called_once()

    @patch("your_module.DataLakeServiceClient")
    @patch("your_module.check_output")
    def test_file_adls_copy_local_to_blob(self, mock_check_output, mock_service_client):
        # Setup configuration and parameters
        config = {
            "az_sub_client_id": "client-id",
            "client_secret": "client-secret",
            "az_sub_client_secret_key": "secret-key",
            "az_sub_tenant_id": "tenant-id",
            "running_local": True,
        }
        source_path = "/local/path/to/file"
        destination_path = "https://example.dfs.core.windows.net/container/path/to/file"
        from_to = "LocalBlobFS"

        # Setup mock
        mock_directory_client = MagicMock()
        mock_file_client = mock_directory_client.create_file.return_value
        mock_file_system_client = MagicMock()
        mock_file_system_client.get_directory_client.return_value = (
            mock_directory_client
        )
        mock_service_client.return_value.get_file_system_client.return_value = (
            mock_file_system_client
        )
        mock_check_output.return_value = "command output"

        # Call the method
        result = AzStorageFile.file_adls_copy(
            config, source_path, destination_path, from_to, dbutils=None
        )

        # Asserts
        mock_check_output.assert_called()  # Adjust based on expected subprocess calls
        mock_service_client.assert_called()  # Adjust based on expected service client calls
        self.assertIsNotNone(result)  # Adjust based on expected result


if __name__ == "__main__":
    unittest.main()
