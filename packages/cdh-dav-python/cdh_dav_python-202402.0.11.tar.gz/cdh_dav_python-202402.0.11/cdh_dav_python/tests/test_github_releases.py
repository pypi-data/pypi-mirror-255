from dotenv import load_dotenv, find_dotenv, set_key
from cdh_dav_python.cdc_metadata_service.environment_metadata import (
    EnvironmentMetaData,
)
from cdh_dav_python.github_service.github_release import GitHubRelease
import cdh_dav_python.az_key_vault_service.az_key_vault as az_key_vault
from pathlib import Path
import os
import sys
import unittest


from requests.exceptions import RequestException

sys.path.append("..")


class TestGitHubRelease(unittest.TestCase):
    """
    A test case for the GitHubRelease class.
    """

    def setUp(self):
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

        data_product_id = "wonder_metadata"
        environment = "dev"

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
        self.client_secret = os.getenv(az_sub_client_secret_key)
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

    def test_get_releases(self):
        """
        Test the get_releases function.
        """

        config = self.config

        gh_owner_name = config.get("gh_owner_name")
        gh_repository_name = config.get("gh_repository_name")

        az_kv_gh_client_secret_key = config.get("az_kv_gh_client_secret_key")

        obj_az_keyvault = self.key_vault
        cdh_databricks_kv_scope = config.get("cdh_databricks_kv_scope")
        gh_access_token = obj_az_keyvault.get_secret(
            az_kv_gh_client_secret_key, cdh_databricks_kv_scope
        )
        if gh_access_token is None:
            gh_access_token = ""
            gh_access_token_length = 0
        else:
            gh_access_token_length = len(gh_access_token)
        print(f"gh_access_token_length: {gh_access_token_length}")
        assert gh_access_token_length > 0

        print(f"gh_owner_name: {gh_owner_name}")
        print(f"gh_repository_name: {gh_repository_name}")

        environment = config["environment"]
        data_product_id = config["data_product_id"]

        (
            status_code,
            response_content,
            api_url,
        ) = GitHubRelease.get_releases(
            gh_access_token,
            gh_owner_name,
            gh_repository_name,
            data_product_id,
            environment,
        )

        print(f"response_content: {response_content}")

        # check count is greater than 0
        assert len(response_content) > 0
        assert response_content is not None
        assert status_code == 200
        assert len(str(response_content)) > 0
