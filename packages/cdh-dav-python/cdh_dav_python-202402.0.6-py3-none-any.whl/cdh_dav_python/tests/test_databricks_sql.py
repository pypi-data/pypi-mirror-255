import os
import sys
import unittest
from unittest.mock import patch
import cdh_dav_python.databricks_service.sql as databricks_sql
import cdh_dav_python.az_key_vault_service.az_key_vault as az_key_vault
import cdh_dav_python.cdc_tech_environment_service.environment_core as az_environment_core


from cdh_dav_python.cdc_admin_service.environment_logging import LoggerSingleton

# Get the currently running file name
NAMESPACE_NAME = os.path.basename(os.path.dirname(__file__))
# Get the parent folder name of the running file
SERVICE_NAME = os.path.basename(__file__)

OS_NAME = os.name
sys.path.append("..")


class TestDatabricksSQL(unittest.TestCase):
    """
    Unit tests for the save_pipeline_sql function.
    """

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

        az_sub_client_secret_key = config.get("az_sub_client_secret_key")
        obj_core = az_environment_core.EnvironmentCore()
        print(f"getting environment variable: {az_sub_client_secret_key}")
        client_secret = obj_core.get_environment_variable(az_sub_client_secret_key)
        tenant_id = config.get("az_sub_tenant_id")
        client_id = config.get("az_sub_client_id")
        vault_url = config.get("az_kv_key_vault_name")
        data_product_id = config.get("data_product_id")
        environment = config.get("environment")
        running_interactive = True

        obj_key_vault = az_key_vault.AzKeyVault(
            tenant_id,
            client_id,
            client_secret,
            vault_url,
            running_interactive,
            data_product_id,
            environment,
        )

        return config, obj_key_vault

    def test_cdh_premier_cpr_reload_metrics_step_1_pipeline(self):
        environment = "prod"
        data_product_id = "cdh_premier"

        config, obj_az_keyvault = self.setup_config(data_product_id, environment)

        cdh_databricks_kv_scope = config.get("cdh_databricks_kv_scope")

        cdh_databricks_pat_secret_key = config.get("cdh_databricks_pat_secret_key")
        databricks_access_token = obj_az_keyvault.get_secret(
            cdh_databricks_pat_secret_key, cdh_databricks_kv_scope
        )

        if databricks_access_token is None:
            databricks_access_token = ""
            databricks_access_token_length = 0
        else:
            databricks_access_token_length = len(databricks_access_token)
        print(f"databricks_access_token_length: {databricks_access_token_length}")
        assert databricks_access_token_length > 0

        repository_path = config.get("repository_path")
        yyyy_param = config.get("repository_path")
        mm_param = config.get("mm_param")
        dd_param = config.get("dd_param")
        environment = config.get("environment")
        databricks_instance_id = config.get("databricks_instance_id")
        data_product_id_root = config.get("data_product_id_root")
        data_product_id = config.get("data_product_id")
        query_name = "rpt_in_resp"
        pipeline_name = "cdh_premier.cpr_reload_metrics_step_1"
        execute_results_flag = (True,)
        arg_dictionary_string = "source_database:cdh_premier_v2|target_database:cdh_premier_exploratory|specific_user_or_role:gp-u-EDAV-CDH-PREMIER-ANALYSTS-AAD|admin_user_or_role:gp-u-EDAV-CDH-ADMIN-AAD"
        cdh_databricks_repository_path = config.get("cdh_databricks_repository_path")

        # Splitting the string into key-value pairs
        pairs = arg_dictionary_string.split("|")

        # Splitting each pair into keys and values and creating a dictionary
        arg_dictionary = dict(pair.split(":") for pair in pairs)

        transmission_period = "daily"
        running_local = config.get("running_local")

        # Call the save_pipeline_sql function with sample parameters
        obj_sql = databricks_sql.DatabricksSQL()

        result = obj_sql.fetch_and_save_pipeline(
            databricks_access_token=databricks_access_token,
            repository_path=repository_path,
            environment=environment,
            databricks_instance_id=databricks_instance_id,
            data_product_id_root=data_product_id_root,
            data_product_id=data_product_id,
            query_name=query_name,
            pipeline_name=pipeline_name,
            execute_results_flag=execute_results_flag,
            arg_dictionary=arg_dictionary,
            running_local=running_local,
            yyyy_param=yyyy_param,
            mm_param=mm_param,
            dd_param=dd_param,
            transmission_period=transmission_period,
            cdh_databricks_repository_path=cdh_databricks_repository_path,
        )

        # Assert that the response is successful
        self.assertEqual(result, "success")

    def test_wonder_metadata_pipeline_gold_davt_rpt_scan_field_vw(self):
        """
        Fetches and processes a pipeline successfully.

        This method retrieves the necessary configuration values, such as the Databricks access token,
        repository path, environment, etc. It then calls the `fetch_and_save_pipeline` method of the
        `DatabricksSQL` class with the provided parameters. Finally, it asserts that the response is "success".

        Returns:
            None
        """
        environment = "dev"
        data_product_id = "wonder_metadata"

        config, obj_az_keyvault = self.setup_config(data_product_id, environment)
        (config,) = self.setup_config(data_product_id, environment)

        cdh_databricks_pat_secret_key = config.get("cdh_databricks_pat_secret_key")
        cdh_databricks_kv_scope = config.get("cdh_databricks_kv_scope")

        databricks_access_token = obj_az_keyvault.get_secret(
            cdh_databricks_pat_secret_key, cdh_databricks_kv_scope
        )

        if databricks_access_token is None:
            databricks_access_token = ""
            databricks_access_token_length = 0
        else:
            databricks_access_token_length = len(databricks_access_token)
        print(f"databricks_access_token_length: {databricks_access_token_length}")
        assert databricks_access_token_length > 0

        repository_path = config.get("repository_path")
        yyyy_param = config.get("repository_path")
        mm_param = config.get("mm_param")
        dd_param = config.get("dd_param")
        environment = config.get("environment")
        databricks_instance_id = config.get("databricks_instance_id")
        data_product_id_root = config.get("data_product_id_root")
        data_product_id = config.get("data_product_id")
        query_name = "gold_davt_rpt_scan_field_vw"
        pipeline_name = "gold_davt_rpt_scan_field_vw"
        execute_results_flag = (True,)
        arg_dictionary = ({},)
        transmission_period = "daily"
        running_local = config.get("running_local")

        # Call the save_pipeline_sql function with sample parameters
        obj_sql = databricks_sql.DatabricksSQL()
        cdh_databricks_repository_path = config.get("cdh_databricks_repository_path")
        result = obj_sql.fetch_and_save_pipeline(
            databricks_access_token=databricks_access_token,
            repository_path=repository_path,
            environment=environment,
            databricks_instance_id=databricks_instance_id,
            data_product_id_root=data_product_id_root,
            data_product_id=data_product_id,
            query_name=query_name,
            pipeline_name=pipeline_name,
            execute_results_flag=execute_results_flag,
            arg_dictionary=arg_dictionary,
            running_local=running_local,
            yyyy_param=yyyy_param,
            mm_param=mm_param,
            dd_param=dd_param,
            transmission_period=transmission_period,
            cdh_databricks_repository_path=cdh_databricks_repository_path,
        )

        # Assert that the response is successful
        self.assertEqual(result, "success")


if __name__ == "__main__":
    unittest.main()
