# Databricks notebook source
dbutils.widgets.text("data_source", "")
dbutils.widgets.text("delivery_date", "")
dbutils.widgets.text("request_id", "ISOLATED")
dbutils.widgets.text("workflow_id", "ISOLATED")
dbutils.widgets.text("storage_account_name", "")
dbutils.widgets.text("source_folder", "")
dbutils.widgets.text("manifest_file_folder", "")
dbutils.widgets.text("manifest_file", "")
dbutils.widgets.text("manifest_file_level_2", "")
dbutils.widgets.text("email_to", "")
dbutils.widgets.text("adjust_metrics_range", "False")
dbutils.widgets.dropdown(
    "validation_mode",
    "vendor_specific",
    ["vendor_specific", "vendor_common", "skip_validation"],
)
dbutils.widgets.dropdown(
    "send_email_mode", "on_needs_review", ["always", "on_needs_review"]
)

# COMMAND ----------

from multiprocessing.pool import ThreadPool
import multiprocessing as mp

# from pyspark.sql.functions import *
from pyspark.sql.types import *
import os
import json
import base64
import requests
import time
import pandas as pd
from datetime import datetime, timezone

import cdc_azure.databricks.etl.shared.cdh_helper as cdh_helper
import cdc_azure.databricks.etl.shared.data_load_helper as data_load_helper
from cdc_azure.databricks.etl.shared import constants


# COMMAND ----------

data_source = dbutils.widgets.get("data_source")
delivery_date = dbutils.widgets.get("delivery_date")
request_id = dbutils.widgets.get("request_id")
workflow_id = dbutils.widgets.get("workflow_id")
storage_account_name = dbutils.widgets.get("storage_account_name")
source_folder = dbutils.widgets.get("source_folder")
manifest_file_folder = dbutils.widgets.get("manifest_file_folder")
manifest_file = dbutils.widgets.get("manifest_file")
manifest_file_level_2 = dbutils.widgets.get("manifest_file_level_2")
email_to = dbutils.widgets.get("email_to")
adjust_metrics_range = bool(dbutils.widgets.get("adjust_metrics_range"))
validation_mode = dbutils.widgets.get("validation_mode")
send_email_mode = dbutils.widgets.get("send_email_mode")

app_environment = cdh_helper.get_app_environment()
email_service_url = cdh_helper.get_notification_service_url()


base_path = f"abfss://cdh@{storage_account_name}.dfs.core.windows.net/"
canonical_validation_file_name = (
    f"{data_source}_{delivery_date}_validation_metadata.txt"
)
manifest_file_folder_full_path = os.path.join(base_path, manifest_file_folder)
vendor_canonical_level_1_path = os.path.join(
    base_path, manifest_file_folder, manifest_file
)
vendor_canonical_level_2_path = os.path.join(
    base_path, manifest_file_folder, manifest_file_level_2
)
output_file_directory = os.path.join(
    base_path, f"work/datahub/completed/{data_source}/{workflow_id}/misc"
)
canonical_validation_output_directory = os.path.join(
    output_file_directory, canonical_validation_file_name
)
ge_nb_params_json = {
    "data_source": data_source,
    "delivery_date": delivery_date,
    "source_folder": source_folder,
    "manifest_file_path": canonical_validation_output_directory,
    "storage_account_name": storage_account_name,
    "workflow_id": workflow_id,
    "adjust_metrics_range": adjust_metrics_range,
}

ge_nb_output = ""
print(canonical_validation_output_directory)
print(ge_nb_params_json)

# COMMAND ----------


def spark_setup():
    cdh_helper.secure_connect_spark_adls()


# COMMAND ----------


def safe_cast(val, to_type, default=None):
    try:
        return to_type(val)
    except (ValueError, TypeError):
        return default


# COMMAND ----------

# Vendor,DataElement,DataObject,Metric,MetricValue
canonical_df_schema = StructType(
    [
        StructField("data_source", StringType(), False),
        StructField("data_object", StringType(), False),
        StructField("data_element", StringType(), False),
        StructField("metric", StringType(), False),
        StructField("metric_value", StringType(), False),
    ]
)
emptyRDD = spark.sparkContext.emptyRDD()
canonical_df = spark.createDataFrame(emptyRDD, canonical_df_schema)
display(canonical_df)

# COMMAND ----------


