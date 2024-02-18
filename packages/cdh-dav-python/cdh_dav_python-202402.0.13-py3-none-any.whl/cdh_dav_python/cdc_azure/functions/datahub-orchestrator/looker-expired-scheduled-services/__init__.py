import datetime
import json
import logging

import cdc_azure.functions as func

from shared_code import (
    app_config,
    storage_queue_helper,
    app_utils,
    workflow_state_store_helper,
)

SERVICE_NAME: str = "LOOKER_EXPIRED_SCHEDULED_SERVICES"


def main(mytimer: func.TimerRequest) -> None:
    utc_timestamp = (
        datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).isoformat()
    )
    logging.info(f"[{SERVICE_NAME}] Service running now at %s", utc_timestamp)
    logging.info(f"[{SERVICE_NAME}] Processing expired scheduled services ")
    process_all_expired_schedule_services()
    logging.info(f"[{SERVICE_NAME}] Finished processing expired scheduled services ")


def process_all_expired_schedule_services():
    try:
        results = workflow_state_store_helper.get_expired_scheduled_services()
        now = app_utils.utc_now_formatted()
        for result in results:
            try:
                workflow_id = result["workflow_id"]
                request_id = result["request_id"]
                data_source = result["data_source"]
                job_payload = {
                    "data_source": "{data_source}",
                    "workflow_id": "{workflow_id}",
                    "request_id": "{request_id}",
                    "event_source": "looker-expired-scheduled-svc",
                    "event_time_utc": "{event_time_utc}",
                    "status": "{status}",
                }

                job_payload = (
                    json.dumps(job_payload)
                    .replace("{request_id}", request_id)
                    .replace("{workflow_id}", workflow_id)
                    .replace("{data_source}", data_source)
                    .replace("{status}", app_config.WORKFLOW_STATUS_RERUN)
                    .replace("{event_time_utc}", now)
                )

                storage_queue_helper.send_message_to_queue(
                    queue_name=app_config.QUEUE_ORCHESTRATOR_UPDATE_NAME,
                    message=job_payload,
                )

            except Exception as ex:
                logging.error(
                    f"[Looker Service] process_all_expired_schedule_services: \n"
                    f"workflow_id: {workflow_id} \n"
                    f"request_id: {request_id} \n"
                    f"data_source: {data_source} \n"
                    f" {str(ex)}"
                )
    except Exception as ex:
        logging.error(
            f"[Looker Service] process_all_expired_schedule_services: {str(ex)}"
        )


if __name__ == "__main__":
    process_all_expired_schedule_services()
