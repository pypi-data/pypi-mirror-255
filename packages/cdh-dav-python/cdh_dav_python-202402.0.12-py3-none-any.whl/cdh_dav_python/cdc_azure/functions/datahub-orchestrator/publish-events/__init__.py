import json
import logging

import cdc_azure.functions as func

from shared_code import storage_queue_helper, app_config


def main(req: func.HttpRequest) -> func.HttpResponse:
    message = req.get_body()
    logging.info(f"[Publish Events Service] received request: {message}")
    try:
        msg_body = req.get_json()
        message = json.dumps(msg_body)
        storage_queue_helper.send_message_to_queue(
            queue_name=app_config.QUEUE_ORCHESTRATOR_UPDATE_NAME, message=message
        )
    except Exception as ex:
        logging.error(
            f"[Publish Events Service] Error processing message {msg_body}. \n \n error: "
            + str(ex)
        )
        return func.HttpResponse(str(ex), status_code=500)

    return func.HttpResponse(
        json.dumps({"status": "success"}),
        status_code=200,
        headers={"content-type": "text/json"},
    )
