import json
import uuid

from shared_code import config_file_helper, app_config, app_utils, datalake_helper, email_helper, \
    workflow_state_store_helper


def process(data_source: str, workflow_id: str, request_id: str,
            status: str, file_name: str, event_time_utc: str):
    config_json = datalake_helper.get_json_file(file_system=app_config.WORKFLOW_IN_PROGRESS_DIRECTORY,
                                                file_name=file_name)
    delivery_date = config_json["delivery_date"]
    delivery_type = config_json["delivery_type"]
    vendor_delivery_location = ""
    if config_json.get("vendor_delivery_location") is not None:
        vendor_delivery_location = config_json["vendor_delivery_location"]

    target_database = ""
    if config_json.get("target_database") is not None:
        target_database = config_json["target_database"]

    data_manager_email = config_json["data_manager_email"]

    current_service = config_file_helper.update_service_status_by_request_id(config_json=config_json,
                                                                             request_id=request_id,
                                                                             status=status,
                                                                             event_time_utc=event_time_utc)

    datalake_helper.save_file(data=json.dumps(config_json), file_system=app_config.WORKFLOW_IN_PROGRESS_DIRECTORY,
                              file_name=file_name)

    completed_dir = f"{app_config.WORKFLOW_COMPLETED_DIRECTORY}/{data_source}"
    workflow_files_from_dir = f"{app_config.WORKFLOW_IN_PROGRESS_DIRECTORY}/{workflow_id}"
    workflow_files_to_dir = f"{completed_dir}/{workflow_id}"

    if status.casefold() != app_config.WORKFLOW_STATUS_SUCCEEDED.casefold() \
            and status.casefold() != app_config.WORKFLOW_STATUS_RERUN.casefold() \
            and status.casefold() != app_config.WORKFLOW_STATUS_PENDING_APPROVAL.casefold():
        config_json["tracking"]["status"] = status
        config_json["tracking"]["end_utc"] = app_utils.utc_now_formatted()
        new_file_name = f"{data_source}_{workflow_id}_{status}.json" \
            if status.casefold() != app_config.WORKFLOW_STATUS_REJECTED.casefold() \
            else f"{data_source}_{workflow_id}.json"

        datalake_helper.save_file(data=json.dumps(config_json), file_system=app_config.WORKFLOW_IN_PROGRESS_DIRECTORY
                                  , file_name=file_name)

        if status.lower() != "rejected":
            datalake_helper.rename_file(file_system=app_config.WORKFLOW_IN_PROGRESS_DIRECTORY
                                        , file_name=file_name, new_name=new_file_name)
        else:
            datalake_helper.rename_file(file_system=app_config.WORKFLOW_IN_PROGRESS_DIRECTORY
                                        , file_name=file_name, new_name=file_name, new_path=completed_dir)

            datalake_helper.move_directory(old_dir_name=workflow_files_from_dir, new_dir_name=workflow_files_to_dir)

        workflow_state_store_helper.upsert_workflow_status(
            data_source=data_source, workflow_id=workflow_id, delivery_date=delivery_date,
            config_json=config_json
        )
        email_helper.send_workflow_status_email(config_json)
        return

    if status.casefold() == app_config.WORKFLOW_STATUS_PENDING_APPROVAL.casefold():
        workflow_state_store_helper.upsert_workflow_status(
            data_source=data_source, workflow_id=workflow_id, delivery_date=delivery_date,
            config_json=config_json
        )
        return

    # get next service
    next_request_id = uuid.uuid4().hex
    next_service = config_file_helper.get_next_unprocessed_service(config_json=config_json, request_id=next_request_id)
    if next_service is None:
        config_json["tracking"]["status"] = status
        config_json["tracking"]["end_utc"] = app_utils.utc_now_formatted()

        datalake_helper.save_file(data=json.dumps(config_json), file_system=app_config.WORKFLOW_IN_PROGRESS_DIRECTORY
                                  , file_name=file_name)

        datalake_helper.rename_file(file_system=app_config.WORKFLOW_IN_PROGRESS_DIRECTORY
                                    , file_name=file_name, new_name=file_name, new_path=completed_dir)

        datalake_helper.move_directory(old_dir_name=workflow_files_from_dir, new_dir_name=workflow_files_to_dir)

        workflow_state_store_helper.upsert_workflow_status(
            data_source=data_source, workflow_id=workflow_id, delivery_date=delivery_date,
            config_json=config_json
        )
        email_helper.send_workflow_status_email(config_json)
    else:
        next_request_id = next_service["tracking"]["request_id"]
        config_file_helper.invoke_next_service(service=next_service,
                                               data_source=data_source,
                                               delivery_date=delivery_date,
                                               workflow_id=workflow_id,
                                               request_id=next_request_id,
                                               delivery_type=delivery_type,
                                               data_manager_email=data_manager_email,
                                               vendor_delivery_location=vendor_delivery_location,
                                               target_database=target_database
                                               )

        datalake_helper.save_file(data=json.dumps(config_json), file_system=app_config.WORKFLOW_IN_PROGRESS_DIRECTORY
                                  , file_name=file_name)

        workflow_state_store_helper.upsert_workflow_status(
            data_source=data_source, workflow_id=workflow_id, delivery_date=delivery_date,
            config_json=config_json
        )
