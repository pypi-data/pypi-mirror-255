import json
from datetime import datetime, date

from flask import Blueprint, current_app
from flask import render_template, request

from shared_code import (
    datalake_helper,
    session_helper,
    config_file_helper,
    sql_helper,
    app_config,
    storage_queue_helper,
    aad_helper,
)

workflow_status_page = Blueprint(
    "workflow_status", __name__, template_folder="templates"
)


@workflow_status_page.route("/workflow-status/<data_source>", methods=["GET"])
def workflow_status(data_source: str):
    """
    Retrieves the workflow status based on the provided data source.

    Args:
        data_source (str): The data source for which to retrieve the workflow status.

    Returns:
        The rendered template for displaying the workflow status.

    Raises:
        Exception: If an unhandled error occurs during the process.
    """

    try:
        session_helper.set_session_variables()
        mode = request.args.get("mode")
        workflow_id = request.args.get("workflow_id")
        file_name = request.args.get("file_name")
        config_json = ""
        path = "work/datahub/inprogress"
        if mode.casefold() == "completed":
            path = f"work/datahub/completed/{data_source}"
        if workflow_id is not None and len(workflow_id) > 0:
            config_json = datalake_helper.get_json_file(
                file_system=path, file_name=f"{data_source}_{workflow_id}.json"
            )
        elif file_name is not None and len(file_name) > 0:
            config_json = datalake_helper.get_json_file(
                file_system=path, file_name=file_name
            )

        return render_template(
            "workflow/status.html", config_json=config_json, mode=mode
        )
    except Exception as ex:
        current_app.logger.error(f"Error : {str(ex)}")
        return render_template(
            "_shared/result.html",
            message="Oops - unhandled error occurred",
            trace=str(ex),
            category="danger",
        )


@workflow_status_page.route("/workflow-running", methods=["GET"])
def workflow_running():
    try:
        session_helper.set_session_variables()
        files = config_file_helper.get_all_running_etls_v2()

        return render_template("workflow/running.html", files=files)
    except Exception as ex:
        current_app.logger.error(f"Error : {str(ex)}")
        return render_template(
            "_shared/result.html",
            message="Oops - unhandled error occurred",
            trace=str(ex),
            category="danger",
        )


@workflow_status_page.route("/workflow-completed-summary", methods=["GET"])
def workflow_completed_summary():
    try:
        session_helper.set_session_variables()
        files = sql_helper.get_completed_workflows()

        return render_template("workflow/completed-summary.html", files=files)
    except Exception as ex:
        current_app.logger.error(f"Error : {str(ex)}")
        return render_template(
            "_shared/result.html",
            message="Oops - unhandled error occurred",
            trace=str(ex),
            category="danger",
        )


@workflow_status_page.route("/workflow-completed/<data_source>", methods=["GET"])
def workflow_completed(data_source: str):
    try:
        session_helper.set_session_variables()
        files = sql_helper.get_completed_workflows_by_data_source(data_source)

        return render_template("workflow/completed.html", files=files)
    except Exception as ex:
        current_app.logger.error(f"Error : {str(ex)}")
        return render_template(
            "_shared/result.html",
            message="Oops - unhandled error occurred",
            trace=str(ex),
            category="danger",
        )


@workflow_status_page.route("/workflow-trigger", methods=("GET", "POST"))
def workflow_trigger():
    try:
        session_helper.set_session_variables()
        name, email = aad_helper.get_name_and_email_address()
        can_user_trigger_workflow = aad_helper.is_user_an_admin(email, "")
        if not can_user_trigger_workflow:
            return render_template(
                "_shared/result.html",
                message=f"Permission denied to trigger workflows for '{email}'. Please contact DDPHSSCSELSDHISPEBcdhengineering@cdc.gov for assistance.",
                category="danger",
            )

        datasets = config_file_helper.get_all_configured_dataasets()
        data_source = ""
        delivery_date = date.today()
        vendor_delivery_location = ""
        is_delivery_date_valid_to_process = True
        is_workflow_already_running = False
        workflow_successfully_started = False

        if request.method == "POST":
            data_source = request.form["data_source"]
            delivery_date = request.form["delivery_date"]
            delivery_date_formatted = datetime.strptime(
                delivery_date, "%Y-%m-%d"
            ).strftime("%Y%m%d")
            vendor_delivery_location = request.form["vendor_delivery_location"]

            is_delivery_date_valid_to_process = (
                sql_helper.is_delivery_date_valid_to_process(
                    data_source=data_source, delivery_date=delivery_date_formatted
                )
            )

            is_workflow_already_running = (
                config_file_helper.is_workflow_already_running_for_data_source(
                    data_source
                )
            )

            if is_delivery_date_valid_to_process and not is_workflow_already_running:
                json_load = {
                    "data_source": data_source,
                    "delivery_date": delivery_date_formatted,
                    "vendor_delivery_location": vendor_delivery_location,
                    "triggerred_by": email,
                }
                storage_queue_helper.send_message_to_queue(
                    queue_name=app_config.QUEUE_ORCHESTRATOR_START_NAME,
                    message=json.dumps(json_load),
                )
                workflow_successfully_started = True

        return render_template(
            "workflow/trigger.html",
            datasets=datasets,
            data_source=data_source,
            delivery_date=delivery_date,
            vendor_delivery_location=vendor_delivery_location,
            is_delivery_date_valid_to_process=is_delivery_date_valid_to_process,
            is_workflow_already_running=is_workflow_already_running,
            workflow_successfully_started=workflow_successfully_started,
        )
    except Exception as ex:
        current_app.logger.error(f"Error : {str(ex)}")
        return render_template(
            "_shared/result.html",
            message="Oops - unhandled error occurred",
            trace=str(ex),
            category="danger",
        )
