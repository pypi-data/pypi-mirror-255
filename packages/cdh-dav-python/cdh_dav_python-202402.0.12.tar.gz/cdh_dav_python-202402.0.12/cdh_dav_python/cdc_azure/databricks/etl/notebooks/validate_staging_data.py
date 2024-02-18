# Databricks notebook source
dbutils.widgets.text("data_source", "")
dbutils.widgets.text("delivery_date", "")
dbutils.widgets.text("request_id", "ISOLATED")
dbutils.widgets.text("workflow_id", "ISOLATED")
dbutils.widgets.text("storage_account_name", "")
dbutils.widgets.text("production_source_folder", "")
dbutils.widgets.text("staging_source_folder", "")
dbutils.widgets.text("manifest_file_folder", "")
dbutils.widgets.text("manifest_file", "")
dbutils.widgets.text("excluded_tables", "")
dbutils.widgets.text("delivery_type", "")
dbutils.widgets.text("email_to", "")
dbutils.widgets.text("validation_file_provided_by_vendor", "False")
dbutils.widgets.text("is_validation_file_canonical", "False")
dbutils.widgets.dropdown(
    "send_email_mode", "on_needs_review", ["always", "on_needs_review"]
)

# COMMAND ----------

from multiprocessing.pool import ThreadPool
import multiprocessing as mp
from pyspark.sql.functions import *
import os
import json
import base64
import requests
import time

import cdc_azure.databricks.etl.shared.cdh_helper as cdh_helper
import cdc_azure.databricks.etl.shared.data_load_helper as data_load_helper


# COMMAND ----------

data_source = dbutils.widgets.get("data_source")
delivery_date = dbutils.widgets.get("delivery_date")
request_id = dbutils.widgets.get("request_id")
workflow_id = dbutils.widgets.get("workflow_id")
storage_account_name = dbutils.widgets.get("storage_account_name")
production_source_folder = dbutils.widgets.get("production_source_folder")
staging_source_folder = dbutils.widgets.get("staging_source_folder")
manifest_file_folder = dbutils.widgets.get("manifest_file_folder")
manifest_file = dbutils.widgets.get("manifest_file")
excluded_tables = dbutils.widgets.get("excluded_tables")
delivery_type = dbutils.widgets.get("delivery_type")
email_to = dbutils.widgets.get("email_to")
validation_file_provided_by_vendor = (
    dbutils.widgets.get("validation_file_provided_by_vendor").casefold() == "true"
)
is_validation_file_canonical = (
    dbutils.widgets.get("is_validation_file_canonical").casefold() == "true"
)
send_email_mode = dbutils.widgets.get("send_email_mode")


app_environment = cdh_helper.get_app_environment()
email_service_url = cdh_helper.get_notification_service_url()

is_manifest_present = manifest_file != "" and manifest_file is not None
excluded_tables_array = (
    []
    if excluded_tables is None or len(excluded_tables) == 0
    else excluded_tables.split(",")
)
result_array = {}

base_path = "abfss://" + "cdh" + "@" + storage_account_name + ".dfs.core.windows.net/"
canonical_validation_file_name = f"{data_source}_{delivery_date}_level1.csv"
canonical_validation_file_path = os.path.join(
    base_path, manifest_file_folder, canonical_validation_file_name
)
output_file_directory = os.path.join(
    base_path, f"work/datahub/inprogress/{workflow_id}/misc"
)
manifest_file_folder_full_path = os.path.join(base_path, manifest_file_folder)
canonical_validation_file_level_1_columns = ["table_name", "row_count"]

# COMMAND ----------


def get_row_counts(source_folder_location, format_type, json_element_name, tables):
    for table_name in tables:
        source = os.path.join(source_folder_location, table_name)
        df = spark.read.format(format_type).load(source)
        if table_name in result_array.keys():
            info = result_array.get(table_name)
            info.update({json_element_name: df.count()})
        else:
            result_array[table_name] = {json_element_name: df.count()}


# COMMAND ----------


def process_production():
    source_folder_location = base_path + production_source_folder
    tables = cdh_helper.get_first_level_subfolders(source_folder_location)

    print(f"\n production : {tables}")
    get_row_counts(source_folder_location, "delta", "currentProductionCount", tables)


def process_staging(json_element_name="stagingCount"):
    source_folder_location = base_path + staging_source_folder
    tables = cdh_helper.get_first_level_subfolders(source_folder_location)

    print(f"\n staging : {tables}")
    get_row_counts(source_folder_location, "parquet", json_element_name, tables)


# COMMAND ----------


