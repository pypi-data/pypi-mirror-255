"""
This module contains unit tests for the AwsStorageFile class, part of the cdh_dav_python.amzn_s3_service package. 

The AwsStorageFile class is designed to facilitate the downloading of files from Amazon S3 to the local file system. This module specifically tests the functionality and reliability of the download process under various conditions.

The primary focus of these tests is to ensure that the AwsStorageFile correctly handles the downloading of files from S3, including cases of successful downloads. Each test case within the module sets up the necessary environment, executes the download operation using the AwsStorageFile class, and then asserts the expected outcomes.

By running these tests, developers can verify that the AwsStorageFile class operates as expected in the context of retrieving files from Amazon S3, thereby ensuring data integrity and consistency in file handling.

Classes:
    TestAwsStorageFile: Contains all the unit tests for testing the AwsStorageFile class.

Usage:
    This module is intended to be run as a standard unit test script using Python's unittest framework. It can be executed directly from the command line or integrated into a larger test suite for more comprehensive testing.
"""

import os
import unittest
import tempfile
from cdh_dav_python.aws_storage_service.aws_storage_file import AwsStorageFile


class TestAwsStorageFile(unittest.TestCase):
    """
    Unit tests for the AwsStorageFile class.
    """

    def test_download_file_from_s3_to_local_success(self):
        """
        Test case to verify the successful download of a file from S3 to the local system.

        Steps:
        1. Set up the necessary variables for the test.
        2. Create an instance of the AwsStorageFile class.
        3. Call the download_file_from_s3_to_local method with the provided parameters.
        4. Assert that the result is "Success".

        """
        # Arrange
        bucket_name = "hls-eng-data-public"
        file_name = "OMOP-VOCAB.tar.gz"
        s3_object_key = "omop/OMOP-VOCAB.tar.gz"
        data_product_id = "wonder_metadata_dev"
        environment = "dev"
        temp_dir = tempfile.gettempdir()
        file_path = os.path.join(temp_dir, file_name)

        obj_s3_downloader = AwsStorageFile()

        # Act
        result = obj_s3_downloader.download_file_from_s3_to_local(
            bucket_name, s3_object_key, file_path, data_product_id, environment
        )

        assert result == "Success"


if __name__ == "__main__":
    unittest.main()
