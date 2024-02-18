from dotenv import load_dotenv
import os
import sys
import unittest
import cdh_dav_python.jira_service.jira_client as jira_client
import cdh_dav_python.cdc_metadata_service.environment_metadata as cdc_env_metadata
from cdh_dav_python.cdc_admin_service.environment_logging import LoggerSingleton
import cdh_dav_python.az_key_vault_service.az_key_vault as az_key_vault
import cdh_dav_python.cdc_tech_environment_service.environment_core as az_environment_core

from pathlib import Path

sys.path.append("..")


NAMESPACE_NAME = os.path.basename(os.path.dirname(__file__))
# Get the parent folder name of the running file
SERVICE_NAME = os.path.basename(__file__)


class TestJiraClient(unittest.TestCase):
    def get_config(self, parameters, data_product_id, environment):
        environment_metadata = cdc_env_metadata.EnvironmentMetaData()

        config = environment_metadata.get_configuration_common(
            parameters, None, data_product_id, environment
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

        obj_az_key_vault = az_key_vault.AzKeyVault(
            tenant_id,
            client_id,
            client_secret,
            vault_url,
            running_interactive,
            data_product_id,
            environment,
        )

        return config, obj_az_key_vault

    def test_get_tasks_cdh_wonder(self):
        data_product_id = "wonder_metadata"
        environment = "dev"

        tracer, logger = LoggerSingleton.instance(
            NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
        ).initialize_logging_and_tracing()

        with tracer.start_as_current_span("test_get_tasks"):
            try:
                dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
                logger.info(f"dotenv_path:{dotenv_path}")
                load_dotenv(dotenv_path)

                # Get the absolute path of the current script
                current_script_path = os.path.abspath(__file__)

                # Get the project root directory by going up one or more levels
                project_root = os.path.dirname(os.path.dirname(current_script_path))

                # Change the current working directory to the project root directory
                os.chdir(project_root)

                repository_path_default = str(Path(os.getcwd()))
                parameters = {
                    "data_product_id": "wonder_metadata",
                    "data_product_id_root": "wonder",
                    "data_product_id_individual": "metadata",
                    "environment": "dev",
                    "repository_path": repository_path_default,
                }

                config, obj_az_keyvault = self.get_config(
                    parameters, data_product_id, environment
                )

                cdh_databricks_kv_scope = config.get("cdh_databricks_kv_scope")

                jira_client_secret_key = config.get("jira_client_secret_key")
                jira_client_secret = obj_az_keyvault.get_secret(
                    jira_client_secret_key, cdh_databricks_kv_scope
                )
                if jira_client_secret is None:
                    raise Exception(
                        f"Unable to get Jira client secret from key_vault {jira_client_secret_key}"
                    )
                else:
                    logger.info(f"jira_client_secret_length:{len(jira_client_secret)}")

                # Set your default project value here
                jira_project = config.get("jira_project_key")
                if jira_project is None:
                    raise Exception(
                        f"Unable to get jira_project from config {jira_project}"
                    )

                # "DTEDS"

                jira_base_url = config.get("jira_base_url")
                if jira_base_url is None:
                    raise Exception(
                        f"Unable to get jira_base_url from config {jira_base_url}"
                    )

                jira_headers = {
                    "Authorization": f"Bearer {jira_client_secret}",
                    "Content-Type": "application/json",
                }
                logger.info(f"headers_length:{str(len(jira_headers))}")

                jira_client_instance = jira_client.JiraClient()
                jira_tasks = jira_client_instance.get_tasks(
                    jira_project,
                    jira_headers,
                    jira_base_url,
                    data_product_id,
                    environment,
                )
                logger.info(jira_tasks)
                assert jira_tasks is not None
            except Exception as ex:
                error_msg = "Error: %s", ex
                exc_info = sys.exc_info()
                LoggerSingleton.instance(
                    NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
                ).error_with_exception(error_msg, exc_info)
                raise
