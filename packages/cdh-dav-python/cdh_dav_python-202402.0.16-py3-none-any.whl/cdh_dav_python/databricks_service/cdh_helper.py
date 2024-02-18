# Databricks notebook
import os
import traceback
import json
import base64
import requests
import uuid
from datetime import datetime, timezone

from cdc_azure.databricks.etl.shared import constants

from pyspark.dbutils import DBUtils
from pyspark.sql import SparkSession
from delta.tables import *

spark = SparkSession.builder.getOrCreate()
dbutils = DBUtils(spark)


class CdhHelper:
    """
    A helper class for CDH operations.

    Methods:
        delete_zero_byte_folder(path): Deletes zero-byte folders from the specified path.
        secure_connect_spark_adls(): Connects to Azure Data Lake Storage using Service Principal secrets and OAuth.
        find_nth(haystack, needle, n): Find the index of the nth occurrence of a substring in a string.
        get_table_list(source_folder_location): Retrieves a list of tables from the specified source folder location.
        get_all_files_in_directory(ls_path): Recursively retrieves all files in a directory and its subdirectories.
        get_specific_files_in_directory(ls_path, file_name, exact_match=True): Retrieves a list of specific files in a directory based on the given file name.
        get_file_info_in_directory(path): Recursively retrieves file information in a directory.
        get_first_file_in_directory(ls_path, file_type): Get the first file with the specified file type in the given directory.
        get_first_level_subfolders(SourceFolderLocation): Retrieves the names of the first-level subfolders in the specified source folder location.
        exception_to_string(ex): Converts an exception to a string representation.
        publish_event_status(status_success, data_source, workflow_id, request_id, outputs=[]): Publishes the status of an event.
        publish_event_status_with_custom_status(status, data_source, workflow_id, request_id, outputs=[]): Publishes the event status with custom status to a queue.
        fetchTables(database): Fetches tables from a database.
    """