def validate_canonical_manifests():
    files_list = list(
        cdh_helper.get_specific_files_in_directory(
            manifest_file_folder_full_path, canonical_validation_file_name
        )
    )
    if len(files_list) > 0:
        df = (
            spark.read.format("csv")
            .option("inferSchema", True)
            .option("header", True)
            .option("sep", "|")
            .load(files_list)
        )

        columns = df.schema.fields[0].name.split(",")
        print(columns)
        does_columns_match_canonical = (
            columns == canonical_validation_file_level_1_columns
        )
        print(f"does_columns_match_canonical: {does_columns_match_canonical}")
    else:
        raise ValueError(
            f"Canonical validation file {canonical_validation_file_name} does not exist at location {manifest_file_folder_full_path}."
        )


def process_vendor_provided_manifests():
    file_paths = cdh_helper.get_specific_files_in_directory(
        manifest_file_folder_full_path, manifest_file
    )
    print(f"validation files: {file_paths}")
    out_file = ""
    if is_validation_file_canonical == True:
        print("Processing canonical manifest files.")
        validate_canonical_manifests()
        return
    if data_source.casefold() == "premier":
        print("Processing premier manifest files.")
        out_file = process_premier(file_paths)
    else:
        raise Exception(f"no transformation exists for source {data_source}")

    dbutils.fs.mv(out_file, canonical_validation_file_path)


def process_premier(file_paths):
    df = (
        spark.read.format("csv")
        .option("inferSchema", True)
        .option("header", True)
        .option("sep", "|")
        .load(file_paths)
    )

    group_df = (
        df.groupBy("TABLENAME")
        .agg(sum("ROWCOUNT").alias("row_count"))
        .withColumnRenamed("TABLENAME", "table_name")
    )
    # group_df.show()

    dest_path_temp = base_path + f"raw/{data_source}/{delivery_date}-temp/manifest/"
    group_df.write.mode("overwrite").option("header", True).csv(dest_path_temp)
    csv_file = cdh_helper.get_first_file_in_directory(dest_path_temp, ".csv")
    # print(csv_file)
    return csv_file


# COMMAND ----------

manifest_count_json_prop_name = "manifestCount"


def generate_manifest():
    source_folder_location = base_path + staging_source_folder
    tables_1 = cdh_helper.get_first_level_subfolders(source_folder_location)
    canonical_array = []

    for table in tables_1:
        table_name = table
        source = os.path.join(source_folder_location, table_name)
        df = spark.read.format("parquet").load(source)
        row_count = df.count()
        canonical_array.append([table_name, row_count])

    df = spark.createDataFrame(
        data=canonical_array, schema=canonical_validation_file_level_1_columns
    )
    display(df)
    dest_path_temp = base_path + f"raw/{data_source}/{delivery_date}-temp/manifest/"
    print(f"Deleting directory: {dest_path_temp}")
    dbutils.fs.rm(dest_path_temp, True)
    df.coalesce(1).write.mode("overwrite").option("header", True).csv(dest_path_temp)
    csv_file = cdh_helper.get_first_file_in_directory(dest_path_temp, ".csv")
    print(f"Moving {csv_file} to {canonical_validation_file_path}")
    dbutils.fs.mv(csv_file, canonical_validation_file_path)
    return dest_path_temp


def process_manifest():
    if is_manifest_present:
        df = (
            spark.read.format("csv")
            .option("inferSchema", True)
            .option("header", True)
            .option("sep", ",")
            .load(canonical_validation_file_path)
        )

        for row in df.collect():
            table_name = str(row["table_name"]).lower()
            row_count = str(row["row_count"]).lower()
            if table_name in result_array.keys():
                info = result_array.get(table_name)
                info.update({manifest_count_json_prop_name: int(row_count)})
            else:
                result_array[table_name] = {
                    manifest_count_json_prop_name: int(row_count)
                }

    else:
        # no manifest - get counts as staging
        process_staging(manifest_count_json_prop_name)


# COMMAND ----------


def calculate_diffs():
    for table_name in result_array.keys():
        info = result_array.get(table_name)

        stagingCount = 0
        manifestCount = 0
        prodCount = 0
        row_marked_for_review = False

        if result_array[table_name].get("currentProductionCount") is not None:
            prodCount = int(result_array[table_name]["currentProductionCount"])
        else:
            info.update({"currentProductionCount": 0})

        if result_array[table_name].get("stagingCount") is not None:
            stagingCount = int(result_array[table_name]["stagingCount"])
        else:
            info.update({"stagingCount": 0})

        if (
            result_array[table_name].get("manifestCount") is not None
            and is_manifest_present
        ):
            manifestCount = int(result_array[table_name]["manifestCount"])

        if stagingCount > 0:
            if delivery_type.casefold() == "full":
                new_records = f"{(stagingCount - prodCount):,d}"
            else:
                new_records = f"{(stagingCount):,d}"
        else:
            if table_name in excluded_tables_array:
                new_records = "excluded for comparision"
            else:
                new_records = "missing"
                row_marked_for_review = True

        expected_actual_diff = 0
        if manifestCount > 0:
            expected_actual_diff_int = stagingCount - manifestCount
            expected_actual_diff = f"{expected_actual_diff_int:,d}"
            if expected_actual_diff_int > 0:
                row_marked_for_review = True
        else:
            expected_actual_diff = "n/a"

        # if stagingCount < prodCount and delivery_type.casefold() == "full":
        #     row_marked_for_review = True

        info.update({"newRecords": new_records})
        info.update({"expectedActualDiff": expected_actual_diff})
        info.update({"row_marked_for_review": row_marked_for_review})


