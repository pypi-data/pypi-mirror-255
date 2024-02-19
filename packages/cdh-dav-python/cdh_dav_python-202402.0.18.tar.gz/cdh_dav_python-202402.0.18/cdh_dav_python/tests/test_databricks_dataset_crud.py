import os
import sys
import unittest
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


class TestDatabricksDatasetCrud(unittest.TestCase):
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

        self.key_vault = az_key_vault.AzKeyVault(
            self.tenant_id,
            self.client_id,
            self.client_secret,
            self.vault_url,
            self.running_interactive,
            self.data_product_id,
            self.environment,
        )

        return config

    def test_upsert(self):
        assert True


if __name__ == "__main__":
    unittest.main()
