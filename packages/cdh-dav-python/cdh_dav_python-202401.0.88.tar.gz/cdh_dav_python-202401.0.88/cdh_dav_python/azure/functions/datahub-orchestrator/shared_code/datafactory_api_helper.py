import requests
from azure.identity import ClientSecretCredential
from azure.mgmt.datafactory import DataFactoryManagementClient

from shared_code import aad_helper, app_config


def get_token_and_url(target_resource_name: str):
    token = aad_helper.get_aad_token(resource="https://management.azure.com")
    url = f"{app_config.DATAFACTORY_URL}/pipelines/{target_resource_name}/createRun?api-version=2018-06-01"
    return token, url;


def invoke(url: str, token: str, params_json: any):
    response = requests.post(url, json=params_json, headers={"Authorization": f"Bearer {token}"})
    if response.ok:
        return response.json()["runId"]
    else:
        print(response.text)
        raise Exception(f"Error invoking data factory url at {url}. \n Status_Code: {response.status_code}. Text: {response.text}")


def get_adf_client():
    credentials = ClientSecretCredential(client_id=app_config.CLIENT_ID, client_secret=app_config.CLIENT_SECRET,
                                         tenant_id=app_config.TENANT_ID)
    adf_client = DataFactoryManagementClient(credentials, app_config.DATAFACTORY_SUBSCRIPTION_ID)
    return adf_client


def get_run_id_status(run_id: str, adf_client: any):
    rg_name = 'OCIO-DAV-DEV'
    df_name = 'edav-cdh-dev-factory'
    pipeline_run = adf_client.pipeline_runs.get(
        rg_name, df_name, run_id)
    return pipeline_run.status



