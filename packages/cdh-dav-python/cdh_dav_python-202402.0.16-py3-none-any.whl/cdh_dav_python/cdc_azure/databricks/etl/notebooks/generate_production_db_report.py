# Databricks notebook source
dbutils.widgets.text("data_source", "")
dbutils.widgets.text("delivery_date", "")
dbutils.widgets.text("request_id", "ISOLATED")
dbutils.widgets.text("workflow_id", "ISOLATED")
dbutils.widgets.text("storage_account_name", "")
dbutils.widgets.text("delivery_type", "")
dbutils.widgets.text("email_to", "")
# comma separated names for databases
dbutils.widgets.text("database_names", "")
dbutils.widgets.text("output_file_directory", "")

# COMMAND ----------

import base64
import requests
import os
import json
import cdc_azure.databricks.etl.shared.cdh_helper as cdh_helper
from delta.tables import *


# COMMAND ----------

data_source = dbutils.widgets.get("data_source")
delivery_date = dbutils.widgets.get("delivery_date")
request_id = dbutils.widgets.get("request_id")
workflow_id = dbutils.widgets.get("workflow_id")
storage_account_name = dbutils.widgets.get("storage_account_name")
delivery_type = dbutils.widgets.get("delivery_type")
email_to = dbutils.widgets.get("email_to")
database_names = dbutils.widgets.get("database_names")
output_file_directory = dbutils.widgets.get("output_file_directory")

app_environment = cdh_helper.get_app_environment()
email_service_url = cdh_helper.get_notification_service_url()
databases = database_names.split(",")
print(databases)

results_array = []
results_array_level2 = []
base_path = "abfss://" + "cdh" + "@" + storage_account_name + ".dfs.core.windows.net/"

# COMMAND ----------


def fetchTables(database):
    tables = []
    print("Database:", database)
    v = spark.sql("SHOW TABLES in " + database + "")
    print(v)
    for row in v.collect():
        t = spark.sql("DESCRIBE DETAIL " + database + "." + row["tableName"] + "")
        type = t.collect()[0]["format"]
        if type == "delta":
            tables.append(row["tableName"])

    return tables


def is_table_partitioned(table):
    col_details = spark.sql("describe extended " + table).collect()
    for col_detail in col_details:
        if col_detail["col_name"].casefold() == "not partitioned":
            return False

    return True


def get_database_metrics():
    for database in databases:
        tables = fetchTables(database)
        print(f"{database} : {tables}")
        results = []
        for table in tables:
            try:
                full_table_name = database + "." + table
                df = spark.sql("describe history " + full_table_name)
                latest_version = df.collect()[0]["version"]
                latest_timestamp = str(df.collect()[0]["timestamp"])
                row_count = spark.sql(
                    "select count(*) as count from  " + full_table_name
                ).collect()[0]["count"]
                if df.count() > 1:
                    previous_version = df.collect()[1]["version"]
                    previous_row_count = spark.sql(
                        f"select count(*) as count from  {full_table_name}@v{previous_version}"
                    ).collect()[0]["count"]
                else:
                    previous_version = "n/a"
                    previous_row_count = 0

                if is_table_partitioned(full_table_name):
                    try:
                        df = spark.sql("SHOW PARTITIONS " + full_table_name)
                        partitions = df.columns
                    except Exception as ex:
                        print(ex)
                        partitions = []
                else:
                    partitions = []

                results.append(
                    {
                        "database": database,
                        "table": table,
                        "version": latest_version,
                        "timestamp": latest_timestamp,
                        "row_count": row_count,
                        "previous_row_count": previous_row_count,
                        "partitions": partitions,
                    }
                )

            except Exception as ex:
                print(f"error when processing table {full_table_name}")
                print(ex)
                results.append(
                    {
                        "database": database,
                        "table": table,
                        "version": 0,
                        "timestamp": "",
                        "row_count": 0,
                        "previous_row_count": 0,
                        "partitions": "[]",
                    }
                )

        results_array.append(results)

    full_output_path = os.path.join(
        base_path, output_file_directory, "production_validation.json"
    )
    if (
        workflow_id is not None
        and workflow_id != ""
        and workflow_id.casefold() != "ISOLATED".casefold()
        and storage_account_name is not None
    ):
        dbutils.fs.put(full_output_path, json.dumps(results_array), True)