def process_vendor_specific():
    if data_source.casefold() == "premier":
        canonical_df = process_premier()
    elif data_source.casefold() == "pointclickcare":
        canonical_df = process_pointclickcare()
    else:
        raise Exception(f"no transformation exists for source {data_source}")

    dest_path_temp = base_path + f"raw/{data_source}/{delivery_date}-temp/manifest/"
    dbutils.fs.rm(dest_path_temp, True)
    canonical_df.coalesce(1).write.mode("overwrite").option("header", True).csv(
        dest_path_temp
    )
    csv_file = cdh_helper.get_first_file_in_directory(dest_path_temp, ".csv")
    dbutils.fs.mv(csv_file, canonical_validation_output_directory)
    return canonical_df


def process_premier():
    file_paths = cdh_helper.get_specific_files_in_directory(
        manifest_file_folder_full_path, manifest_file
    )
    df = (
        spark.read.format("csv")
        .option("inferSchema", True)
        .option("header", True)
        .option("sep", "|")
        .load(file_paths)
    )

    result_array = {}
    canonical_df = spark.createDataFrame(emptyRDD, canonical_df_schema)
    for row in df.collect():
        table_name = row["TABLENAME"]
        row_count = str(row["ROWCOUNT"])
        if table_name in result_array.keys():
            info = int(result_array.get(table_name)) + int(row_count)
            result_array[table_name] = info
        else:
            result_array[table_name] = int(row_count)

    for key in result_array.keys():
        table_name = key
        metric_value = result_array.get(key)
        newRow = spark.createDataFrame(
            [(data_source, table_name, "", "total_count", metric_value)],
            canonical_df_schema,
        )
        canonical_df = canonical_df.union(newRow)

    # print(json.dumps(result_array))
    display(canonical_df)
    return canonical_df


def process_pointclickcare():
    file_paths = cdh_helper.get_specific_files_in_directory(
        manifest_file_folder_full_path, manifest_file, exact_match=False
    )
    df = (
        spark.read.format("csv")
        .option("inferSchema", True)
        .option("header", True)
        .option("sep", "|")
        .load(file_paths)
    )

    # display(df)
    canonical_df = spark.createDataFrame(emptyRDD, canonical_df_schema)
    result_array = {}
    average_metric_file_count_tracker = {}
    for row in df.collect():
        column_name = row["DataElement"]
        table_name = str(row["DataObject"]).split("_")[0]
        metric = row["Metric"]
        metric_value = row["MetricValue"]
        canonical_metric = (
            "max_value"
            if metric.casefold() == "maximumvalue"
            else (
                "min_value"
                if metric.casefold() == "minimumvalue"
                else (
                    "mean_value"
                    if metric.casefold() == "averagevalue"
                    else (
                        "total_count"
                        if metric.casefold() == "totalcount"
                        else (
                            "unique_value_count"
                            if metric.casefold() == "uniquecount"
                            else ""
                        )
                    )
                )
            )
        )
        temp_key = f"{table_name}*{column_name}*{canonical_metric}"
        # TODO : need to figure out what defaultvaluecount from PCC means
        if (
            metric.casefold()
            in [
                "uniquecount",
                "totalcount",
                "maximumvalue",
                "minimumvalue",
                "averagevalue",
            ]
            and safe_cast(metric_value, float) is not None
        ):
            if temp_key in result_array.keys():
                info = result_array.get(temp_key)
                if metric.casefold() in ["uniquecount", "totalcount"]:
                    info = str(float(info) + float(metric_value))
                elif metric.casefold() in ["maximumvalue"]:
                    info = str(max([float(info), float(metric_value)]))
                elif metric.casefold() in ["minimumvalue"]:
                    info = str(min([float(info), float(metric_value)]))
                elif metric.casefold() in ["averagevalue"]:
                    info = str(float(info) + float(metric_value))
                    avg_tracker_key = f"{table_name}*{column_name}"
                    if avg_tracker_key in average_metric_file_count_tracker.keys():
                        average_metric_file_count_tracker[avg_tracker_key] = (
                            int(average_metric_file_count_tracker.get(avg_tracker_key))
                            + 1
                        )
                    else:
                        average_metric_file_count_tracker[avg_tracker_key] = 1
                else:
                    info = "0"

                result_array[temp_key] = info

            else:
                result_array[temp_key] = metric_value
                if metric.casefold() in ["averagevalue"]:
                    avg_tracker_key = f"{table_name}*{column_name}"
                    average_metric_file_count_tracker[avg_tracker_key] = 1

    print(f"average_metric_file_count_tracker : {average_metric_file_count_tracker}")
    for key in result_array.keys():
        table_name = key.split("*")[0]
        column_name = key.split("*")[1]
        metric = key.split("*")[2]
        metric_value = result_array.get(key)
        column_name = column_name if metric.casefold() != "total_count" else ""
        metric_value = (
            result_array.get(key)
            if metric.casefold() != "mean_value"
            else float(result_array.get(key))
            / int(average_metric_file_count_tracker.get(f"{table_name}*{column_name}"))
        )

        newRow = spark.createDataFrame(
            [(data_source, table_name, column_name, metric, metric_value)],
            canonical_df_schema,
        )
        canonical_df = canonical_df.union(newRow)

    # print(json.dumps(result_array))
    display(canonical_df)

    return canonical_df


