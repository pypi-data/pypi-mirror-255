"""
AwsStorageFile.download_file_from_s3_to_local(
    bucket_name='my-bucket',
    s3_object_key='path/to/s3/object',
    local_file_path='path/to/local/file',
    data_product_id='your-data-product-id'
)
Usage Example:
    # Specify the S3 bucket details and local file path
    bucket_name = 'my-bucket'  # Replace with your S3 bucket name
    s3_object_key = 'path/to/s3/object'  # Replace with the path to your S3 object
    local_file_path = 'path/to/local/file'  # Replace with the desired local path for the downloaded file

    # Call the static method to download the file
    AwsStorageFile.download_file_from_s3(bucket_name, s3_object_key, local_file_path)

Note:
    The module requires the installation of boto3 packages.
    Ensure that AWS credentials are configured properly for boto3 to access the specified S3 bucket.
"""

import os
import sys
import boto3
import botocore

from cdh_dav_python.cdc_admin_service.environment_logging import LoggerSingleton
from azure.storage.filedatalake import DataLakeServiceClient

OS_NAME = os.name
sys.path.append("../..")

if OS_NAME.lower() == "nt":
    print("environment_logging: windows")
    sys.path.append(os.path.dirname(os.path.abspath(__file__ + "\\..")))
    sys.path.append(os.path.dirname(os.path.abspath(__file__ + "\\..\\..")))
    sys.path.append(os.path.dirname(os.path.abspath(__file__ + "\\..\\..\\..")))
else:
    print("environment_logging: non windows")
    sys.path.append(os.path.dirname(os.path.abspath(__file__ + "/..")))
    sys.path.append(os.path.dirname(os.path.abspath(__file__ + "/../..")))
    sys.path.append(os.path.dirname(os.path.abspath(__file__ + "/../../..")))


# Get the currently running file name
NAMESPACE_NAME = os.path.basename(os.path.dirname(__file__))
# Get the parent folder name of the running file
SERVICE_NAME = os.path.basename(__file__)


class AwsStorageFile:
    """
    This module provides a class for downloading files from an S3 bucket.

    Usage:
        bucket_name = 'my-bucket'  # Replace with your S3 bucket name
        s3_object_key = 'path/to/s3/object'  # Replace with the path to your S3 object
        local_file_path = 'path/to/local/file'  # Replace with the desired local path for the downloaded file

        AwsStorageFile.download_file_from_s3(bucket_name, s3_object_key, local_file_path)
    """

    @staticmethod
    def download_file_from_s3_to_adls(
        s3_bucket,
        s3_key,
        adls_account_name,
        adls_file_system,
        adls_directory,
        adls_file_name,
        azure_storage_sas_token,
    ):
        # Initialize S3 client
        s3_client = boto3.client("s3")

        # Get the object from S3
        s3_object = s3_client.get_object(Bucket=s3_bucket, Key=s3_key)
        data_stream = s3_object["Body"].read()

        # Initialize ADLS client
        service_client = DataLakeServiceClient(
            account_url=f"https://{adls_account_name}.dfs.core.windows.net",
            credential=azure_storage_sas_token,
        )

        # Get ADLS file system client
        file_system_client = service_client.get_file_system_client(
            file_system=adls_file_system
        )

        # Get directory client
        directory_client = file_system_client.get_directory_client(adls_directory)

        # Get file client
        file_client = directory_client.get_file_client(adls_file_name)

        # Upload data to ADLS
        file_client.upload_data(data_stream, overwrite=True)

        return "Success"

    @staticmethod
    def download_file_from_s3_to_local(
        bucket_name: str,
        s3_object_key: str,
        local_file_path: str,
        data_product_id: str,
        environment: str,
    ):
        """
        Downloads a file from an S3 bucket to the local file system.

        Args:
            bucket_name (str): The name of the S3 bucket.
            s3_object_key (str): The key of the object in the S3 bucket.
            local_file_path (str): The path where the file will be downloaded to on the local file system.
            aws_access_key_id (str): The AWS access key ID.
            aws_secret_access_key (str): The AWS secret access key.
            data_product_id (str): The ID of the data product.
            environment (str): The environment in which the operation is performed.

        Raises:
            Exception: If there is an error during the file download.

        """

        tracer, logger = LoggerSingleton.instance(
            NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
        ).initialize_logging_and_tracing()

        with tracer.start_as_current_span("download_file_from_s3_to_local"):
            try:
                # Create a botocore session
                session = botocore.session.get_session()

                region_name = "us-east-1"

                # Create a client for the S3 service
                s3 = session.create_client(
                    "s3", region_name=region_name
                )  # Replace 'your-region' with the appropriate region

                # Download the file
                try:
                    response = s3.get_object(Bucket=bucket_name, Key=s3_object_key)
                    total_downloaded = 0
                    with open(local_file_path, "wb") as f:
                        # Stream the content to file
                        for chunk in response["Body"].iter_chunks():
                            f.write(chunk)
                            total_downloaded += len(chunk)
                            logger.info(f"Downloaded {total_downloaded} bytes")
                    logger.info(f"File downloaded successfully: {local_file_path}")

                except Exception as e:
                    error_message = f"Error downloading file: {e}"
                    error_message = (
                        error_message
                        + f"Failed to download file from S3 bucket {bucket_name} to local file path {local_file_path}"
                    )
                    logger.error(error_message)
                    raise e

            except Exception as ex:
                error_msg = "Error: %s", ex
                exc_info = sys.exc_info()
                LoggerSingleton.instance(
                    NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
                ).error_with_exception(error_msg, exc_info)
                raise
