import json
import os
import tempfile

import requests

from shared_code import aad_helper, app_config


def get_json_file(file_system: str, file_name: str):
    file_text = get_file_text(file_system=file_system, file_name=file_name)
    if file_text is not None:
        config_json = json.loads(file_text)
        return config_json

    return None


def get_file_text(file_system: str, file_name: str):
    service_client = aad_helper.get_edav_datalake_service_connection()
    directory_client = service_client.get_file_system_client(file_system=file_system)
    file_client = directory_client.get_file_client(file_name)
    if file_client.exists():
        download = file_client.download_file()
        downloaded_bytes = download.readall()
        temp_file_path = tempfile.gettempdir()
        file_local_path = f"{temp_file_path}/{file_name}"
        with open(file_local_path, "wb") as my_file:
            my_file.write(downloaded_bytes)
            my_file.close()

        file_object = open(file_local_path, "r")
        return file_object.read()
    else:
        return None


def save_file(data: str, file_system: str, file_name: str):
    service_client = aad_helper.get_edav_datalake_service_connection()

    directory_client = service_client.get_file_system_client(file_system)
    file_client = directory_client.get_file_client(file_name)
    file_client.upload_data(data=data, length=len(data), overwrite=True)


def delete_file(account_url: str, file_system: str, file_name: str):
    service_client = aad_helper.get_service_connection(account_url)

    directory_client = service_client.get_file_system_client(file_system)
    file_client = directory_client.get_file_client(file_name)
    if file_client.exists():
        file_client.delete_file()


def get_all_ready_files(sub_directory: str):
    blob_service_client = aad_helper.get_edav_blob_service_service_connection()
    container_client = blob_service_client.get_container_client(container='cdh')
    blob_list = container_client.list_blobs(name_starts_with=sub_directory)
    return blob_list


def does_file_exist(file_system: str, file_name: str):
    service_client = aad_helper.get_edav_datalake_service_connection()
    directory_client = service_client.get_file_system_client(file_system=file_system)
    file_client = directory_client.get_file_client(file_name)
    if file_client.exists():
        return True
    else:
        return False


def rename_file(file_system: str, file_name: str, new_name: str, new_path: str = ""):
    service_client = aad_helper.get_edav_datalake_service_connection()
    directory_client = service_client.get_file_system_client(file_system=file_system)
    file_client = directory_client.get_file_client(file_name)
    token = aad_helper.get_aad_token(resource="https://storage.azure.com")
    if new_path is None or new_path == "":
        new_path = file_client.file_system_name
    else:
        root_dir = new_path.split("/")[0]
        remaining_path = "/".join(new_path.split("/")[1:])
        create_dir_if_not_exists(root_dir=root_dir, dir_name=remaining_path)

    if file_client.exists():
        url = f"https://{app_config.EDAV_STORAGE_ACCOUNT_NAME}.dfs.core.windows.net/{app_config.EDAV_STORAGE_CDH_CONTAINER_NAME}/{new_path}/{new_name}"
        response = requests.put(url, headers={"Authorization": f"Bearer {token}","x-ms-rename-source": f"/{app_config.EDAV_STORAGE_CDH_CONTAINER_NAME}/{file_client.file_system_name}/{file_name}"})
        if response.ok:
            print('Renamed file')
        else:
            print(response.text)
            raise Exception(
                f"Error renaming file at {url}. \n Status_Code: {response.status_code}. Text: {response.text}")
    else:
        return False


def create_dir_if_not_exists(root_dir: str, dir_name:str):
    service_client = aad_helper.get_edav_datalake_service_connection()
    directory_client = service_client.get_file_system_client(file_system=root_dir)
    directory_client.create_directory(dir_name)


def move_directory(old_dir_name: str, new_dir_name: str):
    service_client = aad_helper.get_edav_datalake_service_connection()
    file_system_client = service_client.get_file_system_client(file_system="cdh")
    directory_client = file_system_client.get_directory_client(old_dir_name)
    try:
        directory_client.rename_directory(new_name=new_dir_name)
    except Exception as ex:
        print(f"{old_dir_name} does not exist.")

