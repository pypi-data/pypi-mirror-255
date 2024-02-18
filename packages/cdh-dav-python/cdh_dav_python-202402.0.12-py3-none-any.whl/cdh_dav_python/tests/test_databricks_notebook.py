import os
import sys
import unittest
from pathlib import Path
import cdh_dav_python.az_key_vault_service.az_key_vault as az_key_vault
import cdh_dav_python.cdc_tech_environment_service.environment_core as az_environment_core

from cdh_dav_python.databricks_service.notebook import Notebook
from cdh_dav_python.cdc_admin_service.environment_logging import LoggerSingleton

# Get the currently running file name
NAMESPACE_NAME = os.path.basename(os.path.dirname(__file__))
# Get the parent folder name of the running file
SERVICE_NAME = os.path.basename(__file__)

OS_NAME = os.name
sys.path.append("..")


class TestDatabricksNotebook(unittest.TestCase):
    def setup_config(self, data_product_id, environment):
        """
        Set up the test environment before running each test case.
        """

        dbutils_exists = "dbutils" in locals() or "dbutils" in globals()
        if dbutils_exists is False:
            dbutils = None

        spark_exists = "spark" in locals() or "spark" in globals()
        if spark_exists is False:
            spark = None

        running_local = dbutils is None
        print(f"running_local: {running_local}")

        initial_script_dir = (
            os.path.dirname(os.path.abspath(__file__))
            if "__file__" in globals()
            else os.getcwd()
        )
        print(f"initial_script_dir: {initial_script_dir}")

        parent_dir = os.path.abspath(os.path.join(initial_script_dir, "..", ".."))
        print(f"parent_dir: {parent_dir}")
        if parent_dir not in sys.path:
            sys.path.append(parent_dir)

        repository_path_default = str(parent_dir)

        print(f"repository_path_default: {repository_path_default}")

        import run_install_cdh_dav_python

        (
            spark,
            obj_environment_metadata,
            obj_job_core,
            config,
        ) = run_install_cdh_dav_python.setup_core(
            running_local,
            initial_script_dir,
            dbutils,
            spark,
            data_product_id,
            environment,
        )

        self.config = config

        az_sub_client_secret_key = config.get("az_sub_client_secret_key")
        obj_core = az_environment_core.EnvironmentCore()
        print(f"getting environment variable: {az_sub_client_secret_key}")
        self.client_secret = obj_core.get_environment_variable(az_sub_client_secret_key)
        self.tenant_id = config.get("az_sub_tenant_id")
        self.client_id = config.get("az_sub_client_id")
        self.vault_url = config.get("az_kv_key_vault_name")
        self.data_product_id = config.get("data_product_id")
        self.environment = config.get("environment")
        self.running_interactive = True

        obj_az_keyvault = az_key_vault.AzKeyVault(
            self.tenant_id,
            self.client_id,
            self.client_secret,
            self.vault_url,
            self.running_interactive,
            self.data_product_id,
            self.environment,
        )

        cdh_databricks_pat_secret_key = config.get("cdh_databricks_pat_secret_key")
        cdh_databricks_kv_scope = config.get("cdh_databricks_kv_scope")
        databricks_access_token = obj_az_keyvault.get_secret(
            cdh_databricks_pat_secret_key, cdh_databricks_kv_scope
        )

        if databricks_access_token is None or databricks_access_token == "":
            databricks_access_token = ""
            databricks_access_token_length = 0
            raise ValueError("databricks_access_token is empty")
        else:
            databricks_access_token_length = len(databricks_access_token)

        config["cdh_databricks_token"] = databricks_access_token

        return config

    def test_run_jobs_cdh_premier_notebook(self):
        """
        Test case for the run_notebook function.

        This function tests the functionality of the run_notebook function by calling it with mock variables
        and asserting that the response is equal to {"result": "success"}.

        Parameters:
        None

        Returns:
        None
        """

        data_product_id = "cdh_premier"
        environment = "prod"

        tracer, logger = LoggerSingleton.instance(
            NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
        ).initialize_logging_and_tracing()

        logger.info(f"tracer: {tracer}")

        with tracer.start_as_current_span("setup_core"):
            try:
                repository_path_default = str(Path(os.getcwd()))

                parameters = {
                    "data_product_id": data_product_id,
                    "data_product_id_root": "cdh",
                    "data_product_id_individual": "premier",
                    "environment": environment,
                    "running_local": True,
                    "repository_path": repository_path_default,
                }

                config = self.setup_config(data_product_id, environment)

                # Mock variables
                token = config["cdh_databricks_token"]
                databricks_instance_id = config["cdh_databricks_instance_id"]
                logger.info(f"databricks_instance_id: {databricks_instance_id}")
                cluster_id = config["cdh_databricks_cluster"]
                logger.info(f"cluster_id: {cluster_id}")
                notebook_path = "/Workspace/Repos/zfi4@cdc.gov/cdh-dav/cdh_dav_lib/cdh/cdh_premier/_run_jobs_cdh_premier.py"
                logger.info(f"notebook_path: {notebook_path}")
                parameters = {}
                logger.info(f"parameters: {parameters}")
                # Call the function under test
                obj_notebook = Notebook()
                response = obj_notebook.run_notebook(
                    token,
                    databricks_instance_id,
                    cluster_id,
                    notebook_path,
                    parameters,
                    data_product_id,
                    environment,
                )

                # Assert the response
                assert response == {"result": "success"}

            except Exception as ex:
                error_msg = "Error: %s", ex
                exc_info = sys.exc_info()
                LoggerSingleton.instance(
                    NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
                ).error_with_exception(error_msg, exc_info)
                raise