# COMMAND ----------

EMAIL_TEMPLATE_HEAD = """
<div>
    <h2>#DATA_SOURCE# datasource</h2>
    <p>
        <ul>
        <li>Workflow: #WORKFLOW_ID#</li>
        <li>Delivery Date: #DELIVERY_DATE#</li>
        <li>Load Type: #LOAD_TYPE# </li>
    </ul></p>"""

EMAIL_TEMPLATE_BODY = """
<table role="presentation" border="1" width="100%">
    <caption>#DATABASE_NAME#</caption>
  <tr>
    <th>Table</th>
    <th>Partitions</th>
    <th>Latest Version</th>
    <th>Last Updated At</th>
    <th>Latest Count</th>
     <th>Previous Count</th>
     <th>Difference</th>
  </tr>
  #BODY#
</table>

</div>
"""


# COMMAND ----------


def process():
    get_database_metrics()
    for database in databases:
        email_body = ""
        for db_result in results_array:
            html_body = ""
            html_template = EMAIL_TEMPLATE_BODY
            db = db_result[0]["database"]
            stripe_row = False
            for table in db_result:
                row_count = int(table["row_count"])
                row_count_formatted = "{:,}".format(row_count)
                previous_row_count = int(table["previous_row_count"])
                previous_row_count_formatted = "{:,}".format(previous_row_count)
                row_count_delta_formatted = "{:,}".format(
                    row_count - previous_row_count
                )
                table_name = table["table"]
                version = table["version"]
                timestamp = table["timestamp"]
                partitions = table["partitions"]

                if stripe_row:
                    css_style = "background-color: #f2f2f2;"
                    stripe_row = False
                else:
                    css_style = ""
                    stripe_row = True

                html_body = (
                    html_body
                    + f"""<tr style="{css_style}">
                    <td>{table_name}</td>
                    <td>{partitions}</td>
                    <td>{version}</td>
                    <td>{timestamp}</td>
                    <td>{row_count_formatted}</td>
                    <td>{previous_row_count_formatted}</td>
                    <td>{row_count_delta_formatted}</td>
                    </tr>"""
                )
            email_body = (
                email_body
                + html_template.replace("#BODY#", html_body).replace(
                    "#DATABASE_NAME#", db
                )
                + "<br/><br/>"
            )

    full_email_body = email_body
    url = email_service_url
    email_subject = f"CDH Database Report - {len(databases)} databases."
    if (
        len(databases) == 1
        and workflow_id is not None
        and workflow_id != ""
        and workflow_id.casefold() != "ISOLATED".casefold()
    ):
        email_subject = (
            f"[{app_environment}] ETL completed for {data_source} - {delivery_date} ."
        )
        full_email_body = (
            EMAIL_TEMPLATE_HEAD.replace("#WORKFLOW_ID#", workflow_id)
            .replace("#DELIVERY_DATE#", delivery_date)
            .replace("#DATA_SOURCE#", data_source)
            .replace("#LOAD_TYPE#", delivery_type)
            + email_body
        )

    message_bytes = full_email_body.encode("utf-8")
    base64_bytes = base64.b64encode(message_bytes)
    base64_message = base64_bytes.decode("utf-8")
    json = {
        "emailBody_Base64": base64_message,
        "emailTo": email_to,
        "emailSubject": email_subject,
    }
    response = requests.post(
        url, json=json, headers={"Content-Type": "application/json"}
    )
    if response.ok:
        print("EMAIL SENT")
    else:
        print(response.text)
        raise Exception(
            f"Error invoking url at {url}. \n Status_Code: {response.status_code}. Text: {response.text}"
        )


# COMMAND ----------

try:
    process()
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
