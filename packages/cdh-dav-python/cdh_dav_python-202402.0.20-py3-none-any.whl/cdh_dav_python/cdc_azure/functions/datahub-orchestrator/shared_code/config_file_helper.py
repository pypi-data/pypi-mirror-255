import json
import os
from datetime import datetime, timedelta, timezone
import logging
import pytz

from shared_code import app_config, datafactory_api_helper, databricks_api_helper, aad_helper, datalake_helper, \
    app_utils, workflow_state_store_helper, logicapp_api_helper


def get_next_unprocessed_service(config_json, request_id):
    services = config_json["services"]
    workflow_id = config_json["workflow_id"]
    delivery_date = config_json["delivery_date"]
    data_source = config_json["datasource"]
    for service in services:
        service_name = service["display_name"]
        if service.get("tracking") is None \
                or service["tracking"].get("status") is None \
                or service["tracking"]["status"] == app_config.WORKFLOW_STATUS_RERUN:

            ok_to_proceed = __check_service_for_schedule(service)
            service["tracking"] = {} if service.get("tracking") is None else service["tracking"]
            current_status = service["tracking"]["status"] if service["tracking"].get("status") is not None else ""
            service["tracking"]["request_id"] = request_id \
                if service["tracking"].get("request_id") is None \
                else service["tracking"]["request_id"]
            if ok_to_proceed:
                service["tracking"]["status"] = app_config.WORKFLOW_STATUS_RUNNING
                service["tracking"]["start_utc"] = app_utils.utc_now_formatted() \
                    if service["tracking"].get("start_utc") is None \
                    else service["tracking"]["start_utc"]
            else:
                service["tracking"]["status"] = app_config.WORKFLOW_STATUS_PENDING_SCHEDULE_EXPIRATION
                service["tracking"]["start_utc"] = app_utils.utc_now_formatted()
                workflow_state_store_helper.insert_scheduled_status(
                    data_source=data_source,
                    workflow_id=workflow_id,
                    delivery_date=delivery_date,
                    service_json=service)
            return service
        else:
            logging.info(f"[{workflow_id}] {service_name} has completed already.")

    return None


