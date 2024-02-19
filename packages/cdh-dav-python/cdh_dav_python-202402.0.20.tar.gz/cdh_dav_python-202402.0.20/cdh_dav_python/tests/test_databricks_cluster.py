"""
This module contains unit tests for the Cluster class in the 'cdh_dav_python.databricks_service.cluster' package. It includes tests for various scenarios such as successful installation of cluster libraries, handling already installed libraries, and failure to install libraries. The tests use mock objects and patching to simulate different responses and states of the Databricks cluster environment.

The TestCluster class extends unittest.TestCase and contains methods to set up the test environment and test different functionalities of the Cluster class. It tests the install_cluster_library method under different conditions such as when the library is already installed, successfully installed, or fails to install.

Environment variables and configurations are set up in the setUp method to simulate the Databricks environment. Mock objects are used to replace actual calls to Databricks APIs, and assertions are made to verify the expected outcomes of these operations.

These tests ensure the robustness and reliability of the Cluster class in handling library installations on Databricks clusters.

"""

import unittest
from unittest.mock import patch
import cdh_dav_python.databricks_service.cluster as dbx_cluster
import os
import sys


class TestCluster(unittest.TestCase):
    """
    A test case for the Cluster class.
    """

    def setUp(self):
        ENVIRONMENT = "dev"

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
        self.client_secret = os.getenv(az_sub_client_secret_key)
        self.tenant_id = config.get("az_sub_tenant_id")
        self.client_id = config.get("az_sub_client_id")
        self.vault_url = config.get("az_kv_key_vault_name")
        self.running_interactive = True

    @patch(
        "cdh_dav_python.databricks_service.cluster.Cluster.get_cluster_library_status"
    )
    @patch(
        "cdh_dav_python.databricks_service.cluster.Cluster.call_databricks_install_api"
    )
    def test_install_cluster_library_success(self, mock_call_api, mock_get_status):
        # Arrange
        config = self.config
        library_source = "jar"
        content_data = "library_file"
        cluster_id = "cluster_id"
        status = "INSTALLED"
        mock_get_status.return_value = status
        mock_call_api.return_value = "- response : success  -"

        obj_cluster = dbx_cluster.Cluster(config)

        # Act
        result = obj_cluster.install_cluster_library(
            config, library_source, content_data
        )

        # Assert
        mock_get_status.assert_called_once_with(
            config, library_source, content_data, False
        )
        mock_call_api.assert_called_once_with(
            config,
            "2.0/libraries/install",
            {"cluster_id": cluster_id, "libraries": {"jar": "library_file"}},
            "POST",
        )
        self.assertEqual(result, status)

    @patch(
        "cdh_dav_python.databricks_service.cluster.Cluster.get_cluster_library_status"
    )
    def test_install_cluster_library_already_installed(self, mock_get_status):
        # Arrange
        config = {"cdh_databricks_cluster": "cluster_id"}
        library_source = "jar"
        content_data = "library_file"
        cluster_id = "cluster_id"
        status = "INSTALLED"
        mock_get_status.return_value = status

        # Act
        result = Cluster.install_cluster_library(
            Cluster, config, library_source, content_data
        )

        # Assert
        mock_get_status.assert_called_once_with(
            config, library_source, content_data, False
        )
        self.assertEqual(result, status)

    @patch(
        "cdh_dav_python.databricks_service.cluster.Cluster.get_cluster_library_status"
    )
    @patch(
        "cdh_dav_python.databricks_service.cluster.Cluster.call_databricks_install_api"
    )
    def test_install_cluster_library_failure(self, mock_call_api, mock_get_status):
        # Arrange
        config = {"cdh_databricks_cluster": "cluster_id"}
        library_source = "jar"
        content_data = "library_file"
        cluster_id = "cluster_id"
        status = "NOT_INSTALLED"
        mock_get_status.return_value = status
        mock_call_api.return_value = "Error: Failed to install library"

        # Act
        result = Cluster.install_cluster_library(
            Cluster, config, library_source, content_data
        )

        # Assert
        mock_get_status.assert_called_once_with(
            config, library_source, content_data, False
        )
        mock_call_api.assert_called_once_with(
            config,
            "2.0/libraries/install",
            {"cluster_id": cluster_id, "libraries": {"jar": "library_file"}},
            "POST",
        )
        self.assertEqual(result, status)


if __name__ == "__main__":
    unittest.main()
