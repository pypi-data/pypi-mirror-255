import datetime
import json
import logging
import os
import uuid

import cdc_azure.functions as func

from handlers import update_workflow_handler
from shared_code import (
    datalake_helper,
    app_config,
    storage_queue_helper,
    app_utils,
    duplication_check_helper,
    email_helper,
    workflow_state_store_helper,
)

SERVICE_NAME: str = "LOOKER_SERVICE"


def main(mytimer: func.TimerRequest) -> None:
    utc_timestamp = (
        datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).isoformat()
    )
    logging.info(f"[{SERVICE_NAME}] Service running now at %s", utc_timestamp)
    logging.info(f"[{SERVICE_NAME}] Processing ready files ")
    process_all_ready_files()
    logging.info(f"[{SERVICE_NAME}] Finished processing ready files ")


def process_all_ready_files():
    sub_directory = "landing/datahub/ready_drop/"
    success_directory = "landing/datahub/ready_pickedup_success/"
    failure_directory = "landing/datahub/ready_pickedup_failed/"

    # move success files to a directory along with workflow id

    blob_list = datalake_helper.get_all_ready_files(sub_directory=sub_directory)
    for blob in blob_list:
        workflow_id = uuid.uuid4().hex
        if blob.name.casefold() != sub_directory.casefold():
            try:
                logging.info(f"[{SERVICE_NAME}] processing file {blob.name}")
                file_name = os.path.basename(blob.name)
                if file_name.casefold().endswith("_ready.json"):
                    blob_md5_hash = app_utils.decode_byte_array(
                        blob.content_settings.content_md5
                    )
                    ready_file_json = datalake_helper.get_json_file(
                        file_system=sub_directory, file_name=file_name
                    )
                    validate_file_data(file_name, ready_file_json, blob_md5_hash)

                    ready_file_json["workflow_id"] = workflow_id
                    message = json.dumps(ready_file_json)
                    logging.info(
                        f"[{SERVICE_NAME}] Sending start event  {message} for starting workflow "
                    )

                    storage_queue_helper.send_message_to_queue(
                        queue_name=app_config.QUEUE_ORCHESTRATOR_START_NAME,
                        message=message,
                    )

                    new_file_name = app_utils.get_unique_file_name_from_file_name(
                        file_name=file_name
                    )
                    datalake_helper.save_file(
                        data=message,
                        file_name=new_file_name,
                        file_system=success_directory,
                    )

                    datalake_helper.delete_file(
                        account_url=app_config.EDAV_STORAGE_CDH_CONTAINER_URL,
                        file_system=sub_directory,
                        file_name=file_name,
                    )
                else:
                    logging.info(
                        f"[{SERVICE_NAME}] not processing file {blob.name} since its not named in correct format."
                    )
                    error_text = "Error:  Not named in correct format. Must end with _ready and must be of type json."
                    add_error_text_and_save(
                        ready_dir=sub_directory,
                        org_file_name=file_name,
                        failure_dir=failure_directory,
                        error_text=error_text,
                    )
            except ValueError as ex:
                logging.error(ex)
                error_text = str(ex)
                add_error_text_and_save(
                    ready_dir=sub_directory,
                    org_file_name=file_name,
                    failure_dir=failure_directory,
                    error_text=error_text,
                )
            except Exception as ex:
                logging.error(ex)
                error_text = "[Uncaught error]. " + str(ex)
                add_error_text_and_save(
                    ready_dir=sub_directory,
                    org_file_name=file_name,
                    failure_dir=failure_directory,
                    error_text=error_text,
                )


def validate_file_data(file_name: str, ready_file_json, blob_md5_hash):
    data_source = ready_file_json["data_source"]

    config_file_name = f"{data_source.strip()}{app_config.DATAHUB_CONFIGS_FILE_SUFFIX}"
    exists_config_file = datalake_helper.does_file_exist(
        file_system=app_config.DATAHUB_CONFIGS_LOCATION, file_name=config_file_name
    )
    if not exists_config_file:
        raise ValueError(
            f"invalid data source in input file. Cannot find configuration file {config_file_name}"
        )

    file_processed_already, duplicate_file_name = (
        duplication_check_helper.has_file_been_processed_already(
            file_name=file_name, md5_hash=blob_md5_hash, data_source=data_source
        )
    )
    if file_processed_already:
        raise ValueError(
            f"File has been processed already based on the hash {blob_md5_hash} in file {duplicate_file_name}"
        )

    # if delivery date is not present, make it today for download purpose.
    # todo : may still need to know how to calculate the date if vendor does not send date information
    if ready_file_json.get("delivery_date") is None:
        ready_file_json["delivery_date"] = app_utils.utc_now_formatted_ymd()


def add_error_text_and_save(
    ready_dir: str, org_file_name: str, failure_dir: str, error_text: str
):
    email_helper.send_looker_fail_email(file_name=org_file_name, error_text=error_text)
    file_text = datalake_helper.get_file_text(
        file_system=ready_dir, file_name=org_file_name
    )
    file_text = file_text + "\n" + error_text
    new_file_name = app_utils.get_unique_file_name_from_file_name(
        file_name=org_file_name
    )
    datalake_helper.save_file(
        data=file_text, file_name=new_file_name, file_system=failure_dir
    )
    datalake_helper.delete_file(
        account_url=app_config.EDAV_STORAGE_CDH_CONTAINER_URL,
        file_system=ready_dir,
        file_name=org_file_name,
    )


if __name__ == "__main__":
    #     process_all_expired_schedule_services()
    update_workflow_handler.process(
        data_source="demo_integration_test",
        workflow_id="11879bd5de2f4766a4f4fba070c0c7d4",
        request_id="a4acbaf0950741e382d0950d2587e47a",
        status="succeeded",
        file_name="demo_integration_test_11879bd5de2f4766a4f4fba070c0c7d4.json",
        event_time_utc=app_utils.utc_now_formatted(),
    )
