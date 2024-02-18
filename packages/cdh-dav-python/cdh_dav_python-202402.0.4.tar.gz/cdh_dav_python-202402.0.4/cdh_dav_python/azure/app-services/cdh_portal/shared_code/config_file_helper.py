import json
import os
from datetime import datetime, timedelta, timezone

import pytz
from ago import human
from ago import delta2dict

from shared_code import datalake_helper, app_config, sql_helper


def is_service_still_pending_approval(data_source: str, workflow_id: str, request_id: str, file_name: str):
    # file_name = f"{data_source}_{workflow_id}.json"
    if not datalake_helper.does_file_exist(file_system=app_config.WORKFLOW_IN_PROGRESS_DIRECTORY,
                                           file_name=file_name):
        return False

    config_json = datalake_helper.get_json_file(file_system=app_config.WORKFLOW_IN_PROGRESS_DIRECTORY,
                                                file_name=file_name)

    service_status = __get_service_status(config_json=config_json, request_id=request_id)

    if service_status is None:
        return False

    if service_status.casefold() == app_config.WORKFLOW_STATUS_PENDING_APPROVAL.casefold():
        return True

    return False


def __get_service_status(config_json: any, request_id: str) -> str | None:
    services = config_json["services"]
    for service in services:
        if service.get("tracking") is not None:
            if service["tracking"].get("request_id") is not None and service["tracking"]["request_id"] == request_id:
                return service["tracking"]["status"]

    return None


def get_all_configured_dataasets():
    all_files = datalake_helper.get_all_files_in_directory("metadata/datahub/configs")
    file_names = []
    for a_file in all_files:
        file_name = os.path.basename(a_file)
        file_name = file_name.replace("_datahub_config.json", "")
        file_names.append(file_name)

    file_names.sort()
    return file_names


def get_all_running_etls():
    all_files = datalake_helper.get_all_files_in_directory("work/datahub/inprogress/")
    results = []
    for a_file in all_files:
        file_name = os.path.basename(a_file)
        try:
            config_json = datalake_helper.get_json_file(file_system="work/datahub/inprogress",
                                                        file_name=file_name)
            completed_services = []
            pending_services = []
            current_service = ""
            for service in config_json["services"]:
                service_name = service["display_name"]
                if service.get("tracking") is not None:
                    status = service["tracking"]["status"]
                    if status.casefold() == "running" or status.casefold() == "failed" or status.casefold().startswith(
                            "pending"):
                        current_service = service_name
                        start_utc = datetime.strptime(service["tracking"]["start_utc"], "%Y-%m-%dT%H:%M:%SZ")
                        if service["tracking"].get("end_utc") is not None:
                            end_utc = datetime.strptime(service["tracking"]["end_utc"], "%Y-%m-%dT%H:%M:%SZ")
                        else:
                            end_utc = datetime.utcnow()
                        delta_time = end_utc - start_utc
                        # total_time = str(timedelta(seconds=delta_time.total_seconds()))
                        total_time = human(delta_time, 1)
                    else:
                        completed_services.append("- " + service_name)
                else:
                    status = "Pending"
                    pending_services.append("- " + service_name)

            start_utc = datetime.strptime(config_json["tracking"]["start_utc"], "%Y-%m-%dT%H:%M:%SZ")
            delta_time = datetime.utcnow() - start_utc
            time_taken = human(delta_time, 1)  # str(timedelta(seconds=delta_time.total_seconds()))

            data_source = config_json["datasource"]
            workflow_id = config_json["workflow_id"]
            metadata = {
                "data_source": data_source,
                "workflow_id": workflow_id,
                "file_name": file_name,
                "detail_url": f"workflow-status/{data_source}?file_name={file_name}&mode=inprogress",
                "delivery_type": config_json["delivery_type"],
                "target_database": config_json["target_database"],
                "start_utc": config_json["tracking"]["start_utc"],
                "time_taken": time_taken,
                # "end_utc": config_json["tracking"]["end_utc"],
                "pending_services": "<br/>".join(pending_services),
                "completed_services": "<br/>".join(completed_services),
                "current_service": current_service,
                "current_service_time_taken": total_time
            }

            results.append(metadata)
        except Exception as ex:
            print(f"Exception occurred when processing: {file_name}. {str(ex)}")

    return results


def get_all_running_etls_v2():
    all_files = datalake_helper.get_all_files_in_directory("work/datahub/inprogress/")
    results = []
    file_to_workflow_id_map = {}
    for a_file in all_files:
        file_name = os.path.basename(a_file)
        cleaned_file_name = file_name.replace("_Failed", "").replace(".json", "")
        workflow_id = cleaned_file_name.split("_")[-1]
        file_to_workflow_id_map[workflow_id] = file_name

    workflow_ids = []
    for id in file_to_workflow_id_map.keys():
        workflow_ids.append(f"'{id}'")

    if len(workflow_ids) > 0:
        db_results = sql_helper.get_running_workflows(",".join(workflow_ids))

        for workflow_id in file_to_workflow_id_map.keys():
            has_metadata_db_row = False
            try:
                completed_services = []
                for result in db_results:
                    r_workflow_id = result["workflow_id"]
                    if r_workflow_id == workflow_id:
                        has_metadata_db_row = True
                        data_source = result["dataset_name"]
                        file_name = file_to_workflow_id_map[workflow_id]
                        status = result["tracking_status"]
                        workflow_start_utc = result["workflow_start_utc"]
                        if status.casefold() == "running" or status.casefold() == "failed" or status.casefold().startswith(
                                "pending"):
                            current_service = result["display_name"]
                            start_utc = result["tracking_start_utc"]
                            end_utc = datetime.utcnow().replace(tzinfo=pytz.utc)
                            delta_time = end_utc - start_utc
                            total_time = human(delta_time, 1)
                            current_service_status = result["tracking_status"]
                        else:
                            completed_services.append("- " + result["display_name"])

                        start_utc = workflow_start_utc
                        delta_time = datetime.utcnow().replace(tzinfo=pytz.utc) - start_utc
                        time_taken = human(delta_time, 1)  # str(timedelta(seconds=delta_time.total_seconds()))

                if has_metadata_db_row:
                    metadata = {
                        "data_source": data_source,
                        "workflow_id": workflow_id,

                        "file_name": file_to_workflow_id_map[workflow_id],
                        "detail_url": f"workflow-status/{data_source}?file_name={file_name}&mode=inprogress",
                        "delivery_type": "",
                        "target_database": "",
                        "start_utc": result["tracking_start_utc"],
                        "time_taken": time_taken,
                        # "end_utc": config_json["tracking"]["end_utc"],
                        # "pending_services": "<br/>".join(pending_services),
                        "completed_services": "<br/>".join(completed_services),
                        "current_service": current_service,
                        "current_service_time_taken": total_time,
                        "current_service_status": current_service_status,
                    }

                    results.append(metadata)
            except:
                print(f"Error when processing {workflow_id}")

    return results


def is_workflow_already_running_for_data_source(data_source):
    all_files = datalake_helper.get_all_files_in_directory(app_config.WORKFLOW_IN_PROGRESS_DIRECTORY)
    for a_file in all_files:
        if data_source.casefold() in a_file:
            return True

    return False
