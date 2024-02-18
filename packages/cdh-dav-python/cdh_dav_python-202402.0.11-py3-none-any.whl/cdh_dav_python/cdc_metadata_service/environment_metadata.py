""" Module for environment_metadata for the developer service with
metadata config file dependencies. """


# core
import sys  # don't remove required for error handling
import os
from pathlib import Path

# text
import json
from html.parser import HTMLParser  # web scraping html

import logging.config

# data
import logging
import uuid
from datetime import datetime

# Import from sibling directory ..\cdc_tech_environment_service
OS_NAME = os.name
sys.path.append("..")

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

# cdh
from cdh_dav_python.cdc_security_service import (
    security_core as cdh_sec_core,
)

from cdh_dav_python.cdc_tech_environment_service import (
    environment_file as cdc_environment_file,
)


from cdh_dav_python.az_storage_service import (
    az_storage_file as az_file,
)


from cdh_dav_python.cdc_metadata_service import (
    logging_metadata as cdh_log_metadata,
)

from cdh_dav_python.cdc_admin_service.environment_logging import LoggerSingleton
from cdh_dav_python.az_key_vault_service.az_key_vault import AzKeyVault

from dotenv import load_dotenv, find_dotenv, set_key

# spark
from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.functions import col, concat_ws, lit, udf, trim
from pyspark.sql.types import StringType, StructType

# http
import requests

# Import from sibling directory ..\databricks_service
OS_NAME = os.name

uuid_udf = udf(lambda: str(uuid.uuid4()), StringType())

# Get the currently running file name
NAMESPACE_NAME = os.path.basename(os.path.dirname(__file__))
# Get the parent folder name of the running file
SERVICE_NAME = os.path.basename(__file__)


