import base64
import datetime
import json
import os

import requests
from flask import Blueprint, current_app
from flask import render_template, request

from shared_code import aad_helper, session_helper, config_file_helper

approval_page = Blueprint('approval_page', __name__,
                          template_folder='templates')


@approval_page.route('/workflow-confirm/<params>', methods=("GET", "POST"))
def workflow_confirm(params: str):
    name, email = aad_helper.get_name_and_email_address()
    full_name = f"{name} - {email}"
    session_helper.set_session_variables()
    if request.method == 'GET':
        try:
            query = base64.b64decode(params)
            query_json = json.loads(query)

            data_source = query_json['data_source']
            workflow_id = query_json['workflow_id']
            request_id = query_json['request_id']

            file_name = f"{data_source}_{workflow_id}.json"
            service_still_pending_approval = config_file_helper.is_service_still_pending_approval \
                (file_name=file_name, workflow_id=workflow_id, request_id=request_id, data_source=data_source)
            if not service_still_pending_approval:
                return render_template('_shared/result.html',
                                       message=f"Could not find the relevant workflow(or service) for '{data_source}'."
                                               f"The workflow may have been approved or rejected already.",
                                       trace=f"Trace : Workflow # {workflow_id} | Request # {request_id}",
                                       category="danger")

            return render_template('workflow/confirm.html',
                                   data_source=data_source,
                                   workflow_id=workflow_id,
                                   request_id=request_id,
                                   approver=full_name)
        except Exception as ex:
            return render_template('_shared/result.html',
                                   message="Oops - either the link is incorrect or something bad happened",
                                   trace=str(ex),
                                   category="danger")

    else:
        try:
            data_source = request.form['data_source']
            workflow_id = request.form['workflow_id']
            request_id = request.form['request_id']
            action = request.form['action']
            justification = request.form['justification']
            datetime_now_utc = datetime.datetime.now(tz=datetime.timezone.utc)
            now = datetime_now_utc.strftime('%Y-%m-%dT%H:%M:%SZ')

            status = "Succeeded" if action.casefold() == "approve" else "Rejected"

            json_load = {
                "data_source": data_source,
                "workflow_id": workflow_id,
                "request_id": request_id,
                "event_source": "approver-svc",
                "action": action,
                "justification": justification,
                "user": full_name,
                "status": status,
                "event_time_utc": now,
            }
            url = os.getenv("EVENT_STATUS_PUBLISHER_FUNC_URL")

            response = requests.post(url, data=json.dumps(json_load))
            # https://stackoverflow.com/questions/71639448/is-there-a-way-to-use-bootstrap-toast-in-flask-flashing-natively
            response_text = f"Your action of '{action}' was successfully recorded."
            response_status = "success"
            if not response.ok:
                print(response.text)
                response_text = f"Something went wrong. Please contact support. Error: {response.text}"
                response_status = "danger"

            # send email saying that workflow has been approved
            # check for workflow status in databricks - request id status should be "PendingApproval"
            return render_template('_shared/result.html',
                                   message=response_text,
                                   category=response_status)
        except Exception as ex:
            current_app.logger.error(f"Error : {str(ex)}")
            return render_template('_shared/result.html',
                                   message="Oops - unhandled error occurred",
                                   trace=str(ex),
                                   category="danger")
