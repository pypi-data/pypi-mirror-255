import os

import requests

from shared_code import aad_helper, app_config


def get_json_file(file_system: str, file_name: str):
    storage_account_url = app_config.EDAV_STORAGE_CDH_CONTAINER_URL
    path_to_file = file_system + "/" + file_name
    token = aad_helper.get_aad_token(resource="https://storage.azure.com")
    header = {"Authorization": f"Bearer {token}"}
    full_url = storage_account_url + "/" + path_to_file
    response = requests.get(full_url, headers=header)
    if response.status_code == 200:
        return response.json()
    else:
        return None


def get_raw_file(file_system: str, file_name: str):
    storage_account_url = app_config.EDAV_STORAGE_CDH_CONTAINER_URL
    path_to_file = file_system + "/" + file_name
    token = aad_helper.get_aad_token(resource="https://storage.azure.com")
    header = {"Authorization": f"Bearer {token}"}
    full_url = storage_account_url + "/" + path_to_file
    response = requests.get(full_url, headers=header)
    if response.status_code == 200:
        return response.text
    else:
        return None


def save_file(data: str, file_system: str, file_name: str):
    service_client = aad_helper.get_edav_datalake_service_connection()

    directory_client = service_client.get_file_system_client(file_system)
    file_client = directory_client.get_file_client(file_name)
    file_client.upload_data(data=data, length=len(data), overwrite=True)


def does_file_exist(file_system: str, file_name: str):
    service_client = aad_helper.get_edav_datalake_service_connection()
    directory_client = service_client.get_file_system_client(file_system=file_system)
    file_client = directory_client.get_file_client(file_name)
    if file_client.exists():
        return True
    else:
        return False


def get_all_files_in_directory(directory: str, recursive=False):
    service_client = aad_helper.get_service_connection(
        account_url=f'https://{os.getenv("EDAV_STORAGE_ACCOUNT_NAME")}.dfs.core.windows.net')
    directory_client = service_client.get_file_system_client(file_system="cdh")
    path_list = directory_client.get_paths(path=directory, recursive=recursive)
    paths = []
    for path in path_list:
        if not path.is_directory:
            paths.append(path.name)

    return paths


def get_all_sub_directories_in_directory(directory: str, recursive=False):
    service_client = aad_helper.get_service_connection(
        account_url=f'https://{os.getenv("EDAV_STORAGE_ACCOUNT_NAME")}.dfs.core.windows.net')
    directory_client = service_client.get_file_system_client(file_system="cdh")
    path_list = directory_client.get_paths(path=directory, recursive=recursive)
    paths = []
    for path in path_list:
        if path.is_directory:
            paths.append(path.name)

    return paths