# COMMAND ----------


def process_vendor_common():
    canonical_df = spark.createDataFrame(emptyRDD, canonical_df_schema)

    # Reading in our dataset from ADLS
    file_paths = cdh_helper.get_specific_files_in_directory(
        manifest_file_folder_full_path, manifest_file
    )
    df_table_level = (
        spark.read.format("csv")
        .option("inferSchema", True)
        .option("header", True)
        .option("sep", ",")
        .load(file_paths)
    )

    display(df_table_level)

    file_paths = cdh_helper.get_specific_files_in_directory(
        manifest_file_folder_full_path, manifest_file_level_2
    )
    df_col_level = (
        spark.read.format("csv")
        .option("inferSchema", True)
        .option("header", True)
        .option("sep", ",")
        .load(file_paths)
    )

    display(df_col_level)

    for row in df_table_level.collect():
        newRow = spark.createDataFrame(
            [(data_source, row["table"], "", "total_count", row["table_row_counts"])],
            canonical_df_schema,
        )
        canonical_df = canonical_df.union(newRow)

    for row in df_col_level.collect():
        if row["max_value"] is not None and row["max_value"] != "":
            newRow = spark.createDataFrame(
                [
                    (
                        data_source,
                        row["table"],
                        row["column"],
                        "max_value",
                        row["max_value"],
                    )
                ],
                canonical_df_schema,
            )
            canonical_df = canonical_df.union(newRow)

        if row["min_value"] is not None and row["min_value"] != "":
            newRow = spark.createDataFrame(
                [
                    (
                        data_source,
                        row["table"],
                        row["column"],
                        "min_value",
                        row["min_value"],
                    )
                ],
                canonical_df_schema,
            )
            canonical_df = canonical_df.union(newRow)

        if row["unique_value_count"] is not None and row["unique_value_count"] != "":
            newRow = spark.createDataFrame(
                [
                    (
                        data_source,
                        row["table"],
                        row["column"],
                        "unique_value_count",
                        row["unique_value_count"],
                    )
                ],
                canonical_df_schema,
            )
            canonical_df = canonical_df.union(newRow)

        if row["mean_value"] is not None and row["mean_value"] != "":
            newRow = spark.createDataFrame(
                [
                    (
                        data_source,
                        row["table"],
                        row["column"],
                        "mean_value",
                        row["mean_value"],
                    )
                ],
                canonical_df_schema,
            )
            canonical_df = canonical_df.union(newRow)

    display(canonical_df)
    dest_path_temp = base_path + f"raw/{data_source}/{delivery_date}-temp/manifest/"
    dbutils.fs.rm(dest_path_temp, True)
    canonical_df.coalesce(1).write.mode("overwrite").option("header", True).csv(
        dest_path_temp
    )
    csv_file = cdh_helper.get_first_file_in_directory(dest_path_temp, ".csv")
    dbutils.fs.mv(csv_file, canonical_validation_output_directory)
    return canonical_df


# COMMAND ----------


def process_skip_validation():
    canonical_df = spark.createDataFrame(emptyRDD, canonical_df_schema)
    source_folder_location = base_path + source_folder
    tables = cdh_helper.get_first_level_subfolders(source_folder_location)

    for table in tables:
        source = os.path.join(source_folder_location, table)
        df = spark.read.format("parquet").load(source)
        row_count = df.count()
        newRow = spark.createDataFrame(
            [(data_source, table, "", "total_count", row_count)], canonical_df_schema
        )
        canonical_df = canonical_df.union(newRow)

    display(canonical_df)
    dest_path_temp = base_path + f"raw/{data_source}/{delivery_date}-temp/manifest/"
    dbutils.fs.rm(dest_path_temp, True)
    canonical_df.coalesce(1).write.mode("overwrite").option("header", True).csv(
        dest_path_temp
    )
    csv_file = cdh_helper.get_first_file_in_directory(dest_path_temp, ".csv")
    dbutils.fs.mv(csv_file, canonical_validation_output_directory)
    save_metadata_to_db(canonical_df)
    return canonical_df


# COMMAND ----------


