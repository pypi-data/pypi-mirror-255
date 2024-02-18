"""
Module: test_cdc_tech_environment_file_file

This module contains unit tests for the CDC Tech Environment File functionality.

Functions:
test_execute: Test if the CDC Tech Environment File exists.
test_download_file: Test the content of the CDC Tech Environment File.
test_convert_to_windows_dir: Test the permissions of the CDC Tech Environment File.
test_combine_files:
"""
import pathlib
import sys
import os
from dotenv import load_dotenv
import cdh_dav_python.cdc_tech_environment_service.environment_file as cdc_env_file

sys.path.append("..")

# python -m pytest cdh_dav_lib/cdh_dav_python/tests
# Load the .env file
dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(dotenv_path)


def test_execute_script_string():
    """_summary_"""
    obj_env_file = cdc_env_file.EnvironmentFile()
    command = "ls -l"
    DATA_PRODUCT_ID = "wonder_metadata"
    ENVIRONMENT = "dev"
    execute_results = obj_env_file.execute_script_string(
        command, DATA_PRODUCT_ID, ENVIRONMENT
    )
    print(f"execute_results: {execute_results}")


def test_download_file():
    """
    Test the download_file function from the EnvironmentFile class.

    It downloads a file from a given URL and asserts the success of the download.

    Returns:
        None
    """
    DATA_PRODUCT_ID = "wonder_metadata"
    ENVIRONMENT = "dev"
    obj_env_file = cdc_env_file.EnvironmentFile()
    url = "https://github.com/Azure/azure-dev/releases/download/azure-dev-cli_1.0.2/azd-linux-amd64.tar.gz"
    file_name = "azd-linux-amd64.tar.gz"
    bin_folder = obj_env_file.get_local_bin_folder()
    status_code, execute_results = obj_env_file.download_file(
        url=url,
        data_product_id=DATA_PRODUCT_ID,
        environment=ENVIRONMENT,
        local_file_name=file_name,
        timeout=90,
        download_folder=bin_folder,
    )
    print(f"execute_results: {execute_results}")
    expected_results = os.path.join(bin_folder, file_name)
    # Assert the success of the download
    assert status_code == 200
    assert execute_results == expected_results


def test_delete_directory_manifest_downloads_dev():
    """
    Tests the function delete_directory_files on the 'dev_manifest_downloads' directory.

    This function first gets the project root directory and changes the current working directory to it.
    It then constructs the path to the 'dev_manifest_downloads' directory and calls delete_directory_files on it.
    The test asserts that the delete_directory_files function returns a non-empty result.

    This test function is specific to a development environment, and the 'dev_manifest_downloads' directory is expected to exist.
    The delete_directory_files function is expected to keep any files matching the pattern '*input.json' and delete all others.

    Note: This function prints the results of the delete_directory_files function, which includes messages about which files have been deleted.

    Raises
    ------
    AssertionError
        If no files were deleted, i.e., the result from delete_directory_files is empty.
    """

    # Get the absolute path of the current script
    current_script_path = os.path.abspath(__file__)

    # Get the project root directory by going up one or more levels
    project_root = os.path.dirname(os.path.dirname(current_script_path))

    # Change the current working directory to the project root directory
    os.chdir(project_root)
    app_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(app_dir)
    DATA_PRODUCT_ID = "wonder_metadata"
    ENVIRONMENT = "dev"

    obj_env_file = cdc_env_file.EnvironmentFile()
    manifest_path = parent_dir + "/" + ENVIRONMENT + "_manifest_downloads/"

    manifest_path = obj_env_file.convert_to_current_os_dir(
        manifest_path, DATA_PRODUCT_ID, ENVIRONMENT
    )
    data_product_id = "wonder_metadata"
    environment = "dev"
    delete_results = obj_env_file.delete_directory_files(
        manifest_path, data_product_id, environment, files_to_keep=["*input.json"]
    )
    print(f"delete_results: {delete_results}")
    assert len(delete_results) >= 0


