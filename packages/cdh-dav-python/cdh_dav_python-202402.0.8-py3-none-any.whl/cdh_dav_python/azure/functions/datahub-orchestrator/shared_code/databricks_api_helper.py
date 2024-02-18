import base64
import json

from shared_code import app_config, aad_helper, datalake_helper, databricks_cluster_types
import requests


def get_token_and_url(target_resource_name: str):
    # https://learn.microsoft.com/en-us/azure/databricks/dev-tools/api/2.0/jobs?source=recommendations
    url = f"{app_config.DATABRICKS_URL}/api/2.1/jobs/run-now"
    return app_config.DATABRICKS_TOKEN, url;


def invoke(url: str, token: str, notebook_path: str, request_id: str,
           notebook_params: any, spark_conf_type: str, dependencies: [str]):

    shell_script_path = generate_and_upload_dependencies_install_script\
                (dependencies=dependencies,notebook_path=notebook_path)

    job_id = get_notebook_job_id(
                        notebook_path=notebook_path,
                        token=token,
                        spark_conf_type=spark_conf_type,
                        shell_script_path=shell_script_path)
    job_payload_str = '{"job_id": $JOB_ID,' \
                      '"idempotency_token": "$REQUEST_ID",' \
                      '"notebook_params": $NOTEBOOK_PARAMS }'

    job_payload_str = job_payload_str \
        .replace("$JOB_ID", str(job_id)) \
        .replace("$REQUEST_ID", request_id) \
        .replace("$NOTEBOOK_PARAMS", json.dumps(notebook_params))

    job_payload = json.loads(job_payload_str)
    response = requests.post(url, json=job_payload,
                             headers={"Authorization": f"Bearer {token}"})

    if response.ok:
        run_id = response.json()["run_id"]
        return job_id, run_id
    else:
        print(response.text)
        raise Exception(f"Status_Code: {response.status_code}. Text: {response.text}")


# https://github.com/jixjia/databricks-create-run-jobs/blob/master/run_all_jobs.py
#
def create_job(token: str,
               notebook_path: str,
               spark_conf_type: str,
               shell_script_path: str):
    if spark_conf_type.casefold() == app_config.DATABRICKS_CLUSTER_CONFIG_NON_PASSTHROUGH:
        spark_conf = databricks_cluster_types.CLUSTER_NON_PASS_THROUGH_CREDS_SPARK_CONF
    else:
        spark_conf = databricks_cluster_types.CLUSTER_PASS_THROUGH_CREDS_SPARK_CONF_DEFAULT

    init_script_cluster_scope = ""
    if shell_script_path is not None and len(shell_script_path) > 0:
        init_script_cluster_scope = """{
            "dbfs": {
                "destination": "dbfs:$init_script_file_name"
            }
        }"""
        init_script_cluster_scope = init_script_cluster_scope \
            .replace("$init_script_file_name", shell_script_path)

    # https://docs.databricks.com/dev-tools/api/latest/jobs.html#operation/JobsCreate
    job_payload_str = """{
        "name": "cdh_etl_$NOTEBOOK",
        "max_concurrent_runs": 100,
        "tags": {
            "project": "CDH",
            "git_branch": "$GIT_BRANCH",
            "spark_version": "$SPARK_VERSION",
            "node_type": "$NODE_TYPE"
        },
        "tasks": [
            {
                "task_key": "cdh_etl_$NOTEBOOK",
                "description": "execute $NOTEBOOK",
                "new_cluster": {
                    "spark_version": "$SPARK_VERSION",
                    "node_type_id": "$NODE_TYPE",
                    "driver_node_type_id": "$NODE_TYPE",
                    "cluster_log_conf": {
                        "dbfs": {
                            "destination": "dbfs:/mnt/cluster-logs"
                        }
                    },
                    "spark_conf": {
                        $SPARK_CONF
                    },
                    "init_scripts": [
                        $INIT_SCRIPT_CLUSTER_SCOPE
                    ],
                    "spark_env_vars": {
                        "CDH_ENVIRONMENT": "$CDH_ENVIRONMENT"
                    },
                    "azure_attributes": {
                        "first_on_demand": 1,
                        "availability": "ON_DEMAND_AZURE",
                        "spot_bid_max_price": -1
                    },
                    "autoscale": {
                        "min_workers": 2,
                        "max_workers": 8
                    }
                },
                "notebook_task": {
                    "notebook_path": "$NOTEBOOK_PATH",
                    "source": "GIT"
                }

            }
        ],
        "access_control_list": [
            {
                "group_name": "gp-u-EDAV-CDH-ADMIN-AAD",
                "permission_level": "CAN_MANAGE"
            }
        ],
        "git_source": {
            "git_url": "https://github.com/cdcent/cdc-datahub-engineering.git",
            "git_provider": "gitHub",
            "git_branch": "$GIT_BRANCH"
        }
    }"""

    # params_json = json.loads(os.path.expandvars(json.dumps(params_json)))
    notebook = notebook_path.rsplit('/', 1)[-1]
    job_payload_str = job_payload_str.replace("$NOTEBOOK_PATH", notebook_path) \
        .replace("$NOTEBOOK", notebook) \
        .replace("$CDH_ENVIRONMENT", app_config.APP_ENVIRONMENT) \
        .replace("$DATABRICKS_NB_PATH_PREFIX", app_config.DATABRICKS_NB_PATH_PREFIX) \
        .replace("$NODE_TYPE", "Standard_D8s_v3") \
        .replace("$SPARK_VERSION", "11.3.x-scala2.12") \
        .replace("$GIT_BRANCH", app_config.GIT_BRANCH) \
        .replace("$INIT_SCRIPT_CLUSTER_SCOPE", init_script_cluster_scope) \
        .replace("$SPARK_CONF", spark_conf)

    job_payload = json.loads(job_payload_str)
    url = f"{app_config.DATABRICKS_URL}/api/2.1/jobs/create"
    response = requests.post(url, json=job_payload,
                             headers={"Authorization": f"Bearer {token}"})

    if response.ok:
        return response.json()["job_id"]
    else:
        print(response.text)
        raise Exception(f"Status_Code: {response.status_code}. Text: {response.text}")