def save_metadata_to_db(canonical_df):
    ingest_table = "cdh_engineering.cdm_ingest_metadata"
    time_now = datetime.now(tz=timezone.utc)

    spark.sql(
        f"DELETE from {ingest_table} where workflow_id= '{workflow_id}' and dataset_name='{data_source}'"
    )
    sql_header = f"""insert into {ingest_table}(workflow_id, dataset_name, table_name,column_name,  metric,metric_value, created_time) values \n"""
    sql_array = []
    for row in canonical_df.collect():
        table_name = row["data_object"]
        column_name = row["data_element"]
        metric = row["metric"]
        metric_value = row["metric_value"]
        sql_array.append(
            f" ('{workflow_id}', '{data_source}', '{table_name}','{column_name}','{metric}','{metric_value}', '{time_now}')"
        )

    sql = sql_header + ", \n".join(sql_array) + ";"
    print(sql)
    spark.sql(sql)


# COMMAND ----------

VALIDATION_EMAIL_TEMPLATE = """
<div>
    <h2>#DATA_SOURCE#</h2>
    <div style="text-align: center;padding-bottom: 0%;"><h4>Summary</h4></div>
    <table role="presentation" border="1" width="100%" style="border-collapse: collapse;
    margin: 25px 0;
    font-size: 1.0em;
    font-family: sans-serif;
    min-width: 400px;
    box-shadow: 0 0 20px rgba(0, 0, 0, 0.15)">
        
        <tr style=" background-color: #007fff;
                color: #ffffff;
                text-align: left;">
            <th style="padding: 12px 15px;">Status</th>     
            <th>Workflow</th>
            <th>Delivery Date</th>
            <th>Validation Mode</th>        
               
        </tr>
        <tr>
            <td>#STATUS#</td>
            <td>#WORKFLOW_ID#</td>
            <td>#DELIVERY_DATE#</td>
            <td>#VALIDATION_MODE#</td>
            
        </tr>
</table>    

<br/><br/>
<div style="text-align: center;padding-bottom: 0%;"><h4>Result</h4></div>
<table role="presentation" border="1" width="100%" style="border-collapse: collapse;
                            margin: 25px 0;
                            font-size: 1.0em;
                            font-family: sans-serif;
                            min-width: 400px;
                            box-shadow: 0 0 20px rgba(0, 0, 0, 0.15)">
  <tr style=" background-color: #007fff;
        color: #ffffff;
        text-align: left;">
    <th style="padding: 12px 15px;">Table</th>
    <th>Tests (Total | Success | Failed)</th>
    <th>Detail</th>
  </tr>
  #BODY#
</table>

</div>
"""