# COMMAND ----------

VALIDATION_EMAIL_TEMPLATE = """
<div>
    <h2>#DATA_SOURCE# datasource</h2>
    <p>
        <ul>
        <li>Workflow: #WORKFLOW_ID#</li>
        <li>Delivery Date: #DELIVERY_DATE#</li>
        <li>Load Type: #LOAD_TYPE# </li>
        <li>Manifest Files Present: #MANIFEST_PRESENT# </li>
        <li>Status: #STATUS# </li>
    </ul></p>

<table role="presentation" border="1" width="100%">
  <tr>
    <th>Table</th>
    <th>Production Count (P)</th>
    <th>Staging Count (S)</th>
    <th>Vendor Manifest Count (V)</th>
    <th>New Records <br/> Full: (S - P)<br/> Increment: (S)</th>
    <th>Difference (V - S)</th>    
  </tr>
  #BODY#
</table>

</div>
"""


def send_validation_email():
    # generate html
    validation_needs_review = False
    html_template = VALIDATION_EMAIL_TEMPLATE
    html_body = ""
    stripe_row = False
    for table_name in result_array.keys():
        prodCount = "{:,}".format(
            int(result_array[table_name]["currentProductionCount"])
        )
        stagingCount = "{:,}".format(int(result_array[table_name]["stagingCount"]))
        if (
            result_array[table_name].get("manifestCount") is not None
            and is_manifest_present
        ):
            manifestCount = "{:,}".format(
                int(result_array[table_name]["manifestCount"])
            )
        else:
            manifestCount = "n/a"
        newRecords = result_array[table_name]["newRecords"]
        expectedActualDiff = result_array[table_name]["expectedActualDiff"]
        row_marked_for_review = bool(result_array[table_name]["row_marked_for_review"])

        if row_marked_for_review:
            validation_needs_review = True
        if stripe_row:
            css_style = "background-color: #f2f2f2;"
            stripe_row = False
        else:
            css_style = ""
            stripe_row = True

        if row_marked_for_review:
            css_style = css_style + "color:red;"

        html_body = (
            html_body
            + f"""<tr style="{css_style}">
                                <td>{table_name}</td>
                                <td>{prodCount}</td>
                                <td>{stagingCount}</td>
                                <td>{manifestCount}</td>
                                <td>{newRecords}</td>
                                <td>{expectedActualDiff}</td>
                              </tr>"""
        )

    email_body = (
        html_template.replace("#BODY#", html_body)
        .replace("#DATA_SOURCE#", data_source)
        .replace("#DELIVERY_DATE#", delivery_date)
        .replace("#WORKFLOW_ID#", workflow_id)
        .replace(
            "#STATUS#",
            "Passed Validation" if not validation_needs_review else "NEEDS REVIEW",
        )
        .replace("#MANIFEST_PRESENT#", "Yes" if is_manifest_present else "No")
        .replace("#LOAD_TYPE#", delivery_type)
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


def process():
    if validation_file_provided_by_vendor == True:
        print("Processing vendor specific manifest files.")
        process_vendor_provided_manifests()
    elif is_validation_file_canonical == True:
        print("Processing canonical manifest files.")
        validate_canonical_manifests()
    else:
        print(
            "\n WARNING: Manifest file not present so system will autogenerate Level 1 manifest file from staging data."
        )
        generate_manifest()

    process_production()
    process_staging()
    process_manifest()
    calculate_diffs()

    json_object = json.dumps(result_array, indent=4)
    full_output_path = os.path.join(output_file_directory, "staging_validation.json")
    dbutils.fs.put(full_output_path, json_object, True)

    data_load_helper.insert_raw_delivery_metrics_table_level(
        data_source, delivery_date, workflow_id, canonical_validation_file_path
    )

    validation_needs_review = send_validation_email()

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
        # cdh_helper.publish_event_status_with_custom_status(status="Rejected", data_source=data_source, workflow_id=workflow_id, request_id=request_id, outputs=[])


try:
    process()

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