def get_notebook_job_id(notebook_path: str, token: str,
                        spark_conf_type: str,
                        shell_script_path:str):
    config_json = datalake_helper.get_json_file(
        file_system=app_config.DATAHUB_JOURNALS_LOCATION,
        file_name="_databricks_notebook_jobs_config.json")
    if config_json is None:
        config_json = {}

    if notebook_path in config_json:
        job_id = config_json[notebook_path]
    else:
        job_id = create_job(token=token,
                            notebook_path=notebook_path,
                            spark_conf_type=spark_conf_type,
                            shell_script_path=shell_script_path)
        config_json[notebook_path] = job_id
        datalake_helper.save_file(data=json.dumps(config_json), file_system=app_config.DATAHUB_JOURNALS_LOCATION,
                                  file_name="_databricks_notebook_jobs_config.json")

    return job_id


def generate_and_upload_dependencies_install_script(dependencies:[str],notebook_path:str):
    if len(dependencies) == 0:
        return

    notebook_name = notebook_path.rsplit('/', 1)[-1]
    shell_script_path = f"/cdh/etl/{notebook_name}_install_reqs.sh"
    script_text = "#!/bin/sh \n"
    for dependency in dependencies:
        script_text = script_text + f"/databricks/python/bin/pip install {dependency} \n"

    message_bytes = script_text.encode('utf-8')
    base64_bytes = base64.b64encode(message_bytes)
    base64_message = base64_bytes.decode('utf-8')
    url = f"{app_config.DATABRICKS_URL}/api/2.0/dbfs/put"
    token = app_config.DATABRICKS_TOKEN
    job_payload = {
        "path": shell_script_path,
        "contents": base64_message,
        "overwrite": "true"
    }
    response = requests.post(url, json=job_payload,
                             headers={"Authorization": f"Bearer {token}"})
    if response.ok:
        return shell_script_path
    else :
        raise ValueError(f"error when uploading init script for {notebook_name}. "
                         f"\n {response.status_code} - {response.text}")



def invoke_job_execution():
    print(1)
    # https://stackoverflow.com/questions/56153505/calling-databricks-notebook-using-databricks-job-api-runs-submit-endpoint