class EnvironmentMetaData:
    """This is a conceptual class representation of an Environment
    It is a static class libary
    Todo
    Note which variables require manual updates from the centers and which
    can be prepopulated
    Note which variables are EDAV or Peraton specific
    Separate out config.devops.dev, config.cdh.dev and config.core.dev
    """

    @classmethod
    def check_configuration_files(
        cls, config: dict, dbutils: object, data_product_id, environment
    ) -> dict:
        """Takes in config dictionary and dbutils objects, returns populated
            check_files dictionary with check results

        Args:
            config (dict): global config dictionary
            dbutils (object): databricks dbutils object

        Returns:
            dict: check_files dictionary with results of file configuration
                    checks
        """

        tracer, logger = LoggerSingleton.instance(
            NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
        ).initialize_logging_and_tracing()

        with tracer.start_as_current_span("check_configuration_files"):
            try:
                sp_client_id = config["az_sub_client_id"]
                sp_tenant_id = config["az_sub_tenant_id"]
                sp_subscription_id = config["az_sub_subscription_id"]
                sp_client_secret = config["client_secret"]
                running_local = config["running_local"]
                # confirm ingress_folder
                ingress_folder = config["cdh_folder_ingress"]
                ingress_folder_files_exists = str(
                    cls.file_exists(
                        running_local,
                        ingress_folder,
                        dbutils,
                        data_product_id,
                        environment,
                        sp_client_id,
                        sp_client_secret,
                        sp_tenant_id,
                    )
                )

                # confirm cdh_folder_config
                cdh_folder_config = config["cdh_folder_config"]
                cdh_folder_config_files_exists = str(
                    cls.file_exists(
                        running_local,
                        cdh_folder_config,
                        dbutils,
                        data_product_id,
                        environment,
                    )
                )

                # confirm database path
                cdh_folder_database = config.get("cdh_folder_database")
                files_exists = cls.file_exists(
                    running_local,
                    cdh_folder_database,
                    dbutils,
                    data_product_id,
                    environment,
                    sp_client_id,
                    sp_subscription_id,
                    sp_tenant_id,
                )
                cdh_folder_database_files_exists = str(files_exists)

                s_text = f"ingress_folder_files_exists exists test result:\
                    {ingress_folder_files_exists}"
                s_text_1 = f"cdh_folder_database_files_exists exists test result:\
                    {cdh_folder_database_files_exists}"
                s_text_2 = f"{config.get('cdh_database_name')} at cdh_folder_database:\
                    {cdh_folder_database}"
                ingress_folder_files_exists_test = s_text
                cdh_folder_config_files_exists_test = f"cdh_folder_config_files_exists exists\
                    test result: {cdh_folder_config_files_exists}"
                check_files = {
                    "cdh_folder_ingress": f"{ingress_folder}",
                    "ingress_folder_files_exists_test": ingress_folder_files_exists_test,
                    "cdh_folder_config": f"{cdh_folder_config}",
                    "cdh_folder_config_files_exists_test": cdh_folder_config_files_exists_test,
                    "cdh_folder_database": f"{cdh_folder_database}",
                    "cdh_folder_database_files_exists test": s_text_1,
                    "creating new cdh_database_name": s_text_2,
                }

                logger.info(f"check_files:{check_files}")
                return check_files

            except Exception as ex:
                error_msg = "Error: %s", ex
                exc_info = sys.exc_info()
                LoggerSingleton.instance(
                    NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
                ).error_with_exception(error_msg, exc_info)
                raise

    @classmethod
    def get_job_list(
        cls,
        job_name: str,
        config: dict,
        spark: SparkSession,
        data_product_id,
        environment,
    ) -> DataFrame:
        """Get list of jobs actions for a selected job

        Args:
            job_name (str): Selected Job name
            config (dict): Configuration dictionary
            spark (SparkSession): Spark object

        Returns:
            DataFrame: Dataframe with list of job actions
        """

        tracer, logger = LoggerSingleton.instance(
            NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
        ).initialize_logging_and_tracing()

        with tracer.start_as_current_span("get_job_list"):
            try:
                obj_env_log = cdh_log_metadata.LoggingMetaData()

                ingress_folder_sps = config["ingress_folder_sps"]
                ingress_folder_sps = ingress_folder_sps.rstrip("/")
                config_jobs_path = f"{ingress_folder_sps}/bronze_sps_config_jobs.csv"

                data_product_id = config["data_product_id"]
                info_msg = f"config_jobs_path:{config_jobs_path}"
                obj_env_log.log_info(config, info_msg)

                first_row_is_header = "true"
                delimiter = ","
                df_jobs = (
                    spark.read.format("csv")
                    .option("header", first_row_is_header)
                    .option("sep", delimiter)
                    .option("multiline", True)
                    .option("inferSchema", True)
                    .load(config_jobs_path, forceLowercaseNames=True, inferLong=True)
                )
                df_jobs = df_jobs.withColumn("job_name", trim("job"))
                df_jobs = df_jobs.filter(df_jobs.job_name == job_name)
                data = df_jobs.limit(20).collect()  # Limiting to 20 rows for safety
                data_str = "\n".join(str(row) for row in data)
                logger.info("DataFrame content:\n" + data_str)

                return df_jobs

            except Exception as ex:
                error_msg = "Error: %s", ex
                exc_info = sys.exc_info()
                LoggerSingleton.instance(
                    NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
                ).error_with_exception(error_msg, exc_info)
                raise

    @classmethod
    def get_column_list(
        cls,
        config: dict,
        spark: SparkSession,
        dbutils: object,
        data_product_id: str,
        environment: str,
    ) -> DataFrame:
        """Takes in dataset config dictionary, spark object, dbutils object\
        and returns dataframe
        with list of columns for dataset

        Args:
            config (dict): dataset config dictionary
            spark (SparkSession): spark session
            dbutils (object): databricks dbutils object

        Returns:
            DataFrame: dataframe popluated with list of columns for dataset
        """

        tracer, logger = LoggerSingleton.instance(
            NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
        ).initialize_logging_and_tracing()

        with tracer.start_as_current_span("get_column_list"):
            try:
                first_row_is_header = "true"
                delimiter = ","

                dataset_name = config["dataset_name"]
                running_local = config["running_local"]
                ingress_folder_sps = config["ingress_folder_sps"]
                data_product_id = config["data_product_id"]
                ingesttimestamp = datetime.now()

                file_path = f"{ingress_folder_sps}bronze_sps_config_columns.csv"
                # check if size of file is 0
                client_id = config["az_sub_client_id"]
                tenant_id = config["az_sub_tenant_id"]
                client_secret = config["client_secret"]
                file_size = cls.get_file_size(
                    running_local,
                    file_path,
                    dbutils,
                    data_product_id,
                    environment,
                    spark,
                    client_id,
                    client_secret,
                    tenant_id,
                )

                logger.info(f"file_size: {str(file_size)}")

                # default to empty DataFrame
                df_results = spark.createDataFrame([], StructType([]))

                if file_size > 0:
                    df_results = (
                        spark.read.format("csv")
                        .option("header", first_row_is_header)
                        .option("sep", delimiter)
                        .option("inferSchema", True)
                        .option("inferLong", True)
                        .option("multiline", True)
                        .option("inferDecimal", True)
                        .option("inferInteger", True)
                        .option("forceLowercaseNames", True)
                        .load(file_path)
                        .withColumn("meta_ingesttimestamp", lit(ingesttimestamp))
                        .withColumn(
                            "row_id",
                            concat_ws(
                                "-",
                                col("data_product_id"),
                                col("dataset_name"),
                                col("column_name"),
                            ),
                        )
                    )

                    # bronze_sps_config_columns_df.select(col("column_batch_group").cast("int").as("column_batch_group"))
                    if df_results.count() == 0:
                        logger.info("File hase 0 rows")
                    else:
                        if dataset_name == "sps":
                            project_filter = f"(data_product_id == '{data_product_id}')"
                            df_results = df_results.filter(project_filter)
                else:
                    logger.error(
                        f"{ingress_folder_sps}bronze_sps_config_columns.csv file_size indicates is empty"
                    )

                return df_results

            except Exception as ex:
                error_msg = "Error: %s", ex
                exc_info = sys.exc_info()
                LoggerSingleton.instance(
                    NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
                ).error_with_exception(error_msg, exc_info)
                raise

    @staticmethod
    def get_file_size(
        running_local: bool,
        file_path: str,
        dbutils,
        data_product_id: str,
        environment: str,
        spark,
        client_id: str = None,
        client_secret: str = None,
        tenant_id: str = None,
    ) -> int:
        """Gets the file size in bytes for the specified file path.

        Args:
            running_local (bool): Indicates whether the code is running locally or in a distributed environment.
            file_path (str): The path of the file for which to retrieve the size.
            dbutils: The dbutils object for interacting with Databricks utilities.
            spark: The SparkSession object for running Spark jobs.
            client_id (str, optional): The client ID for authentication (if applicable). Defaults to None.
            client_secret (str, optional): The client secret for authentication (if applicable). Defaults to None.
            tenant_id (str, optional): The tenant ID for authentication (if applicable). Defaults to None.

        Returns:
            int: The size of the file in bytes.
        """

        obj_env_file = cdc_environment_file.EnvironmentFile()
        file_size = obj_env_file.get_file_size(
            running_local,
            file_path,
            dbutils,
            spark,
            data_product_id,
            environment,
            client_id,
            client_secret,
            tenant_id,
        )
        return file_size

    @staticmethod
    def file_exists(
        running_local: bool,
        path: str,
        dbutils,
        data_product_id: str,
        environment: str,
        sp_client_id: str = None,
        sp_client_secret: str = None,
        sp_tenant_id: str = None,
    ) -> bool:
        """
        Check if a file exists in the specified environment.

        Args:
            running_local (bool): Indicates whether the code is running locally or not.
            path (str): The path of the file to check.
            dbutils: The dbutils object for interacting with Databricks.
            data_product_id (str): The ID of the data product.
            environment (str): The name of the environment.
            sp_client_id (str, optional): The client ID for the service principal authentication. Defaults to None.
            sp_client_secret (str, optional): The client secret for the service principal authentication. Defaults to None.
            sp_tenant_id (str, optional): The tenant ID for the service principal authentication. Defaults to None.

        Returns:
            bool: True if the file exists, False otherwise.
        """

        obj_env_file = az_file.AzStorageFile()
        file_exists = obj_env_file.file_exists(
            running_local,
            path,
            data_product_id,
            environment,
            dbutils,
            sp_client_id,
            sp_client_secret,
            sp_tenant_id,
        )
        return file_exists

    @staticmethod
    def convert_to_windows_dir(
        path: str, data_product_id: str, environment: str
    ) -> str:
        """Takes in path and returns path with backslashes converted to forward slashes

        Args:
            path (str): path to be converted

        Returns:
            str: converted path
        """
        obj_env_file = cdc_environment_file.EnvironmentFile()
        converted_path = obj_env_file.convert_to_windows_dir(
            path, data_product_id, environment
        )
        return converted_path

    @staticmethod
    def convert_to_current_os_dir(
        path: str, data_product_id: str, environment: str
    ) -> str:
        """Takes in path and returns path with backslashes converted to forward slashes

        Args:
            path (str): path to be converted

        Returns:
            str: converted path
        """
        obj_env_file = cdc_environment_file.EnvironmentFile()
        converted_path = obj_env_file.convert_to_current_os_dir(
            path, data_product_id, environment
        )
        return converted_path

    @staticmethod
    def load_environment(
        running_local: bool,
        sp_tenant_id: str,
        sp_subscription_id: str,
        sp_client_id: str,
        environment: str,
        data_product_id: str,
        dbutils,
        application_insights_connection_string: str,
        az_sub_oauth_token_endpoint: str,
    ):
        """
        Loads the environment file to configure the environment for the application.

        Args:
            running_local (bool): A flag indicating whether the application is running locally or deployed.
            sp_tenant_id (str): The Azure Active Directory tenant (directory) ID.
            sp_subscription_id (str): The ID of the Azure subscription.
            sp_client_id (str): The Azure service principal's client (application) ID.
            environment (str): The deployment environment (e.g., 'dev', 'test', 'prod').
            data_product_id (str): The project ID to which the application belongs.
            dbutils: Databricks utilities object, which provides access to the Databricks filesystem and secrets, etc.
            application_insights_connection_string (str): The connection string for Azure Application Insights for application monitoring.
        """

        logger = logging.getLogger(data_product_id)
        logger.setLevel(logging.DEBUG)

        path = sys.executable + "\\.."
        sys.path.append(os.path.dirname(os.path.abspath(path)))
        env_path = os.path.dirname(os.path.abspath(path))

        if dbutils is None:
            running_local = True
        if running_local is True:
            logger.info(f"running_local: {running_local}")
            if OS_NAME.lower() == "nt":
                logger.info("windows")
                env_share_path = env_path + "\\share"
                folder_exists = os.path.exists(env_share_path)
                if not folder_exists:
                    # Create a new directory because it does not exist
                    os.makedirs(env_share_path)
                env_share_path_2 = sys.executable + "\\..\\share"
                sys.path.append(os.path.dirname(os.path.abspath(env_share_path_2)))
                env_file_path = env_share_path + "\\.env"
                logger.info(f"env_file_path: {env_file_path}")
                # don't delete line below - it creates the file
            else:
                logger.info("non windows")
                # env_share_path = env_path + "/share"
                env_share_path = os.path.expanduser("~") + "/share"
                folder_exists = os.path.exists(env_share_path)
                if not folder_exists:
                    # Create a new directory because it does not exist
                    os.makedirs(env_share_path)
                env_share_path_2 = sys.executable + "/../share"
                sys.path.append(os.path.dirname(os.path.abspath(env_share_path_2)))
                env_file_path = env_share_path + "/.env"
                logger.info(f"env_file_path: {env_file_path}")
                # don't delete line below - it creates the file

            open(env_file_path, "w+", encoding="utf-8")
            dotenv_file = find_dotenv(env_file_path)
            logger.info(f"dotenv_file: {dotenv_file}")
            set_key(dotenv_file, "AZURE_TENANT_ID", sp_tenant_id)
            set_key(dotenv_file, "AZURE_SUBSCRIPTION_ID", sp_subscription_id)
            set_key(dotenv_file, "az_sub_client_id", sp_client_id)
        else:
            logger.info(f"running_local: {running_local}")
            env_share_path = os.path.expanduser("~") + "/share"
            folder_exists = os.path.exists(env_share_path)
            if not folder_exists:
                # Create a new directory because it does not exist
                os.makedirs(env_share_path)
            env_share_path_2 = sys.executable + "/../share"
            sys.path.append(os.path.dirname(os.path.abspath(env_share_path_2)))
            env_file_path = env_share_path + "/.env"
            env_file = open(env_file_path, "w+", encoding="utf-8")
            logger.info(f"env_file_path: {env_file_path}")
            dotenv_file = find_dotenv(env_file_path)

            # env_file_path = f"/mnt/{environment}/{data_product_id}"
            # print(f"env_file_path: {env_file_path}")
            # env_file_path = env_file_path + "/config/config_{environment}.txt"
            # dbutils.fs.put(
            #     env_file_path,
            #     f"""AZURE_TENANT_ID {sp_tenant_id}
        # AZURE_SUBSCRIPTION_ID {subscription_id}
        # az_sub_client_id {sp_client_id}
        #  """,
        #     True,
        # )

        # Define the desired connection string
        # DEV
        environment = environment.strip().lower()
        if environment == "dev":
            default_connection_string = "InstrumentationKey=8f02ef9a-cd94-48cf-895a-367f102e8a24;IngestionEndpoint=https://eastus-8.in.applicationinsights.azure.com/;LiveEndpoint=https://eastus.livediagnostics.monitor.azure.com/"
        # PROD
        else:
            default_connection_string = "InstrumentationKey=d091b27b-14e0-437f-ae3c-90f3f04ef3dc;IngestionEndpoint=https://eastus-8.in.applicationinsights.azure.com/;LiveEndpoint=https://eastus.livediagnostics.monitor.azure.com/"

        message = f"default_connection_string: {default_connection_string}"
        logger.info(message)
        print(message)

        # Check if the variable is blank (not set or empty)
        if not application_insights_connection_string:
            application_insights_connection_string = default_connection_string

        message = f"application_insights_connection_string: {application_insights_connection_string}"
        logger.info(message)
        print(message)

        set_key(
            dotenv_file,
            "APPLICATIONINSIGHTS_CONNECTION_STRING",
            application_insights_connection_string,
        )

        set_key(dotenv_file, "AZURE_AUTHORITY_HOST ", az_sub_oauth_token_endpoint)
        set_key(dotenv_file, "PYARROW_IGNORE_TIMEZONE", "1")

        message = f"dotenv_file: {dotenv_file}"
        logger.info(message)
        print(message)

        load_dotenv(dotenv_file)

        return env_file_path

    @staticmethod
    def format_key(key):
        """
        Formats the given key by replacing all '-' with '_' and stripping whitespace from both ends.

        Args:
            key (str): The key to be formatted.

        Returns:
            str: The formatted key.
        """
        return key.replace("-", "_").strip()

    @classmethod
    def process_parameters(cls, parameters, dbutils):
        """
        Process the parameters for the metadata service.

        Args:
            cls: The class object.
            parameters (dict): The parameters to be processed.
            dbutils: The dbutils object.

        Returns:
            Tuple: A tuple containing the processed parameters and other variables.
        """

        data_product_id = parameters["data_product_id"]
        environment = parameters["environment"]

        tracer, logger = LoggerSingleton.instance(
            NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
        ).initialize_logging_and_tracing()

        with tracer.start_as_current_span("process_parameters"):
            try:
                parameters.setdefault("running_local", False)
                parameters.setdefault("dataset_name", "na")
                parameters.setdefault("cicd_action", "na")

                running_local = str(parameters.get("running_local", False)).lower() in [
                    "true",
                    "1",
                    "t",
                    "y",
                    "yes",
                ]
                if dbutils is None:
                    running_local = True

                parameters["running_local"] = running_local

                data_product_id_root = parameters["data_product_id_root"]
                # Get the current year
                current_year = str(datetime.now().year)
                # Retrieve the parameter 'yyyy', and if it's not present, default to the current year
                yyyy_param = parameters.get("yyyy", current_year)
                # Get the current month
                current_month = datetime.now().strftime("%m")
                # Retrieve the parameter 'mm', and if it's not present, default to the current month
                mm_param = parameters.get("mm", current_month)
                # Get the current day
                current_day = datetime.now().strftime("%d")
                # Retrieve the parameter 'dd', and if it's not present, default to the current day
                dd_param = parameters.get("dd", current_day)

                dataset_name = parameters["dataset_name"]
                cicd_action = parameters["cicd_action"]
                repository_path = parameters["repository_path"]

                repository_path = (
                    repository_path.split("cdh_dav_python")[0] + "cdh_dav_python"
                    if "cdh_dav_python" in repository_path
                    else repository_path
                )

                repository_path = cls.convert_to_current_os_dir(
                    repository_path, data_product_id, environment
                )

                logger.info(f"repository_path: {repository_path}")

                return (
                    parameters,
                    running_local,
                    data_product_id,
                    environment,
                    data_product_id_root,
                    yyyy_param,
                    mm_param,
                    dd_param,
                    dataset_name,
                    cicd_action,
                    repository_path,
                )

            except Exception as ex:
                error_msg = "Error: %s", ex
                exc_info = sys.exc_info()
                LoggerSingleton.instance(
                    NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
                ).error_with_exception(error_msg, exc_info)
                raise

    @classmethod
    def get_environment_json_path(
        cls,
        repository_path,
        data_product_id,
        environment,
        data_product_id_root,
        running_local,
        dbutils,
    ):
        """
        Retrieves the environment paths for a given repository, data product ID, and environment.

        Args:
            cls (class): The class object.
            repository_path (str): The path to the repository.
            data_product_id (str): The ID of the data product.
            environment (str): The environment name.
            data_product_id_root (str): The ID of the data product root.

        Returns:
            Tuple: Containing the environment JSON path and repository_path.
        """

        tracer, logger = LoggerSingleton.instance(
            NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
        ).initialize_logging_and_tracing()

        with tracer.start_as_current_span("get_environment_paths"):
            try:
                config_string = "config"

                env_folder_path = f"{repository_path.rstrip('/')}/{data_product_id_root}/{data_product_id}/"
                env_folder_path = cls.convert_to_current_os_dir(
                    env_folder_path, data_product_id, environment
                )
                if os.path.exists(env_folder_path) and os.path.isdir(env_folder_path):
                    logger.info(
                        f"The env_folder_path directory {env_folder_path} exists."
                    )
                else:
                    logger.info(
                        f"The env_folder_path directory {env_folder_path} does not exist."
                    )
                    two_levels_up = (
                        os.path.dirname(os.path.dirname(env_folder_path)) + "/"
                    )
                    two_levels_up = cls.convert_to_current_os_dir(
                        two_levels_up, data_product_id, environment
                    )
                    env_folder_path = two_levels_up
                    if os.path.exists(env_folder_path) and os.path.isdir(
                        env_folder_path
                    ):
                        logger.info(
                            f"The env_folder_path directory {env_folder_path} exists."
                        )
                    else:
                        raise ValueError(
                            f"The env_folder_path directory {env_folder_path} does not exist."
                        )

                cdh_folder_config_path = f"{env_folder_path}{config_string}/"
                logger.info(f"cdh_folder_config_path:{cdh_folder_config_path}")
                cdh_folder_config_path = cls.convert_to_current_os_dir(
                    cdh_folder_config_path, data_product_id, environment
                )

                cdh_folder_config_path = cls.convert_to_current_os_dir(
                    cdh_folder_config_path, data_product_id, environment
                )

                environment_json_path = (
                    f"{cdh_folder_config_path}{config_string}.{environment}.json"
                )
                environment_json_path_default = (
                    f"{cdh_folder_config_path}{config_string}.{environment}.json"
                )

                # Check if environment_json_path exists

                check_1_attempt = f"check 1 attempt: {environment_json_path}"
                logger.info(check_1_attempt)

                client_id = None
                client_secret = None

                if not cls.file_exists(
                    running_local,
                    environment_json_path,
                    dbutils,
                    data_product_id,
                    environment,
                    client_id,
                    client_secret,
                ):
                    check_1 = f"check 1: {environment_json_path}"
                    logger.info(check_1)
                    repository_path_temp = os.getcwd()
                    repository_path_temp = str(Path(repository_path_temp)).rstrip("/")
                    repository_path_temp = f"{repository_path_temp}/{data_product_id_root}/{data_product_id}/{config_string}/"
                    repository_path_temp = cls.convert_to_current_os_dir(
                        repository_path_temp, data_product_id, environment
                    )
                    environment_json_path = (
                        f"{repository_path_temp}{config_string}.{environment}.json"
                    )
                    check_2_attempt = f"check 2 attempt: {environment_json_path}"
                    logger.info(check_2_attempt)

                    if not cls.file_exists(
                        running_local,
                        environment_json_path,
                        dbutils,
                        data_product_id,
                        environment,
                        client_id,
                        client_secret,
                    ):
                        check_2 = f"check 2: {environment_json_path}"
                        logger.info(check_2)
                        repository_path_temp = os.getcwd()
                        repository_path_temp = str(
                            Path(repository_path_temp).parent
                        ).rstrip("/")
                        repository_path_temp = f"{repository_path_temp}/{data_product_id_root}/{data_product_id}/{config_string}/"
                        repository_path_temp = cls.convert_to_current_os_dir(
                            repository_path_temp, data_product_id, environment
                        )
                        environment_json_path = (
                            f"{repository_path_temp}{config_string}.{environment}.json"
                        )
                        check_3_attempt = f"check 3 attempt: {environment_json_path}"
                        logger.info(check_3_attempt)

                        if not cls.file_exists(
                            running_local,
                            environment_json_path,
                            dbutils,
                            data_product_id,
                            environment,
                            client_id,
                            client_secret,
                        ):
                            check_3 = f"check 3: {environment_json_path}"
                            logger.info(check_3)
                            # Try two levels up from the current folder
                            repository_path_temp = os.getcwd()
                            repository_path_temp = str(
                                Path(repository_path_temp).parent.parent
                            ).rstrip("/")
                            repository_path_temp = f"{repository_path_temp}/{data_product_id_root}/{data_product_id}/{config_string}/"
                            repository_path_temp = cls.convert_to_current_os_dir(
                                repository_path_temp, data_product_id, environment
                            )
                            environment_json_path = f"{repository_path_temp}{config_string}.{environment}.json"
                            check_4_attempt = (
                                f"check 4 attempt: {environment_json_path}"
                            )
                            logger.info(check_4_attempt)
                            if not cls.file_exists(
                                running_local,
                                environment_json_path,
                                dbutils,
                                data_product_id,
                                environment,
                                client_id,
                                client_secret,
                            ):
                                check_4 = f"check 4: {environment_json_path}"
                                logger.info(check_4)
                                repository_path_temp = os.getcwd()
                                repository_path_temp = str(
                                    Path(repository_path_temp).parent.parent.parent
                                ).rstrip("/")
                                repository_path_temp = cls.convert_to_current_os_dir(
                                    repository_path_temp, data_product_id, environment
                                )
                                repository_path_temp = f"{repository_path_temp}/{data_product_id_root}/{data_product_id}/{config_string}/"
                                repository_path_temp = cls.convert_to_current_os_dir(
                                    repository_path_temp, data_product_id, environment
                                )
                                environment_json_path = f"{repository_path_temp}{config_string}.{environment}.json"
                                check_5_attempt = (
                                    f"check 5 attempt: {environment_json_path}"
                                )
                                logger.info(check_5_attempt)

                                if not cls.file_exists(
                                    running_local,
                                    environment_json_path,
                                    dbutils,
                                    data_product_id,
                                    environment,
                                    client_id,
                                    client_secret,
                                ):
                                    check_5 = f"check 5: {environment_json_path}"
                                    logger.info(check_5)
                                    error_message = f"Environment file not found: {check_1}, {check_2}, {check_3}, {check_4}, {check_5}"
                                    logger.error(error_message)
                                    environment_json_path = (
                                        environment_json_path_default
                                    )
                                    # TODO: Address below
                                    logger.info(
                                        "Continuing with default environment file. Check file not aways working on server"
                                    )
                                else:
                                    logger.info(
                                        f"config exists: {environment_json_path}"
                                    )
                            else:
                                logger.info(f"config exists: {environment_json_path}")
                        repository_path = repository_path_temp
                    else:
                        logger.info(f"config exists: {environment_json_path}")
                        repository_path = env_folder_path

                logger.info(f"repository_path: {repository_path}")
                logger.info(f"environment_json_path: {environment_json_path}")
                return environment_json_path, repository_path

            except Exception as ex:
                error_msg = "Error: %s", ex
                exc_info = sys.exc_info()
                LoggerSingleton.instance(
                    NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
                ).error_with_exception(error_msg, exc_info)
                raise

    @classmethod
    def get_cicd_action_path(
        cls,
        repository_path: str,
        data_product_id_root: str,
        cicd_action,
        data_product_id: str,
        environment: str,
    ):
        """
        Get the path for the CICD action file based on the repository path, data product ID root, data product ID, and environment.

        Args:
            repository_path (str): The path to the repository.
            data_product_id_root (str): The root of the data product ID.
            data_product_id (str): The data product ID.
            environment (str): The environment.

        Returns:
            str: The path for the CICD action file.
        """

        cicd_action_string = "cicd"
        cicd_folder = f"{repository_path}{data_product_id_root}/{data_product_id}/{cicd_action_string}/"
        cicd_folder = cls.convert_to_current_os_dir(
            cicd_folder, data_product_id, environment
        )
        cicd_action_path = f"{cicd_folder}" + f"{cicd_action}" + f".{environment}.json"
        return cicd_action_path

    @classmethod
    def process_configuration(
        cls,
        running_local: str,
        yyyy_param: str,
        mm_param: str,
        dd_param: str,
        dataset_name: str,
        cicd_action: str,
        repository_path: str,
        environment_json_path: str,
        config: dict,
    ):
        """
        Process the configuration parameters and return the updated config dictionary.

        Args:
            cls: The class object.
            running_local (str): The running local parameter.
            yyyy_param (str): The yyyy parameter.
            mm_param (str): The mm parameter.
            dd_param (str): The dd parameter.
            dataset_name (str): The dataset name.
            cicd_action (str): The CI/CD action.
            repository_path (str): The repository path.
            environment_json_path (str): The environment JSON path.
            config (dict): The configuration dictionary.

        Returns:
            dict: The updated configuration dictionary.

        Raises:
            Exception: If an error occurs during the processing.
        """

        data_product_id = config["cdh_data_product_id"]
        environment = config["cdh_environment"]

        tracer, logger = LoggerSingleton.instance(
            NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
        ).initialize_logging_and_tracing()

        with tracer.start_as_current_span("process_configuration"):
            try:
                data_product_id = config["cdh_data_product_id"]
                data_product_id_root = config["cdh_data_product_id_root"]
                environment = config["cdh_environment"]

                # Set CI/CD Action Path Trigger - Not Used Currently
                cicd_action_path = cls.get_cicd_action_path(
                    repository_path,
                    data_product_id_root,
                    cicd_action,
                    data_product_id,
                    environment,
                )

                config["running_local"] = running_local
                config["yyyy"] = yyyy_param
                config["mm"] = mm_param
                config["dd"] = dd_param
                config["dataset_name"] = dataset_name
                config["dataset_type"] = "TABLE"
                config["repository_path"] = repository_path
                config["environment_json_path"] = environment_json_path
                config["cicd_action_path"] = cicd_action_path
                config["ingress_folder_sps"] = "".join(
                    [config["cdh_folder_config"], "cdh/"]
                )
                config["data_product_id"] = config["cdh_data_product_id"]
                config["data_product_id_root"] = config["cdh_data_product_id_root"]
                config["data_product_id_individual"] = config[
                    "cdh_data_product_id_individual"
                ]
                data_product_id_individual = config["data_product_id_individual"]
                config["databricks_instance_id"] = config.get(
                    "cdh_databricks_instance_id"
                )
                config["environment"] = config["cdh_environment"]
                config["override_save_flag"] = "override_with_save"
                config["is_using_dataset_folder_path_override"] = False
                config["is_using_standard_column_names"] = "force_lowercase"
                config["is_export_schema_required_override"] = True
                config[
                    "ingress_mount"
                ] = f"/mnt/{environment}/{data_product_id_individual}/ingress"

                cdh_folder_database = config.get("cdh_folder_database")
                if not cdh_folder_database:
                    schema_dataset_file_path = ""
                else:
                    schema_dataset_file_path = (
                        cdh_folder_database.rstrip("/") + "/bronze_clc_schema"
                    )

                config["schema_dataset_file_path"] = schema_dataset_file_path

                logger.info("Successfuully processed configuration.")
                return config

            except Exception as ex:
                error_msg = "Error: %s", ex
                exc_info = sys.exc_info()
                LoggerSingleton.instance(
                    NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
                ).error_with_exception(error_msg, exc_info)
                raise

    @classmethod
    def get_configuration_common(
        cls, parameters: dict, dbutils, data_product_id: str, environment: str
    ) -> dict:
        """
        Retrieves the common configuration for a given data product and environment.

        Args:
            parameters (dict): A dictionary containing the parameters for the configuration.
            dbutils: The dbutils object for interacting with the database.
            data_product_id (str): The ID of the data product.
            environment (str): The environment for which to retrieve the configuration.

        Returns:
            dict: A dictionary containing the common configuration.

        Raises:
            ValueError: If the configuration directory does not exist.
        """

        data_product_id = data_product_id.lower()
        environment = environment.lower()

        tracer, logger = LoggerSingleton.instance(
            NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
        ).initialize_logging_and_tracing()

        with tracer.start_as_current_span("get_configuration_common"):
            try:
                # Process Parameters
                logger.info(f"initial parameters: {parameters}")
                (
                    parameters,
                    running_local,
                    data_product_id,
                    environment,
                    data_product_id_root,
                    yyyy_param,
                    mm_param,
                    dd_param,
                    dataset_name,
                    cicd_action,
                    repository_path,
                ) = cls.process_parameters(parameters, dbutils)

                # Log Updated Parameters
                logger.info(
                    "Received the following parameters: parameters=%s, running_local=%s, "
                    "data_product_id=%s, environment=%s, data_product_id_root=%s, "
                    "yyyy_param=%s, mm_param=%s, dd_param=%s, dataset_name=%s, "
                    "cicd_action=%s, repository_path=%s",
                    parameters,
                    running_local,
                    data_product_id,
                    environment,
                    data_product_id_root,
                    yyyy_param,
                    mm_param,
                    dd_param,
                    dataset_name,
                    cicd_action,
                    repository_path,
                )

                logger.info(f"initial repository_path:{repository_path}")

                # Get Configuration JSON File Path
                environment_json_path, repository_path = cls.get_environment_json_path(
                    repository_path,
                    data_product_id,
                    environment,
                    data_product_id_root,
                    running_local,
                    dbutils,
                )

                logger.info(f"updated repository_path:{repository_path}")

                # Load Configuration From JSON File
                with open(
                    environment_json_path, mode="r", encoding="utf-8"
                ) as json_file:
                    config = json.load(json_file)

                # Process Configuration
                config = cls.process_configuration(
                    running_local,
                    yyyy_param,
                    mm_param,
                    dd_param,
                    dataset_name,
                    cicd_action,
                    repository_path,
                    environment_json_path,
                    config,
                )

                if config:
                    logger.info(
                        f"Configuration found environment_json_path: {environment_json_path}"
                    )
                else:
                    error_message = "Error: no configurations were found."
                    error_message = (
                        error_message
                        + f"Check your settings file: {environment_json_path}."
                    )
                    raise ValueError(error_message)

                scope = config.get("cdh_databricks_kv_scope")
                kv_client_secret_key = config.get("cdh_oauth_sp_kv_client_secret_key")

                if kv_client_secret_key is not None:
                    if kv_client_secret_key.strip() == "":
                        kv_client_secret_key = None

                sp_redirect_url = config.get("cdh_oauth_sp_redirect_url")
                az_sub_oauth_token_endpoint = config.get("az_sub_oauth_token_endpoint")
                sp_client_id = config["az_sub_client_id"]
                sp_tenant_id = config["az_sub_tenant_id"]
                sp_subscription_id = config["az_sub_subscription_id"]
                sp_azure_databricks_resource_id = config.get(
                    "cdh_oauth_databricks_resource_id"
                )

                az_apin_ingestion_endpoint = config.get("az_apin_ingestion_endpoint")
                az_apin_instrumentation_key = config.get("az_apin_instrumentation_key")
                application_insights_connection_string = f"InstrumentationKey={az_apin_instrumentation_key};IngestionEndpoint={az_apin_ingestion_endpoint}"
                az_sub_oauth_token_endpoint = config.get("az_sub_oauth_token_endpoint")

                # Write changes to .env file - create .env file if it does not exist
                env_file_path = cls.load_environment(
                    running_local,
                    sp_tenant_id,
                    sp_subscription_id,
                    sp_client_id,
                    environment,
                    data_product_id,
                    dbutils,
                    application_insights_connection_string,
                    az_sub_oauth_token_endpoint,
                )

                config["env_file_path"] = env_file_path
                az_sub_client_secret_key = config["az_sub_client_secret_key"]
                sp_authority_host_url = "https://login.microsoftonline.com"
                running_interactive = False

                az_kv_key_vault_name = config.get("az_kv_key_vault_name")

                if running_local is True:
                    if (
                        "sp_client_secret" not in locals()
                        and "sp_client_secret" not in globals()
                    ):
                        sp_client_secret = None

                    if sp_client_secret is None or sp_client_secret == "":
                        running_interactive = True

                    AzKeyVault(
                        sp_tenant_id,
                        sp_client_id,
                        sp_client_secret,
                        az_kv_key_vault_name,
                        running_interactive,
                        data_product_id,
                        environment,
                    )

                    info_message = (
                        f"az_sub_client_secret_key:{az_sub_client_secret_key}"
                    )
                    logger.info(info_message)
                    az_sub_client_secret_key = cls.format_key(az_sub_client_secret_key)
                    sp_client_secret = os.getenv(az_sub_client_secret_key)
                else:
                    message = (
                        f"Retrieving Databricks secret for {az_sub_client_secret_key}."
                    )
                    logger.info(message)
                    logger.info(message)
                    sp_client_secret = dbutils.secrets.get(
                        scope=scope, key=az_sub_client_secret_key
                    )
                    obj_security_core = cdh_sec_core.SecurityCore()

                    config_user = (
                        obj_security_core.acquire_access_token_with_client_credentials(
                            sp_client_id,
                            sp_client_secret,
                            sp_tenant_id,
                            sp_redirect_url,
                            sp_authority_host_url,
                            sp_azure_databricks_resource_id,
                            data_product_id,
                            environment,
                        )
                    )

                    config["redirect_uri"] = config_user["redirect_uri"]
                    config["authority_host_url"] = config_user["authority_host_url"]
                    config["azure_databricks_resource_id"] = config_user[
                        "azure_databricks_resource_id"
                    ]
                    config["az_sub_oauth_token_endpoint"] = config_user[
                        "az_sub_oauth_token_endpoint"
                    ]
                    config["access_token"] = config_user["access_token"]

                config["az_sub_client_id"] = sp_client_id
                config["client_secret"] = sp_client_secret
                config["tenant_id"] = sp_tenant_id

                return config

            except Exception as ex:
                error_msg = "Error: %s", ex
                exc_info = sys.exc_info()
                LoggerSingleton.instance(
                    NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
                ).error_with_exception(error_msg, exc_info)
                raise

    @staticmethod
    def get_dataset_list(
        config: dict, spark: SparkSession, data_product_id: str, environment: str
    ) -> DataFrame:
        """Takes in config dictionary, spark object, returns list of datasets in project

        Args:
            config (dict): global config dictionary
            spark (SparkSession): spark session

        Returns:
            DataFrame: dataframe with list of datasets in project
        """

        tracer, logger = LoggerSingleton.instance(
            NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
        ).initialize_logging_and_tracing()

        with tracer.start_as_current_span("get_dataset_list"):
            try:
                obj_env_log = cdh_log_metadata.LoggingMetaData()

                first_row_is_header = "true"
                delimiter = ","

                csv_file_path = config["ingress_folder_sps"]
                csv_file_path = csv_file_path + "\\"
                csv_file_path = csv_file_path + "bronze_sps_config_datasets.csv"
                data_product_id = config["data_product_id"]
                ingesttimestamp = datetime.now()

                df_results = (
                    spark.read.format("csv")
                    .option("header", first_row_is_header)
                    .option("sep", delimiter)
                    .option("multiline", True)
                    .option("inferSchema", True)
                    .load(csv_file_path, forceLowercaseNames=True, inferLong=True)
                    .withColumn("meta_ingesttimestamp", lit(ingesttimestamp))
                    .withColumn(
                        "row_id",
                        concat_ws("-", col("data_product_id"), col("dataset_name")),
                    )
                )

                # sort
                if df_results.count() > 0:
                    # df_results.show()
                    df_results = df_results.sort("pipeline_batch_group")
                else:
                    err_message = (
                        f"No datasets found for data_product_id:{data_product_id}"
                    )
                    obj_env_log.log_error(data_product_id, err_message)
                    logger.error(err_message)

                return df_results

            except Exception as ex:
                error_msg = "Error: %s", ex
                exc_info = sys.exc_info()
                LoggerSingleton.instance(
                    NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
                ).error_with_exception(error_msg, exc_info)
                raise

    @staticmethod
    def get_pipeline_list(config: dict, spark: SparkSession) -> DataFrame:
        """Takes in config dictionary, spark session object, returns dataframe with list of pipelines in project

        Args:
            config (dict): global config dictionary
            spark (SparkSession): spark session

        Returns:
            DataFrame: dataframe with list of pipelines in project
        """

        first_row_is_header = "true"
        delimiter = ","

        ingress_folder_sps = config["ingress_folder_sps"]
        ingesttimestamp = datetime.now()
        data_product_id = config["data_product_id"]

        bronze_sps_config_pipelines_df = (
            spark.read.format("csv")
            .option("header", first_row_is_header)
            .option("sep", delimiter)
            .option("multiline", True)
            .option("inferSchema", True)
            .load(
                f"{ingress_folder_sps}bronze_sps_config_pipelines.csv",
                forceLowercaseNames=True,
                inferLong=True,
            )
            .withColumn("meta_ingesttimestamp", lit(ingesttimestamp))
            .withColumn(
                "row_id",
                concat_ws("-", col("data_product_id"), col("view_name")),
            )
        )

        bronze_sps_config_pipelines_df = bronze_sps_config_pipelines_df.filter(
            "data_product_id == '" + data_product_id + "' "
        )

        # sort by load group to ensure dependencies are run in order
        bronze_sps_config_pipelines_df = bronze_sps_config_pipelines_df.sort(
            "pipeline_batch_group"
        )

        return bronze_sps_config_pipelines_df

    @classmethod
    def list_files(cls, config: dict, token: str, base_path: str) -> list:
        """Takes in a config dictionary, token and base_path, returns
        populated list of files

        Args:
            config (dict): global config dictionary
            token (str): token
            base_path (str): path to list files

        Returns:
            list: list of files at the path location
        """

        obj_env_log = cdh_log_metadata.LoggingMetaData()

        databricks_instance_id = config["databricks_instance_id"]
        json_text = {"path": base_path}
        headers = {"Authentication": f"Bearer {token}"}
        url = f"https://{databricks_instance_id}/api/2.0/workspace/list"
        data_product_id = config["data_product_id"]
        obj_env_log.log_info(config, f"------- Fetch {base_path}  -------")
        obj_env_log.log_info(config, f"url:{str(url)}")
        headers_redacted = str(headers).replace(token, "[bearer REDACTED]")
        obj_env_log.log_info(config, f"headers:{headers_redacted}")

        response = requests.get(url=url, headers=headers, json=json_text, timeout=120)
        data = None
        results = []

        try:
            response_text = str(response.text)
            data = json.loads(response_text)
            msg = f"Received list_files with length : {len(str(response_text))} when posting to : "
            msg = msg + f"{url} to list files for : {base_path}"
            response_text_fetch = msg
            print("- response : success  -")
            print(f"{response_text_fetch}")
            lst = data["objects"]

            for i in lst:
                if i["object_type"] == "DIRECTORY" or i["object_type"] == "REPO":
                    path = i["path"]
                    results.extend(cls.list_files(config, token, path))
                else:
                    path = i["path"]
                    results.append(path)
        except Exception as exception_object:
            f_filter = HTMLFilter()
            f_filter.feed(response.text)
            response_text = f_filter.text
            print(f"- response : error - {exception_object}")
            print(f"Error converting response text:{response_text} to json")

        return results

    @staticmethod
    def setup_spark_configuration(
        spark: SparkSession, config: dict, data_product_id: str, environment: str
    ) -> SparkSession:
        """Takes spark session, global config dictionary
        and return configured Spark session

        Args:
            spark (SparkSession): spark session
            config (dict): global config dictionary

        Returns:
            SparkSession: configured spark session
        """

        tracer, logger = LoggerSingleton.instance(
            NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
        ).initialize_logging_and_tracing()

        with tracer.start_as_current_span("setup_spark_configuration"):
            try:
                c_ep = config["az_sub_oauth_token_endpoint"]
                c_id = config["az_sub_client_id"]
                c_secret = config["client_secret"]
                sp_tenant_id = config["az_sub_tenant_id"]
                running_local = config["running_local"]

                client_secret_exists = True
                if c_id is None or c_secret is None:
                    client_secret_exists = False
                storage_account = config["cdh_azure_storage_account"]

                client_token_provider = (
                    "org.apache.hadoop.fs.azurebfs.oauth2.ClientCredsTokenProvider"
                )
                provider_type = "OAuth"

                # stack overflow example
                fs_prefix_e1 = "fs.azure.account.auth."
                fso_prefix_e1 = "fs.azure.account.oauth"
                fso2_prefix_e1 = "fs.azure.account.oauth2"
                fso3_prefix_e1 = "fs.azure.account.oauth2.client.secret"  # spark.hadoop
                fs_suffix_e1 = f".{storage_account}.dfs.core.windows.net"
                fso3_prefix_e1 = fso3_prefix_e1 + fs_suffix_e1

                if client_secret_exists is None:
                    client_secret_exists = False

                logger.info(f"client_secret_exists:{str(client_secret_exists)}")
                logger.info(f"endpoint:{str(c_ep)}")

                # config["run_as"] = "service_principal"
                config["run_as"] = "remote_user"
                run_as = config["run_as"]
                logger.info(f"running databricks access using run_as:{run_as}")

                if (
                    client_secret_exists is True
                    and run_as == "service_principal"
                    and running_local is True
                ):
                    spark.conf.set(f"{fs_prefix_e1}type{fs_suffix_e1}", provider_type)
                    spark.conf.set(
                        f"{fso_prefix_e1}.provider.type{fs_suffix_e1}",
                        client_token_provider,
                    )
                    spark.conf.set(f"{fso2_prefix_e1}.client.id{fs_suffix_e1}", c_id)
                    spark.conf.set(
                        f"{fso2_prefix_e1}.client.secret{fs_suffix_e1}", c_secret
                    )
                    client_endpoint_e1 = (
                        f"https://login.microsoftonline.com/{sp_tenant_id}/oauth2/token"
                    )
                    spark.conf.set(
                        f"{fso2_prefix_e1}.client.endpoint{fs_suffix_e1}",
                        client_endpoint_e1,
                    )

                    logger.log_info(
                        config,
                        f'spark.conf.set "({fs_prefix_e1}type{fs_suffix_e1}", "{provider_type}")',
                    )
                    logger.log_info(
                        config,
                        f'spark.conf.set "({fso_prefix_e1}.provider.type{fs_suffix_e1}", \
                        "{client_token_provider}")',
                    )
                    logger.log_info(
                        config,
                        f'spark.conf.set "({fso2_prefix_e1}.client.id{fs_suffix_e1}", "{c_id}")',
                    )
                    logger.log_info(
                        config,
                        f'spark.conf.set "{fso2_prefix_e1}.client.endpoint{fs_suffix_e1}" \
                        = "{client_endpoint_e1}"',
                    )

                spark.conf.set("spark.databricks.io.cache.enabled", "true")
                # Enable Arrow-based columnar data transfers
                spark.conf.set("spark.sql.execution.arrow.enabled", "true")
                # sometimes azure storage has a delta table not found bug - in that scenario try filemount above
                spark.conf.set("spark.sql.execution.arrow.fallback.enabled", "true")
                spark.conf.set("spark.databricks.pyspark.enablePy4JSecurity", "false")
                # Enable Delta Preview
                spark.conf.set("spark.databricks.delta.preview.enabled ", "true")

                if running_local is False:
                    os.environ["PYARROW_IGNORE_TIMEZONE"] = "1"
                    spark.sql(
                        "SET spark.databricks.delta.schema.autoMerge.enabled = true"
                    )
                    cdh_folder_checkpoint = config["cdh_folder_checkpoint"]
                    logger.info(f"cdh_folder_checkpoint: {cdh_folder_checkpoint}")
                    spark.sparkContext.setCheckpointDir(cdh_folder_checkpoint)

                # Checkpoint
                return spark

            except Exception as ex:
                error_msg = "Error: %s", ex
                exc_info = sys.exc_info()
                LoggerSingleton.instance(
                    NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
                ).error_with_exception(error_msg, exc_info)
                raise


class HTMLFilter(HTMLParser):
    """Parses HTMLData

    Args:
        HTMLParser (_type_): _description_
    """

    text = ""

    def handle_data(self, data):
        """Parses HTMLData

        Args:
            data (_type_): _description_
        """
        self.text += data
