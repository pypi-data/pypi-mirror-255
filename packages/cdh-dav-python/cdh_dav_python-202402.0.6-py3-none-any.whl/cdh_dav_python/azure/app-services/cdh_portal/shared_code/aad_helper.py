import os

import jwt
import requests
from azure.identity import ClientSecretCredential
from azure.storage.blob import BlobServiceClient
from azure.storage.filedatalake import DataLakeServiceClient
from flask import request

from shared_code import app_config


def get_aad_token(resource):
    tenant_id = app_config.TENANT_ID
    client_id = app_config.CLIENT_ID
    client_secret = app_config.CLIENT_SECRET
    url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/token"
    data = {
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret,
        "resource": resource
    }
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    response = requests.post(url, data=data, headers=headers)
    if response.ok:
        return response.json()["access_token"]
    else:
        print(response.text)
        raise Exception(f"Status_Code: {response.status_code}. Text: {response.text}")


def get_service_connection(account_url: str):
    credential = ClientSecretCredential(
        client_id=app_config.CLIENT_ID,
        client_secret=app_config.CLIENT_SECRET,
        tenant_id=app_config.TENANT_ID)

    service_client = DataLakeServiceClient(
        account_url=account_url,
        credential=credential)

    return service_client


def get_edav_datalake_service_connection():
    return get_service_connection(app_config.EDAV_STORAGE_CDH_CONTAINER_URL)


def get_edav_blob_service_service_connection():
    credential = ClientSecretCredential(
        client_id=app_config.CLIENT_ID,
        client_secret=app_config.CLIENT_SECRET,
        tenant_id=app_config.TENANT_ID)

    service_client = BlobServiceClient(
        account_url=app_config.EDAV_STORAGE_URL,
        credential=credential)

    return service_client


def get_name_and_email_address():
    token_present = "X-MS-TOKEN-AAD-ACCESS-TOKEN" in request.headers
    if token_present:
        token = request.headers.get('X-MS-TOKEN-AAD-ACCESS-TOKEN')
        if token is not None and len(token) > 0:
            decoded_data = jwt.decode(jwt=token, options={"verify_signature": False})
            name = decoded_data["name"]
            email = decoded_data["upn"]
            return name, email

    return "Anonymous", "n/a"


def is_user_an_admin(user_email: str, data_source: str):
    all_users = os.getenv("CDH_PORTAL_ADMINS")
    skip_admin_check = True if os.getenv("CDH_PORTAL_ADMINS_SKIP_CHECK") is not None \
                               and os.getenv("CDH_PORTAL_ADMINS_SKIP_CHECK").casefold() == "true" \
        else False

    if skip_admin_check:
        return True

    if all_users is not None:
        for user in all_users.split(";"):
            if user.casefold() == user_email.casefold():
                return True

    return False