def invoke_next_service(service: object, data_source: str, delivery_date: str, workflow_id: str, request_id: str,
                        delivery_type: str, data_manager_email: str, vendor_delivery_location: str,
                        target_database: str):
    status = service["tracking"]["status"]
    service_name = service["display_name"]
    if status != app_config.WORKFLOW_STATUS_RUNNING:
        logging.info(f"[{workflow_id}] Not processing {service_name} since its status is {status}.")
        return

    # all services are invoked with atleast these mandatory parameters
    params_json = service["parameters"]
    params_json["workflow_id"] = workflow_id
    params_json["request_id"] = request_id
    params_json["data_source"] = data_source
    params_json["delivery_date"] = delivery_date

    archive_date = app_utils.utc_now_formatted_ym()

    # params_json = json.loads(os.path.expandvars(json.dumps(params_json)))
    temp_params = json.dumps(params_json)
    temp_params = os.path.expandvars(temp_params)
    temp_params = temp_params.replace("$DATA_SOURCE", data_source) \
        .replace("$DELIVERY_DATE", delivery_date) \
        .replace("$DELIVERY_TYPE", delivery_type) \
        .replace("$WORKFLOW_ID", workflow_id) \
        .replace("$REQUEST_ID", request_id) \
        .replace("$DATA_MANAGER_EMAIL", data_manager_email) \
        .replace("$VENDOR_DELIVERY_LOCATION", vendor_delivery_location) \
        .replace("$WORKFLOW_IN_PROGRESS_DIRECTORY", app_config.WORKFLOW_IN_PROGRESS_DIRECTORY) \
        .replace("$DATABRICKS_NB_PATH_PREFIX", app_config.DATABRICKS_NB_PATH_PREFIX) \
        .replace("$ARCHIVE_DATE", archive_date) \
        .replace("$TARGET_DATABASE", target_database)
    params_json = json.loads(temp_params)

    target_system = service['target_system']
    target_resource_name = service['target_resource_name']

    if target_system.lower() == "adf":
        token, url = datafactory_api_helper.get_token_and_url(target_resource_name)
        service["tracking"]["url"] = url
        run_id = datafactory_api_helper.invoke(url=url, params_json=params_json, token=token)
        service["tracking"]["response_id"] = run_id
        service["tracking"][
            "response_tracking_url"] = f"{app_config.DATAFACTORY_URL}/pipelineruns/{run_id}?api-version=2018-06-01"

    elif target_system.lower() == "adb":
        token, url = databricks_api_helper.get_token_and_url(target_resource_name)
        spark_conf_type = app_config.DATABRICKS_CLUSTER_CONFIG_PASSTHROUGH_DEFAULT
        dependencies = []
        if service.get("cluster_config") is not None:
            if service["cluster_config"].get("spark_conf_type") is not None:
                spark_conf_type = service["cluster_config"]["spark_conf_type"]
            if service["cluster_config"].get("dependencies") is not None:
                dependencies = service["cluster_config"]["dependencies"]

        service["tracking"]["url"] = url
        job_id, run_id = \
            databricks_api_helper.invoke(url=url,
                                         notebook_path=target_resource_name,
                                         notebook_params=params_json,
                                         token=token,
                                         request_id=request_id,
                                         spark_conf_type=spark_conf_type,
                                         dependencies = dependencies)
        service["tracking"]["response_id"] = run_id

        service["tracking"]["response_tracking_url"] = f"{app_config.DATABRICKS_URL}/#job/{job_id}/run/{run_id}"

    elif target_system.lower() == "ala":
        url = os.getenv(target_resource_name)
        service["tracking"]["url"] = url
        run_id = logicapp_api_helper.invoke(url=url, params_json=params_json)
        service["tracking"]["response_id"] = run_id
        service["tracking"]["response_tracking_url"] = ""

    else:
        raise Exception(f"Target System: {target_system} is not supported.")

    service["parameters"] = params_json


def update_service_status_by_request_id(config_json, request_id: str, status: str, event_time_utc: str):
    services = config_json["services"]
    for service in services:
        if service.get("tracking") is not None:
            if service["tracking"].get("request_id") is not None and service["tracking"]["request_id"] == request_id:
                service["tracking"]["status"] = status
                service["tracking"]["end_utc"] = event_time_utc
                if status.casefold() == app_config.WORKFLOW_STATUS_RERUN.casefold() and \
                        service.get("schedule") is not None:
                    __check_for_override_of_schedule(service=service)

                # set root tracking status
                # config_json["tracking"]["status"] = status
                return service


def add_error_message_and_save(config_file_name: str, error_text: str):
    config_json = datalake_helper.get_json_file(file_system=app_config.WORKFLOW_IN_PROGRESS_DIRECTORY,
                                                file_name=config_file_name)

    if config_json is None:
        config_json = {}

    config_json["error"] = {}
    config_json["error"]["text"] = error_text
    config_json["error"]["time"] = app_utils.utc_now_formatted()

    split_name = os.path.splitext(config_file_name)
    file_name = split_name[0]
    new_file_name = f"{file_name}_{app_config.WORKFLOW_STATUS_FAILED}.json"
    datalake_helper.save_file(data=json.dumps(config_json), file_system=app_config.WORKFLOW_IN_PROGRESS_DIRECTORY
                              , file_name=config_file_name)

    datalake_helper.rename_file(file_system=app_config.WORKFLOW_IN_PROGRESS_DIRECTORY
                                , file_name=config_file_name, new_name=new_file_name)


def add_event_message_and_save(config_file_name: str, event_msg_json: any):
    config_json = datalake_helper.get_json_file(file_system=app_config.WORKFLOW_IN_PROGRESS_DIRECTORY,
                                                file_name=config_file_name)

    if config_json is None:
        config_json = {}

    if "events" not in config_json:
        config_json["events"] = []

    config_json["events"].append(event_msg_json)

    datalake_helper.save_file(data=json.dumps(config_json), file_system=app_config.WORKFLOW_IN_PROGRESS_DIRECTORY
                              , file_name=config_file_name)