class CdhHelper:
    @staticmethod
    def delete_zero_byte_folder(path):
        """
        Deletes zero-byte folders from the specified path.

        Args:
            path (str): The path to the directory containing the folders.

        Returns:
            None
        """
        match = "$folder$"
        dir_files = get_dbutils().fs.ls(path)
        for file in dir_files:
            if file.name.find(match) != -1:
                dbutils.fs.rm(file.path)
            if file.isDir():
                delete_zero_byte_folder(file.path)

    @staticmethod
    def secure_connect_spark_adls():
        """
        Connects to Azure Data Lake Storage using Service Principal secrets and OAuth.

        Returns:
            None
        """
        secret_scope = constants.get_secret_scope()
        # Application (Client) ID
        applicationId = dbutils.secrets.get(scope=secret_scope, key="cdh-adb-client-id")
        # Application (Client) Secret Key
        authenticationKey = dbutils.secrets.get(
            scope=secret_scope, key="cdh-adb-client-secret"
        )
        # Directory (Tenant) ID
        tenantId = dbutils.secrets.get(scope=secret_scope, key="cdh-adb-tenant-id")

        endpoint = "https://login.microsoftonline.com/" + tenantId + "/oauth2/token"

        # Connecting using Service Principal secrets and OAuth
        configs = {
            "fs.azure.account.auth.type": "OAuth",
            "fs.azure.account.oauth.provider.type": "org.apache.hadoop.fs.azurebfs.oauth2.ClientCredsTokenProvider",
            "fs.azure.account.oauth2.client.id": applicationId,
            "fs.azure.account.oauth2.client.secret": authenticationKey,
            "fs.azure.account.oauth2.client.endpoint": endpoint,
        }

        spark.conf.set("fs.azure.account.auth.type", "OAuth")
        spark.conf.set(
            "fs.azure.account.oauth.provider.type",
            "org.apache.hadoop.fs.azurebfs.oauth2.ClientCredsTokenProvider",
        )
        spark.conf.set("fs.azure.account.oauth2.client.id", applicationId)
        spark.conf.set("fs.azure.account.oauth2.client.secret", authenticationKey)
        spark.conf.set("fs.azure.account.oauth2.client.endpoint", endpoint)

    @staticmethod
    def find_nth(haystack, needle, n):
        """
        Find the index of the nth occurrence of a substring in a string.

        Args:
            haystack (str): The string to search in.
            needle (str): The substring to search for.
            n (int): The occurrence number to find.

        Returns:
            int: The index of the nth occurrence of the substring in the string.
                Returns -1 if the substring is not found or if n is greater than the number of occurrences.

        """
        start = haystack.find(needle)
        while start >= 0 and n > 1:
            start = haystack.find(needle, start + len(needle))
            n -= 1
        return start

    @classmethod
    def get_table_list(source_folder_location):
        """
        Retrieves a list of tables from the specified source folder location.

        Args:
            source_folder_location (str): The path to the source folder location.

        Returns:
            list: A list of table names extracted from the files in the source folder.
        """
        lists = dbutils.fs.ls(source_folder_location)
        tables = []
        for file in lists:
            table = file.path
            loc = cls.find_nth(table, "/", 6)
            loc2 = cls.find_nth(table, "$", 1)
            if loc2 == -1:
                tables.append(table[loc + 1 : -1])
        return tables

    @classmethod
    def get_all_files_in_directory(ls_path):
        """
        Recursively retrieves all files in a directory and its subdirectories.

        Args:
            ls_path (str): The path of the directory.

        Returns:
            list: A list of file paths.
        """
        dir_paths = dbutils.fs.ls(ls_path)
        subdir_paths = [
            cls.get_all_files_in_directory(p.path)
            for p in dir_paths
            if p.isDir() and p.path != ls_path
        ]
        flat_subdir_paths = [p for subdir in subdir_paths for p in subdir]
        return list(map(lambda p: p.path, dir_paths)) + flat_subdir_paths

    @classmethod
    def get_specific_files_in_directory(ls_path, file_name, exact_match=True):
        """
        Retrieves a list of specific files in a directory based on the given file name.

        Parameters:
        ls_path (str): The path of the directory to search in.
        file_name (str): The name of the file(s) to search for.
        exact_match (bool, optional): Determines whether the file name should be an exact match or a partial match.
                                    Defaults to True (exact match).

        Returns:
        list: A list of file paths matching the given file name.
        """
        paths = cls.get_all_files_in_directory(ls_path)
        result = []
        for path in paths:
            path_file_name = os.path.basename(path)
            if exact_match:
                if file_name.casefold() == path_file_name.casefold():
                    result.append(path)
            else:
                if file_name.casefold() in path_file_name.casefold():
                    result.append(path)

        return result

    @classmethod
    def get_file_info_in_directory(path: str):
        """
        Recursively retrieves file information in a directory.

        Args:
            path (str): The path of the directory.

        Yields:
            FileInfo: A generator that yields file information objects.

        """
        for x in dbutils.fs.ls(path):
            if x.path[-1] != "/":
                yield x
            else:
                for y in cls.get_file_info_in_directory(path=x.path):
                    yield y

    @classmethod
    def get_first_file_in_directory(ls_path: str, file_type: str):
        """
        Get the first file with the specified file type in the given directory.

        Args:
            ls_path (str): The path of the directory.
            file_type (str): The file extension to filter the files.

        Returns:
            str: The path of the first file with the specified file type, or None if no such file is found.
        """
        paths = cls.get_all_files_in_directory(ls_path)
        for path in paths:
            file_name = os.path.basename(path)
            if file_name != "":
                file_name_and_path = os.path.splitext(file_name)
                file_extension = file_name_and_path[1]
                if file_extension == file_type:
                    return path
        return None

    @staticmethod
    def get_first_level_subfolders(SourceFolderLocation):
        """
        Retrieves the names of the first-level subfolders in the specified source folder location.

        Args:
            SourceFolderLocation (str): The path of the source folder location.

        Returns:
            list: A list of subfolder names.

        """
        lists = dbutils.fs.ls(SourceFolderLocation)
        tables = []
        for list in lists:
            if list.isDir():
                tables.append(list.name[:-1])
        return tables

    def exception_to_string(ex):
        """
        Converts an exception to a string representation.

        Args:
            ex (Exception): The exception to convert.

        Returns:
            str: The string representation of the exception.
        """
        stack = traceback.extract_stack()[:-3] + traceback.extract_tb(
            ex.__traceback__
        )  # add limit=??
        pretty = traceback.format_list(stack)
        return "".join(pretty) + "\n  {} {}".format(ex.__class__, ex)

    def publish_event_status(
        status_success: bool,
        data_source: str,
        workflow_id: str,
        request_id: str,
        outputs=[],
    ):
        """
        Publishes the status of an event.

        Args:
            status_success (bool): Indicates whether the event status is successful or not.
            data_source (str): The data source of the event.
            workflow_id (str): The ID of the workflow associated with the event.
            request_id (str): The ID of the request associated with the event.
            outputs (list, optional): The outputs associated with the event. Defaults to an empty list.
        """

        if status_success:
            status = "Succeeded"
        else:
            status = "Failed"

        publish_event_status_with_custom_status(
            status=status,
            data_source=data_source,
            workflow_id=workflow_id,
            request_id=request_id,
            outputs=outputs,
        )

    def publish_event_status_with_custom_status(
        status: str, data_source: str, workflow_id: str, request_id: str, outputs=[]
    ):
        """
        Publishes the event status with custom status to a queue.

        Args:
            status (str): The status of the event. Must be one of "succeeded", "failed", or "rejected".
            data_source (str): The data source of the event.
            workflow_id (str): The ID of the workflow.
            request_id (str): The ID of the request.
            outputs (list, optional): The outputs of the event. Defaults to an empty list.

        Returns:
            None

        Raises:
            Exception: If there is an error publishing the message to the queue.

        """
        datetime_now_utc = datetime.now(tz=timezone.utc)
        now = datetime_now_utc.strftime("%Y-%m-%dT%H:%M:%SZ")

        if status.casefold() not in ["succeeded", "failed", "rejected"]:
            print(f"Invalid status: {status}")

        job_payload = {
            "data_source": "{data_source}",
            "workflow_id": "{workflow_id}",
            "request_id": "{request_id}",
            "event_source": "adb",
            "event_time_utc": "{event_time_utc}",
            "outputs": outputs,
            "status": "{status}",
        }

        job_payload = (
            json.dumps(job_payload)
            .replace("{request_id}", request_id)
            .replace("{workflow_id}", workflow_id)
            .replace("{data_source}", data_source)
            .replace("{status}", status)
            .replace("{event_time_utc}", now)
        )

        print(f"\n job_payload back to orchestrator: {job_payload}")
        if (
            workflow_id is None
            or workflow_id == ""
            or workflow_id.casefold() == "simulated".casefold()
            or workflow_id.casefold() == "demo".casefold()
            or workflow_id.casefold() == "isolated".casefold()
        ):
            print(f"\n Running in ISOLATED mode. No messages are sent to queue")
            return

        # get sas token
        secret_scope = constants.get_secret_scope()
        url = dbutils.secrets.get(scope=secret_scope, key="cdh-event-publish-func-url")

        response = requests.post(url, data=job_payload)
        if not response.ok:
            print(response.text)
            raise Exception(
                f"Error publishing message to queue at {url} with payload {job_payload} \n Status_Code: {response.status_code}. Text: {response.text}"
            )

    def fetchTables(database):
        """
        Fetches the tables for a given database.

        Args:
            database (str): The name of the database.

        Returns:
            list: A list of table names in the specified database.
        """
        tables = []
        print("Fetching tables for database:", database)
        v = spark.sql("SHOW TABLES in " + database + "")
        for row in v.collect():
            tables.append(row["tableName"])
        return tables

    def get_json_file_from_datalake(
        storage_account_name: str, file_system: str, file_name: str
    ):
        """
        Retrieves a JSON file from Azure Data Lake Storage and returns its contents as a dictionary.

        Args:
            storage_account_name (str): The name of the Azure Storage account.
            file_system (str): The name of the file system in the Azure Data Lake Storage.
            file_name (str): The name of the JSON file to retrieve.

        Returns:
            dict: The contents of the JSON file as a dictionary.

        Raises:
            Any exceptions that may occur during the retrieval process.

        """
        from azure.identity import ClientSecretCredential
        from azure.storage.filedatalake import DataLakeServiceClient
        import tempfile
        import json

        account_url = f"https://{storage_account_name}.dfs.core.windows.net/cdh"
        secret_scope = constants.get_secret_scope()
        applicationId = dbutils.secrets.get(scope=secret_scope, key="cdh-adb-client-id")
        # Application (Client) Secret Key
        authenticationKey = dbutils.secrets.get(
            scope=secret_scope, key="cdh-adb-client-secret"
        )
        # Directory (Tenant) ID
        tenantId = dbutils.secrets.get(scope=secret_scope, key="cdh-adb-tenant-id")

        credential = ClientSecretCredential(
            client_id=applicationId, client_secret=authenticationKey, tenant_id=tenantId
        )

        service_client = DataLakeServiceClient(
            account_url=account_url, credential=credential
        )

        directory_client = service_client.get_file_system_client(
            file_system=file_system
        )
        file_client = directory_client.get_file_client(file_name)
        download = file_client.download_file()
        downloaded_bytes = download.readall()
        temp_file_path = tempfile.gettempdir()
        file_local_path = f"{temp_file_path}/{file_name}"
        with open(file_local_path, "wb") as my_file:
            my_file.write(downloaded_bytes)
            my_file.close()

        file_object = open(file_local_path, "r")
        file_text = file_object.read()
        config_json = json.loads(file_text)
        return config_json

    def get_notification_service_url():
        """
        Retrieves the URL of the CDH email notification logic app from the secret store.

        Returns:
            str: The URL of the CDH email notification logic app.
        """
        scope = constants.get_secret_scope()
        notifier_url = dbutils.secrets.get(
            scope=scope, key="cdh-email-notification-logicapp-url"
        )
        return notifier_url

    def get_app_environment():
        """
        Returns the CDH environment.

        :return: The CDH environment.
        """
        return constants.CDH_ENVIRONMENT