def send_validation_email(ge_nb_output_body):
    validation_needs_review = False
    html_template = VALIDATION_EMAIL_TEMPLATE
    html_body = ""
    stripe_row = False
    for element in ge_nb_output_body:
        table_name = element["table_name"]
        if table_name != "_summary":
            success_percent = int(element["statistics"]["success_percent"])
            evaluated_tests = element["statistics"]["evaluated_tests"]
            successful_tests = element["statistics"]["successful_tests"]
            unsuccessful_tests = element["statistics"]["unsuccessful_tests"]
            details = element["statistics"]["details"]
            detail_html = """<table width="80%" style="border-collapse:collapse;margin: 15px 0;font-size: 1.0em;font-family: sans-serif;border: 1px solid black;">
                            <tr style="text-align: left;">
                                <th style="border: 1px solid black;padding:7px 7px;">Test Name</th>
                                <th style="border: 1px solid black;padding:7px 7px;">Expected Value</th>
                                <th style="border: 1px solid black;padding:7px 7px;">Observed Value</th>
                                <th style="border: 1px solid black;padding:7px 7px;">Success</th>
                            </tr>"""
            for detail in details:
                detail_status = detail["success"]
                if detail_status == True:
                    details_td_css_color = "green"
                else:
                    details_td_css_color = "red"

                details_td_status = f"""<span style="color: {details_td_css_color};">{detail_status}</span>"""
                detail_html = (
                    detail_html
                    + f""" <tr  style="text-align: left;">
                                <td style="border: 1px solid black;padding:7px 7px;">{detail["test_name"]}</th>
                                <td style="border: 1px solid black;padding:7px 7px;">{detail["expected_value"]}</th>
                                <td style="border: 1px solid black;padding:7px 7px;">{detail["observed_value"]}</th>
                                <td style="border: 1px solid black;padding:7px 7px;">{details_td_status}</th>
                            </tr>"""
                )

            detail_html = detail_html + "</table>"
            json_path = element["path"]
            if stripe_row:
                css_style = (
                    "border-bottom: 1px solid #dddddd;background-color: #f2f2f2;"
                )
                stripe_row = False
            else:
                css_style = "border-bottom: 1px solid #dddddd;"
                stripe_row = True

            if success_percent < 100:
                validation_needs_review = True
                css_style = css_style + "color:red;"

            html_body = (
                html_body
                + f"""<tr style="{css_style}">
                                <td style=" padding: 12px 15px;">{table_name}</td>
                                <td>{evaluated_tests} | {successful_tests} | {unsuccessful_tests}</td>
                                <td>{detail_html}</td>                            
                                </tr>"""
            )

    status = "Passed Validation" if not validation_needs_review else "NEEDS REVIEW"
    status_html_color = "green" if not validation_needs_review else "red"
    status_html = f"""<span style="color: {status_html_color};">{status}</span>"""
    validation_mode_str = (
        validation_mode
        if adjust_metrics_range == False
        else f"{validation_mode} <br/> **<i>Metrics Adjusted by 1 for range Calculations</>"
    )
    email_body = (
        html_template.replace("#BODY#", html_body)
        .replace("#DATA_SOURCE#", data_source)
        .replace("#DELIVERY_DATE#", delivery_date)
        .replace("#WORKFLOW_ID#", workflow_id)
        .replace("#VALIDATION_MODE#", validation_mode_str)
        .replace("#STATUS#", status_html)
    )

    if validation_needs_review:
        email_subject = f"[{app_environment}] {data_source} with delivery date {delivery_date} needs your approval."
    else:
        email_subject = f"[{app_environment}] {data_source} with delivery date {delivery_date} staging completed."

    url = email_service_url
    message_bytes = email_body.encode("utf-8")
    base64_bytes = base64.b64encode(message_bytes)
    base64_message = base64_bytes.decode("utf-8")
    json_payload = {
        "emailTo": email_to,
        "emailSubject": email_subject,
        "workflow_id": workflow_id,
        "request_id": request_id,
        "data_source": data_source,
        "approvalRequired": validation_needs_review,
        "emailBody_Base64": base64_message,
    }

    json_payload = json.loads(json.dumps(json_payload))
    print(f"\n email request : {json_payload}")
    if (
        send_email_mode.casefold() == "on_needs_review" and validation_needs_review
    ) or send_email_mode.casefold() == "always":
        response = requests.post(
            url, json=json_payload, headers={"Content-Type": "application/json"}
        )
        if response.ok:
            return validation_needs_review
        else:
            print(response.text)
            raise Exception(
                f"Error invoking url at {url}. \n Status_Code: {response.status_code}. Text: {response.text}"
            )
    else:
        print(
            f"NOT sending email since send_email_mode is {send_email_mode} and validation_needs_review is {validation_needs_review}"
        )


# COMMAND ----------


def generate_canonical_manifest():
    if validation_mode.casefold() == "vendor_specific":
        return process_vendor_specific()
    elif validation_mode.casefold() == "vendor_common":
        return process_vendor_common()
    else:
        raise Exception(f"invalid validation_mode parameter - {validation_mode}")


def process():
    canonical_df = generate_canonical_manifest()
    ge_nb_output = dbutils.notebook.run("validate_staging_ge", 36000, ge_nb_params_json)

    save_metadata_to_db(canonical_df)
    ge_nb_output_json = json.loads(ge_nb_output)

    print("\n")
    print(ge_nb_output_json)
    if ge_nb_output_json["success"] == False:
        error = ge_nb_output_json["error"]
        raise Exception(f"ge notebook error : {error}")

    ge_nb_output_body = json.loads(ge_nb_output_json["output"])
    return ge_nb_output_body


# COMMAND ----------

try:
    spark_setup()
    if validation_mode.casefold() != "skip_validation":
        ge_nb_output_body = process()
        print(f"ge_nb_output_body: {ge_nb_output_body}")
        validation_needs_review = send_validation_email(ge_nb_output_body)

        if not validation_needs_review:
            cdh_helper.publish_event_status(
                status_success=True,
                data_source=data_source,
                workflow_id=workflow_id,
                request_id=request_id,
                outputs=[],
            )
        else:
            print(
                f"\n NOT sending a response back to orchestrator since manual approval is required which is handled by the notifier service."
            )
    else:
        process_skip_validation()
        cdh_helper.publish_event_status(
            status_success=True,
            data_source=data_source,
            workflow_id=workflow_id,
            request_id=request_id,
            outputs=[],
        )

except Exception as ex:
    print(ex)
    ex_formatted = cdh_helper.exception_to_string(ex)
    print(ex_formatted)
    cdh_helper.publish_event_status(
        status_success=False,
        data_source=data_source,
        workflow_id=workflow_id,
        request_id=request_id,
        outputs=[{"error": str(ex)}],
    )
