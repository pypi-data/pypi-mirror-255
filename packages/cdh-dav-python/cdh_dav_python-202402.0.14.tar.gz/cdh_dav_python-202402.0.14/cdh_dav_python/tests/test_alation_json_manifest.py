from cdh_dav_python.alation_service import (
    db_schema as alation_schema,
    json_manifest as alation_manifest
)
from cdh_dav_python.cdc_tech_environment_service import (
    environment_file as cdc_env_file
)
import cdh_dav_python.cdc_admin_service.environment_logging as environment_logging
from cdh_dav_python.cdc_metadata_service import (
    environment_metadata as cdc_env_metadata
)
import os
import sys
import pytest
from dotenv import load_dotenv
sys.path.append("..")


dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path)

ENVIRONMENT = "dev"


def get_config(parameters):

    environment_metadata = cdc_env_metadata.EnvironmentMetaData()

    config = environment_metadata.get_configuration_common(
        parameters, None)

    return config


def test_validate_manifest_uploads_json_file():

    # Get the absolute path of the current script
    current_script_path = os.path.abspath(__file__)

    # Get the project root directory by going up one or more levels
    project_root = os.path.dirname(os.path.dirname(current_script_path))

    # Change the current working directory to the project root directory
    os.chdir(project_root)

    app_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(app_dir)

    obj_file = cdc_env_file.EnvironmentFile()
    manifest_path = (
        parent_dir + "/" + ENVIRONMENT + "_manifest_uploads/"
    )

    manifest_path = obj_file.convert_to_current_os_dir(manifest_path)
    manifest_file = obj_file.get_latest_file(manifest_path, "json")

    assert (manifest_file is not None)
    running_local = True
    dbutils = None
    manifest_file_exists = obj_file.file_exists(
        running_local, manifest_file, dbutils)

    assert (manifest_file_exists is True)

    data_definition_file_path = (
        parent_dir + "/" + ENVIRONMENT + "_data_definitions/"
    )

    data_definition_file_path = obj_file.convert_to_current_os_dir(
        data_definition_file_path)

    excel_data_definition_file = obj_file.get_latest_file(
        data_definition_file_path, "json", "manifest")

    print("excel_data_definition_file: ", excel_data_definition_file)
    print("manifest_file: ", manifest_file)

    manifest = alation_manifest.ManifestJson(excel_data_definition_file)
    content_result = manifest.validate_manifest(
        manifest_file, excel_data_definition_file)
    assert len(content_result) > 0


if __name__ == '__main__':
    pytest.main()
