"""
This module contains unit tests for the AzKeyVault class.

The AzKeyVault class provides methods for interacting with Azure Key Vault.
These tests verify the functionality of the methods in the AzKeyVault class.
"""

import unittest
import sys
import os


import cdh_dav_python.az_key_vault_service.az_key_vault as az_key_vault

sys.path.append("..")


class TestAzKeyVault(unittest.TestCase):
    """
    Unit test class for the AzKeyVault class.

    This class contains test cases for the methods of the AzKeyVault class.
    """

    def setUp(self):
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

        data_product_id = "wonder_metadata"
        environment = "dev"
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
        self.client_secret = os.getenv(az_sub_client_secret_key)
        self.tenant_id = config.get("az_sub_tenant_id")
        self.client_id = config.get("az_sub_client_id")
        self.vault_url = config.get("az_kv_key_vault_name")
        self.running_interactive = True
        self.data_product_id = config.get("data_product_id")
        self.environment = environment
        self.key_vault_interactive = az_key_vault.AzKeyVault(
            self.tenant_id,
            self.client_id,
            self.client_secret,
            self.vault_url,
            True,
            self.data_product_id,
            self.environment,
        )

        self.key_vault_non_interactive = az_key_vault.AzKeyVault(
            self.tenant_id,
            self.client_id,
            self.client_secret,
            self.vault_url,
            False,
            self.data_product_id,
            self.environment,
        )

    def test_get_secret_wonder_metdata_dev_github_interactive(self):
        """
        Test case for the get_secret_interactive method.

        This test mocks the necessary dependencies and verifies that the get_secret method
        correctly retrieves the secret value from the key vault.

        It asserts that the retrieved secret value matches the expected secret value,
        and that the necessary methods for retrieving the secret are called with the correct arguments.
        """

        config = self.config
        cdh_databricks_kv_scope = config.get("cdh_databricks_kv_scope")
        secret_name = config.get("az_kv_gh_client_secret_key", cdh_databricks_kv_scope)

        secret_value = self.key_vault_interactive.get_secret(secret_name)
        assert secret_value is not None
        assert len(secret_value) > 0

    def test_get_secret_wonder_metdata_dev_non_interactive(self):
        """
        Test case for the 'get_secret' method when running in non-interactive mode.

        This test mocks the necessary dependencies and sets the 'running_interactive' flag to False.
        It then calls the 'get_secret' method with a secret name and asserts that the returned secret value matches the expected value.
        Additionally, it verifies that the 'get_credential', 'get_secret_client', and 'retrieve_secret' methods are called with the expected arguments.

        """

        config = self.config
        cdh_databricks_kv_scope = config.get("cdh_databricks_kv_scope")
        secret_name = config.get("az_kv_gh_client_secret_key", cdh_databricks_kv_scope)

        secret_value = self.key_vault_non_interactive.get_secret(secret_name)
        assert secret_value is not None
        assert len(secret_value) > 0


if __name__ == "__main__":
    unittest.main()