def __check_service_for_schedule(service):
    ok_to_proceed = True
    if service.get("schedule") is not None and service["schedule"].get("prevent_run_window_start_hour_et") is not None:
        eastern_tz = pytz.timezone("America/New_York")
        current_datetime = eastern_tz.localize(datetime.now())
        prevent_run_window_start_hour_et = int(service["schedule"]["prevent_run_window_start_hour_et"])
        prevent_run_window_end_hour_et = int(service["schedule"]["prevent_run_window_end_hour_et"])
        weekends_included = bool(service["schedule"]["weekends_included"]) \
            if service["schedule"].get("weekends_included") is not None \
            else False

        prevent_run_window_start_time_et = datetime(year=current_datetime.year,
                                                    month=current_datetime.month,
                                                    day=current_datetime.day,
                                                    hour=prevent_run_window_start_hour_et)

        prevent_run_window_start_time_et = eastern_tz.localize(prevent_run_window_start_time_et)

        if prevent_run_window_end_hour_et >= prevent_run_window_start_hour_et:
            prevent_run_window_end_time_et = datetime(year=current_datetime.year, month=current_datetime.month,
                                                      day=current_datetime.day, hour=prevent_run_window_end_hour_et)
        else:
            prevent_run_window_end_time_et = datetime(year=current_datetime.year, month=current_datetime.month,
                                                      day=current_datetime.day, hour=prevent_run_window_end_hour_et) \
                                             + timedelta(hours=24, minutes=0)

        prevent_run_window_end_time_et = eastern_tz.localize(prevent_run_window_end_time_et)

        service["schedule"]["current_datetime_et"] = current_datetime.strftime('%Y-%m-%dT%H:%M:%S')
        service["schedule"]["prevent_run_window_start_time_et"] = prevent_run_window_start_time_et.strftime(
            '%Y-%m-%dT%H:%M:%S')
        service["schedule"]["prevent_run_window_end_time_et"] = prevent_run_window_end_time_et.strftime(
            '%Y-%m-%dT%H:%M:%S')

        if not weekends_included and app_utils.is_weekend(current_datetime):
            service["schedule"]["reason"] = \
                "Proceeding since current date is weekend and runs are configured to be allowed on weekends."
            print("ok")
        elif prevent_run_window_start_time_et < current_datetime < prevent_run_window_end_time_et:
            ok_to_proceed = False
        else:
            service["schedule"]["reason"] = \
                "Proceeding since current time does not fall in prevention window."

    return ok_to_proceed


def __check_for_override_of_schedule(service):
    eastern_tz = pytz.timezone("America/New_York")
    current_datetime = eastern_tz.localize(datetime.now())
    prevent_run_window_start_time_et = datetime.strptime(service["schedule"]["prevent_run_window_start_time_et"],
                                                         '%Y-%m-%dT%H:%M:%S')
    prevent_run_window_end_time_et = datetime.strptime(service["schedule"]["prevent_run_window_end_time_et"],
                                                       '%Y-%m-%dT%H:%M:%S')
    prevent_run_window_start_time_et = eastern_tz.localize(prevent_run_window_start_time_et)
    prevent_run_window_end_time_et = eastern_tz.localize(prevent_run_window_end_time_et)

    # This means that we got a Rerun command without the schedule being expired which can happen
    # if an admin updates the database table. We have to honor that so resetting end time
    if prevent_run_window_start_time_et < current_datetime < prevent_run_window_end_time_et:
        service["schedule"]["prevent_run_window_end_hour_et_original"] = \
            service["schedule"]["prevent_run_window_end_hour_et"]

        service["schedule"]["prevent_run_window_end_hour_et"] = service["schedule"]["prevent_run_window_start_hour_et"]
        service["schedule"]["override_comment"] = \
            "An rerun event was received even though the end time in configuration had not expired."