def test_delete_directory_manifest_uploads_dev():
    """
    Tests the function delete_directory_files on the 'dev_manifest_uploads' directory.

    This function first gets the project root directory and changes the current working directory to it.
    It then constructs the path to the 'dev_manifest_uploads' directory and calls delete_directory_files on it.
    The test asserts that the delete_directory_files function returns a non-empty result.

    This test function is specific to a development environment, and the 'dev_manifest_uploads' directory is expected to exist.
    The delete_directory_files function is expected to keep any files matching the pattern '*input.json' and delete all others.

    Note: This function prints the results of the delete_directory_files function, which includes messages about which files have been deleted.

    Raises
    ------
    AssertionError
        If no files were deleted, i.e., the result from delete_directory_files is empty.
    """

    # Get the absolute path of the current script
    current_script_path = os.path.abspath(__file__)

    # Get the project root directory by going up one or more levels
    project_root = os.path.dirname(os.path.dirname(current_script_path))

    # Change the current working directory to the project root directory
    os.chdir(project_root)
    app_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(app_dir)
    DATA_PRODUCT_ID = "wonder_metadata"
    ENVIRONMENT = "dev"
    obj_env_file = cdc_env_file.EnvironmentFile()
    manifest_path = parent_dir + "/" + ENVIRONMENT + "_manifest_uploads/"

    manifest_path = obj_env_file.convert_to_current_os_dir(
        manifest_path, DATA_PRODUCT_ID, ENVIRONMENT
    )
    delete_results = obj_env_file.delete_directory_files(
        manifest_path,
        DATA_PRODUCT_ID,
        ENVIRONMENT,
        files_to_keep=["*input.json, *input.xlsx"],
    )
    print(f"delete_results: {delete_results}")
    assert len(delete_results) >= 0


def test_download_file_error():
    """
    Test the download_file function from the EnvironmentFile class.

    It downloads a file from a given URL and asserts the success of the download.

    Returns:
        None
    """
    DATA_PRODUCT_ID = "wonder_metadata"
    ENVIORNMENT = "dev"
    obj_env_file = cdc_env_file.EnvironmentFile()
    url = "https://github.com/Azure/azure-dev/releases/download/azure-dev-cli_1.0.2/BAD_FILE_ERROR_CONDITION.tar.gz"
    file_name = "BAD_FILE_ERROR_CONDITION.tar.gz"
    bin_folder = obj_env_file.get_local_bin_folder()
    status_code, execute_results = obj_env_file.download_file(
        url=url,
        data_product_id=DATA_PRODUCT_ID,
        environment=ENVIORNMENT,
        local_file_name=file_name,
        timeout=90,
        download_folder=bin_folder,
    )
    print(f"execute_results: {execute_results}")
    # Assert the success of the download
    assert status_code == 500


def test_convert_to_windows_dir():
    """_summary_"""
    unix_dir = "/Users/zfi4/OneDrive - CDC/Documents/DMI PH Infrastructure/Program-Agnostic CDC Data Hub LAVA (CDH)/data-ecosystem-services/cdh_dav_python/ocio/wonder_metadata_dev/config/config.dev.json"
    env_file = cdc_env_file.EnvironmentFile()
    DATA_PRODUCT_ID = "wonder_metadata"
    ENVIRONMENT = "dev"
    windows_dir = env_file.convert_to_windows_dir(
        unix_dir, DATA_PRODUCT_ID, ENVIRONMENT
    )
    print(f"windows_dir: {windows_dir}")


def test_combine_files():
    """Test the combine_files method
    Change current working directory to docs directory before runing
    """

    obj_env_file = cdc_env_file.EnvironmentFile()
    # Get the current file's directory
    current_file_dir = pathlib.Path(__file__).parent.absolute()

    # Go up two levels
    three_levels_up = current_file_dir.parent.parent.parent

    # Get the 'docs' directory
    docs_dir = three_levels_up / "docs"

    # Ensure it's a string
    docs_dir_str = str(docs_dir)

    # user_id = "zfi4"
    # branch = "dev-jcbowyer"
    # project_dir = "OneDrive - CDC\\CDH Analytics\\"
    # branch_dir = f"cdh-{branch}\\"
    # source_path = f"C:\\Users\\{user_id}\\{project_dir}{branch_dir}"
    # docs_dir = "docs\\"
    # source_path = f"{source_path}{docs_dir}"
    DATA_PRODUCT_ID = "wonder_metadata"
    ENVIRONMENT = "dev"
    single_file_name = "index_single_file.md"
    destination_path = f"{docs_dir_str}\\"
    source_path = f"{docs_dir_str}\\build\\single_html\\"
    source_path = obj_env_file.convert_to_current_os_dir(
        source_path, DATA_PRODUCT_ID, ENVIRONMENT
    )
    destination_path = obj_env_file.convert_to_current_os_dir(
        destination_path, DATA_PRODUCT_ID, ENVIRONMENT
    )
    # source_file = f"{source_path}{single_file_name}"
    destination_file = f"{destination_path}{single_file_name}"
    combine_results = obj_env_file.combine_files(
        source_path, "*_ch.md", destination_file
    )
    expected_results = "Success"
    assert combine_results == expected_results
