"""Module to conditionally execute transform logic for silver and gold pipelines based on project metadata
   including creating Databricks views and/or tables.
"""

import os
import sys  # don't remove required for error handling

from pathlib import Path
from importlib import util  # library management
import cdh_dav_python.databricks_service.notebook as dbx_notebook

pyspark_pandas_loader = util.find_spec("pyspark.pandas")
pyspark_pandas_found = pyspark_pandas_loader is not None

if pyspark_pandas_found:
    # import pyspark.pandas  as pd
    # bug - pyspark version will not read local files in the repo
    os.environ["PYARROW_IGNORE_TIMEZONE"] = "1"
    import pyspark.pandas as pd
else:
    import pandas as pd


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


# Get the currently running file name
NAMESPACE_NAME = os.path.basename(os.path.dirname(__file__))
# Get the parent folder name of the running file
SERVICE_NAME = os.path.basename(__file__)

from cdh_dav_python.cdc_admin_service.environment_logging import LoggerSingleton

import cdh_dav_python.databricks_service.sql as databricks_sql
import cdh_dav_python.az_key_vault_service.az_key_vault as az_key_vault
import cdh_dav_python.cdc_tech_environment_service.environment_core as az_environment_core


class PipelineMetaData:
    """Class to conditionally execute transform logic for silver and gold pipelines based on project metadata
    including creating Databricks views and/or tables.
    """

    @classmethod
    def get_configuration_for_pipeline(cls, config, pipeline_metadata):
        """Takes in config dictionary and pipeline_metadata, returns populated config_pipeline dictionary

        Args:
            config (dict): A dictionary containing configuration parameters.
            pipeline_metadata (dict): A dictionary containing metadata for the pipeline.

        Returns:
            dict: A dictionary containing the populated config_pipeline.

        """
        data_product_id = config["data_product_id"]
        environment = config["environment"]

        tracer, logger = LoggerSingleton.instance(
            NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
        ).initialize_logging_and_tracing()

        with tracer.start_as_current_span("get_configuration_for_pipeline"):
            try:
                arg_list = {}

                yyyy_param = config["yyyy"]
                mm_param = config["mm"]
                dd_param = config["dd"]
                if (
                    len(dd_param.strip()) == 0
                    or dd_param.strip() == "N/A"
                    or dd_param.strip() == "NA"
                ):
                    transmission_period = mm_param + "_" + yyyy_param
                    dd_param = "NA"
                else:
                    transmission_period = yyyy_param + "_" + mm_param + "_" + dd_param

                environment = config["environment"]
                override_save_flag = config["override_save_flag"]

                row = pipeline_metadata

                execute_flag = row["execute_flag"]
                pipeline_parameters = row["pipeline_parameters"]
                export_schema_metrics = row["export_schema_metrics"]
                view_name = row["view_name"]
                pipeline_type = row["pipeline_type"]
                pipeline_name = row["pipeline_name"]
                query_name = row["pipeline_name"]
                if view_name is not None:
                    view_name = str(view_name).strip()
                    if len(view_name) > 0:
                        # some queries have multiple params, save for each
                        pipeline_name = view_name

                if pipeline_name is view_name:
                    logger.info(f"saving pipeline with view name: {view_name}")
                else:
                    if pipeline_name is None or pipeline_name == "":
                        logger.info("pipeline_name is blank")
                    else:
                        logger.info(
                            f"saving pipeline with pipeline_name:{pipeline_name}"
                        )

                row_id_keys = row["row_id_keys"]

                # execute
                arg_dictionary = dict()

                if pipeline_parameters is None:
                    logger.info("pipeline_parameters are empty")
                    pipeline_parameters = ""
                else:
                    pipeline_parameters = pipeline_parameters.strip()

                config_pipeline = {"pipeline_parameters": pipeline_parameters}

                if pipeline_parameters != "":
                    logger.info("pipeline_parameters are " + pipeline_parameters)
                    arg_list = [x.strip() for x in pipeline_parameters.split("|")]
                    for line in arg_list:
                        pair = [x.strip() for x in line.split(":")]
                        if len(pair) > 1:
                            arg_dictionary[pair[0]] = pair[1]
                        else:
                            arg_dictionary[pair[0]] = ""
                else:
                    logger.info("pipeline_parameters are blank")

                arg_dictionary["environment"] = environment
                arg_dictionary["yyyy"] = yyyy_param
                arg_dictionary["mm"] = mm_param
                arg_dictionary["dd"] = dd_param
                arg_dictionary["transmission_period"] = transmission_period

                # save the pipeline name as view name
                # this allows for the same pipeline to be saved multiple times with different paramters

                if override_save_flag == "override_with_save":
                    save_flag = "save"
                elif override_save_flag == "override_with_skip_save":
                    save_flag = "skip_save"
                else:
                    save_flag = "default"

                if save_flag == "default":
                    if row["save_flag"] is not None:
                        if len(row["save_flag"]) > 0:
                            save_flag = row["save_flag"]
                    else:
                        save_flag = "save"

                execute_results_flag = row["execute_results_flag"]
                if execute_results_flag is None:
                    execute_results_flag = "skip_execute"
                if execute_results_flag.strip() == "":
                    execute_results_flag = "skip_execute"

                config_pipeline["pipeline_type"] = pipeline_type
                config_pipeline["transmission_period"] = transmission_period
                config_pipeline["pipeline_name"] = pipeline_name
                config_pipeline["query_name"] = query_name
                config_pipeline["view_name"] = view_name
                config_pipeline["save_flag"] = save_flag
                config_pipeline["execute_flag"] = execute_flag
                config_pipeline["arg_dictionary"] = arg_dictionary
                config_pipeline["export_schema_metrics"] = export_schema_metrics
                config_pipeline["row_id_keys"] = row_id_keys
                config_pipeline["execute_results_flag"] = execute_results_flag

                return config_pipeline

            except Exception as ex:
                error_msg = "Error: %s", ex
                exc_info = sys.exc_info()
                LoggerSingleton.instance(
                    NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
                ).error_with_exception(error_msg, exc_info)
                raise

    @staticmethod
    def contains_workspace(repository_path):
        """
        Check if the given repository path contains the '/Workspace' directory.

        Args:
            repository_path (str): The path of the repository.

        Returns:
            bool: True if the repository path contains '/Workspace', False otherwise.
        """
        return "/Workspace" in repository_path

    @classmethod
    def get_execute_pipeline_parameters(cls, config, config_pipeline):
        """Takes in config dictionary and config_pipeline, and returns the result of executed pipelines.

        Args:
            config (dict): A dictionary containing configuration parameters.
            config_pipeline (dict): A dictionary containing pipeline-specific configuration parameters.

        Returns:
            dict: A dictionary containing the updated config_pipeline with additional parameters.

        """

        environment = config["environment"]
        data_product_id = config["data_product_id"]

        tracer, logger = LoggerSingleton.instance(
            NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
        ).initialize_logging_and_tracing()

        with tracer.start_as_current_span("get_execute_pipeline_parameters"):
            try:
                repository_path = config["repository_path"]

                data_product_id_root = config["data_product_id_root"]
                pipeline_name = config_pipeline["pipeline_name"]
                arg_dictionary = config_pipeline["arg_dictionary"]

                if cls.contains_workspace(repository_path):
                    repository_path = repository_path.rstrip("/")
                    base_path = os.path.join(
                        repository_path, data_product_id_root, data_product_id
                    )
                    base_path = base_path.replace("/Workspace", "")
                else:
                    cdh_databricks_repository_path = config[
                        "cdh_databricks_repository_path"
                    ]
                    base_path = cdh_databricks_repository_path.rstrip("/")

                # Create a Path object
                path = Path(base_path)

                # Remove the 'config/' part
                # Here we assume 'config' is always a direct folder and not nested
                new_parts = [part for part in path.parts if part != "config"]

                # Create a new Path object from the remaining parts
                new_path = Path(*new_parts)

                # Convert back to string if needed
                base_path = str(new_path)

                dir_name_python = "/".join([base_path, "autogenerated", "python"])
                pipeline_name = pipeline_name.replace(data_product_id, "").replace(
                    ".", ""
                )
                pipeline_name = data_product_id + "_" + pipeline_name
                path_to_execute = os.path.join(dir_name_python, pipeline_name)

                database_prefix = config["cdh_database_name"]

                arg_dictionary["database_prefix"] = database_prefix

                config_pipeline["arg_dictionary"] = arg_dictionary
                config_pipeline["path_to_execute"] = path_to_execute
                logger.info(f"config_pipeline:{str(config_pipeline)}")
                return config_pipeline

            except Exception as ex:
                error_msg = "Error: %s", ex
                exc_info = sys.exc_info()
                LoggerSingleton.instance(
                    NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
                ).error_with_exception(error_msg, exc_info)
                raise

    @classmethod
    def get_view_dataframe(cls, config, spark, config_pipeline):
        """Takes in config dictionary, spark and config pipeline
        and returns dataframe with columns sorted

        Args:
            config (dict): A dictionary containing configuration parameters.
            spark (pyspark.sql.SparkSession): The Spark session object.
            config_pipeline (dict): A dictionary containing pipeline configuration.

        Returns:
            pyspark.sql.DataFrame: A dataframe with columns sorted.
        """

        data_product_id = config["data_product_id"]
        environment = config["environment"]

        tracer, logger = LoggerSingleton.instance(
            NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
        ).initialize_logging_and_tracing()

        with tracer.start_as_current_span("get_view_dataframe"):
            try:
                cdh_database_name = config["cdh_database_name"]
                view_name = config_pipeline["view_name"]

                full_view_name = f"{cdh_database_name}.{view_name}"
                sql_statement = f"SELECT * FROM {full_view_name}"
                logger.info(f"sql_statement:{sql_statement}")
                unsorted_df = spark.sql(sql_statement)
                sorted_df = unsorted_df.select(sorted(unsorted_df.columns))
                sorted_df.createOrReplaceTempView("table_sorted_df")

                config_pipeline["full_view_name"] = full_view_name

                return sorted_df

            except Exception as ex:
                error_msg = "Error: %s", ex
                exc_info = sys.exc_info()
                LoggerSingleton.instance(
                    NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
                ).error_with_exception(error_msg, exc_info)
                raise

    @classmethod
    def execute_pipeline(cls, config, config_pipeline, pipeline_type, dbutils=None):
        """
        Executes a pipeline based on the provided configuration.

        Args:
            config (dict): The overall configuration for the pipeline.
            config_pipeline (dict): The specific configuration for the pipeline to be executed.

        Returns:
            None
        """

        data_product_id = config.get("data_product_id")
        environment = config.get("environment")

        tracer, logger = LoggerSingleton.instance(
            NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
        ).initialize_logging_and_tracing()

        with tracer.start_as_current_span("execute_pipeline"):
            try:
                running_local = config["running_local"]
                pipeline_type = config_pipeline["pipeline_type"]
                client_secret = config["client_secret"]
                if pipeline_type is None:
                    pipeline_type = "databricks_sql"
                pipeline_name = config_pipeline["pipeline_name"]
                execute_flag = config_pipeline["execute_flag"]
                logger.info(f"execute_flag: {execute_flag}")
                if execute_flag is None:
                    execute_flag = "skip_execute"
                elif execute_flag == "skip_execute":
                    logger.info(f"skip execute requested: {pipeline_name}")
                else:
                    execute_flag = "execute"
                    if pipeline_type == "databricks_sql":
                        logger.info(f"execute_flag requested: {pipeline_name}")
                        config_pipeline = cls.get_execute_pipeline_parameters(
                            config, config_pipeline
                        )
                        path_to_execute = config_pipeline["path_to_execute"]
                        arg_dictionary = config_pipeline["arg_dictionary"]
                        # time out in 15 minutes: 900 sec or 600 10 min
                        if running_local is True:
                            logger.info(f"running_local true:{running_local}")

                            # Initialize running_interactive as False
                            running_interactive = False

                            # Check if the client_secret is None or a zero-length string
                            if not client_secret or len(client_secret) == 0:
                                running_interactive = True
                                logger.info(
                                    f"running_local:{running_local} and running_interactive:{running_interactive}"
                                )
                        else:
                            logger.info(f"running_local false:{running_local}")
                            # Trim leading and trailing whitespace from client_secret

                            running_interactive = False

                        databricks_instance_id = config["databricks_instance_id"]
                        az_sub_tenant_id = config.get("az_sub_tenant_id")
                        az_sub_client_id = config.get("az_sub_client_id")
                        az_kv_key_vault_name = config.get("az_kv_key_vault_name")
                        az_sub_client_secret_key = config.get(
                            "az_sub_client_secret_key"
                        )
                        az_sub_client_secret_key = az_sub_client_secret_key.replace(
                            "-", "_"
                        )
                        client_secret = config.get("client_secret")
                        logger.info(
                            f"az_sub_client_secret_key:{az_sub_client_secret_key}"
                        )
                        logger.info(f"az_sub_client_id:{az_sub_client_id}")

                        if running_local is True:
                            if client_secret is None or client_secret == "":
                                running_interactive = True
                            else:
                                running_interactive = False
                        else:
                            running_interactive = False

                        obj_key_vault = az_key_vault.AzKeyVault(
                            az_sub_tenant_id,
                            az_sub_client_id,
                            client_secret,
                            az_kv_key_vault_name,
                            running_interactive,
                            data_product_id,
                            environment,
                        )

                        cdh_databricks_pat_secret_key = config[
                            "cdh_databricks_pat_secret_key"
                        ]

                        cdh_databricks_kv_scope = config.get("cdh_databricks_kv_scope")
                        dbx_pat_token = obj_key_vault.get_secret(
                            cdh_databricks_pat_secret_key,
                            cdh_databricks_kv_scope,
                            dbutils,
                        )

                        cdh_databricks_cluster = config.get("cdh_databricks_cluster")

                        obj_notebook = dbx_notebook.Notebook()
                        obj_notebook.run_notebook(
                            dbx_pat_token,
                            databricks_instance_id,
                            cdh_databricks_cluster,
                            path_to_execute,
                            arg_dictionary,
                            data_product_id,
                            environment,
                        )

                    else:
                        logger.info("run remote")
                        if "dbutils" in locals():
                            dbutils.notebook.run(path_to_execute, 900, arg_dictionary)
                        else:
                            dbutils = None
                return f"Success: {pipeline_name} executed"
            except Exception as ex:
                error_msg = "Error: %s", ex
                exc_info = sys.exc_info()
                LoggerSingleton.instance(
                    NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
                ).error_with_exception(error_msg, exc_info)
                raise

    @classmethod
    def fetch_and_save_pipeline(cls, config, config_pipeline, dbutils):
        """Takes in config dictionary, config_pipeline dictionary, token, repository_path
        and saves sql

        Args:
            config (dict): A dictionary containing configuration parameters.
            config_pipeline (dict): A dictionary containing pipeline configuration parameters.

        Returns:
            None
        """

        data_product_id = config["data_product_id"]
        environment = config["environment"]

        tracer, logger = LoggerSingleton.instance(
            NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
        ).initialize_logging_and_tracing()

        with tracer.start_as_current_span("fetch_and_save_pipeline"):
            try:
                # environment vars
                running_local = config["running_local"]
                yyyy_param = config["yyyy"]
                mm_param = config["mm"]
                dd_param = config["dd"]
                environment = config["environment"]
                databricks_instance_id = config["databricks_instance_id"]
                data_product_id = config["data_product_id"]
                data_product_id_root = config["data_product_id_root"]
                repository_path = config["repository_path"]
                tenant_id = config.get("az_sub_tenant_id")
                client_id = config.get("az_sub_client_id")
                vault_url = config.get("az_kv_key_vault_name")
                az_sub_client_secret_key = config.get("az_sub_client_secret_key")

                # pipeline vars
                query_name = config_pipeline["query_name"]
                pipeline_name = config_pipeline["pipeline_name"]
                execute_results_flag = config_pipeline["execute_results_flag"]
                arg_dictionary = config_pipeline["arg_dictionary"]
                transmission_period = config_pipeline["transmission_period"]
                logger.info(f"query_name: {query_name}")
                logger.info(f"pipeline_name: {pipeline_name}")
                logger.info(f"execute_results_flag: {execute_results_flag}")
                logger.info(f"arg_dictionary: {arg_dictionary}")
                logger.info(f"transmission_period: {transmission_period}")

                obj_sql = databricks_sql.DatabricksSQL()

                cdh_databricks_pat_secret_key = config.get(
                    "cdh_databricks_pat_secret_key"
                )

                client_secret = config.get("access_token")
                if client_secret is None or client_secret == "":
                    obj_core = az_environment_core.EnvironmentCore()
                    logger.info(
                        f"getting environment variable: {az_sub_client_secret_key}"
                    )
                    client_secret = obj_core.get_environment_variable(
                        az_sub_client_secret_key
                    )

                obj_az_keyvault = az_key_vault.AzKeyVault(
                    tenant_id,
                    client_id,
                    client_secret,
                    vault_url,
                    False,
                    data_product_id,
                    environment,
                )

                cdh_databricks_kv_scope = config.get("cdh_databricks_kv_scope")

                databricks_access_token = obj_az_keyvault.get_secret(
                    cdh_databricks_pat_secret_key, cdh_databricks_kv_scope, dbutils
                )
                if databricks_access_token is None:
                    databricks_access_token = ""
                    databricks_access_token_length = 0
                else:
                    databricks_access_token_length = len(databricks_access_token)
                logger.info(
                    f"databricks_access_token_length: {databricks_access_token_length}"
                )

                # configure to download and save sql only in dev
                # In future, add support for notebook pipelines in addition to sql pipelines
                if environment == "dev":
                    # Always download and save in dev
                    save_flag = "save"
                    logger.info(f"save_flag: {save_flag}")

                    obj_sql = databricks_sql.DatabricksSQL()
                    cdh_databricks_repository_path = config.get(
                        "cdh_databricks_repository_path"
                    )
                    response_text = obj_sql.fetch_and_save_pipeline(
                        databricks_access_token,
                        repository_path,
                        environment,
                        databricks_instance_id,
                        data_product_id_root,
                        data_product_id,
                        query_name,
                        pipeline_name,
                        execute_results_flag,
                        arg_dictionary,
                        running_local,
                        yyyy_param,
                        mm_param,
                        dd_param,
                        transmission_period,
                        cdh_databricks_repository_path,
                    )
                else:
                    # in non-dev environments, only download and save if requested
                    save_flag = config_pipeline["save_flag"]
                    if save_flag.lower == "save":
                        logger.warning(f"save_flag: {save_flag}")
                        logger.warning(
                            "save_flag not supported in non-dev environments - using override"
                        )
                        obj_sql = databricks_sql.DatabricksSQL()
                        cdh_databricks_repository_path = config.get(
                            "cdh_databricks_repository_path"
                        )
                        response_text = obj_sql.fetch_and_save_pipeline(
                            databricks_access_token,
                            repository_path,
                            environment,
                            databricks_instance_id,
                            data_product_id_root,
                            data_product_id,
                            query_name,
                            pipeline_name,
                            execute_results_flag,
                            arg_dictionary,
                            running_local,
                            yyyy_param,
                            mm_param,
                            dd_param,
                            transmission_period,
                            cdh_databricks_repository_path,
                        )
                    else:
                        response_text = "skip_save"

                return response_text

            except Exception as ex:
                error_msg = "Error: %s", ex
                exc_info = sys.exc_info()
                LoggerSingleton.instance(
                    NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
                ).error_with_exception(error_msg, exc_info)
                raise
