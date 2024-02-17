import os
import sys
import unittest
from cdh_dav_python.databricks_service.dataset_core import DataSetCore
import cdh_dav_python.az_key_vault_service.az_key_vault as az_key_vault
import cdh_dav_python.cdc_tech_environment_service.environment_core as az_environment_core


# Get the currently running file name
NAMESPACE_NAME = os.path.basename(os.path.dirname(__file__))
# Get the parent folder name of the running file
SERVICE_NAME = os.path.basename(__file__)

OS_NAME = os.name
sys.path.append("..")


class TestDatabricksDatasetCore(unittest.TestCase):
    """
    A test case class for testing the functionality of DatabricksDatasetCore.
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

        return config, spark

    def test_table_exists_wonder_metadata_dev_success(self):
        """
        Test case to check if a table exists in the specified dataset and database.
        This test is specifically for the 'wonder_metadata' data product in the 'dev' environment.

        Returns:
            None
        """
        data_product_id = "wonder_metadata"
        environment = "dev"
        config, spark = self.setup_config(data_product_id, environment)

        obj_dataset_core = DataSetCore()
        dataset_name = "bronze_config_datasets"
        schema_name = "hive_metastore.wonder_metadata_etl"
        table_exists = obj_dataset_core.table_exists(
            spark, dataset_name, schema_name, data_product_id, environment
        )
        print(f"table_exists: {table_exists}")
        self.assertEqual(table_exists, True)

    def test_table_exists_wonder_metadata_dev_error(self):
        """
        Test case to check if a table exists in the specified dataset and database.
        This test is specifically for the 'wonder_metadata' data product in the 'dev' environment.

        Returns:
            None
        """
        data_product_id = "wonder_metadata"
        environment = "dev"
        config, spark = self.setup_config(data_product_id, environment)

        obj_dataset_core = DataSetCore()
        dataset_name = "test_table"
        schema_name = "hive_metastore.wonder_metadata_etl"
        table_exists = obj_dataset_core.table_exists(
            spark, dataset_name, schema_name, data_product_id, environment
        )
        print(f"table_exists: {table_exists}")
        self.assertEqual(table_exists, False)


if __name__ == "__main__":
    unittest.main()
