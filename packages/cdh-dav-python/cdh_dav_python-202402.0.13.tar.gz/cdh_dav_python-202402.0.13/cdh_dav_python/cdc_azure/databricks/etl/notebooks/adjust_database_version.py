# Databricks notebook source
dbutils.widgets.text("data_source", "")
dbutils.widgets.text("delivery_date", "")
dbutils.widgets.text("request_id", "ISOLATED")
dbutils.widgets.text("workflow_id", "ISOLATED")
dbutils.widgets.text("database_name", "")


# COMMAND ----------

import cdc_azure.databricks.etl.shared.cdh_helper as cdh_helper

# COMMAND ----------

data_source = dbutils.widgets.get("data_source")
delivery_date = dbutils.widgets.get("delivery_date")
request_id = dbutils.widgets.get("request_id")
workflow_id = dbutils.widgets.get("workflow_id")
database_name = dbutils.widgets.get("database_name")

# COMMAND ----------

import builtins as p
from datetime import datetime, timezone


def get_max_version_for_database(results):
    try:
        versions = []
        for item in results:
            versions.append(item["version"])
        return p.max(versions)
    except Exception as ex:
        print(f"Error in finding max version for table{ex}")


def update_version_for_tables(results, maxVersion):
    try:
        sql_array = []
        for item in results:
            current_version = item["version"]
            if maxVersion != item["version"]:
                i = item["version"] + 1
                time_now = datetime.now(tz=timezone.utc)
                for n in range(i, maxVersion + 1):
                    adjust_reason = f"Version Incremented from {current_version} to {str(maxVersion)}[Delivery Date# {delivery_date}]"
                    print(
                        """Alter table {DB}.{TB} SET TBLPROPERTIES ('cdh_comment'='{adjust_reason}')""".format(
                            DB=item["database"],
                            TB=item["table"],
                            adjust_reason=adjust_reason,
                        )
                    )
                    sql(
                        """Alter table {DB}.{TB} SET TBLPROPERTIES ('cdh_comment'='{adjust_reason}')""".format(
                            DB=item["database"],
                            TB=item["table"],
                            adjust_reason=adjust_reason,
                        )
                    )
                sql_array.append(
                    f"""('{workflow_id}', '{data_source}', '{item['database']}' , '{item['table']}', '{item['version']}', '{maxVersion}', '{time_now}' )"""
                )

            else:
                print(f"{item['table']} Table version already matches maximum version")

        if not sql_array:
            print(f"All Tables version already matches maximum version")
        else:
            insert_to_cdm_process_version_adjustment(sql_array)

    except Exception as ex:
        print(f"Exception while updating versions {ex}")
        raise


def get_database_metrics(database, tables):
    print(f"{database} : {tables}")
    results = []
    for table in tables:
        try:
            full_table_name = database + "." + table
            df = spark.sql("describe history " + full_table_name)
            latest_version = df.collect()[0]["version"]
            results.append(
                {"database": database, "table": table, "version": latest_version}
            )
        except Exception as ex:
            print(f"error when processing table {full_table_name}")
            print(ex)
            results.append({"database": database, "table": table, "version": 0})
    print(results)
    return results


def insert_to_cdm_process_version_adjustment(sql_array):
    try:

        ingest_table = "cdh_engineering.cdm_process_version_adjustment"
        spark.sql(
            f"DELETE from {ingest_table} where workflow_id= '{workflow_id}' and dataset_name='{data_source}'"
        )
        sql_header = f"""insert into {ingest_table} (workflow_id, dataset_name, database_name, table_name, start_version, end_version, created_time) values \n"""

        sql = sql_header + ", \n".join(sql_array) + ";"
        print(f"\n{sql}")
        spark.sql(sql)
    except Exception as ex:
        print(f"Error in inserting to table cdm_process_version_adjustment")


# COMMAND ----------

try:
    tables = cdh_helper.fetchTables(database=database_name)
    results = get_database_metrics(database=database_name, tables=tables)
    maxVersion = get_max_version_for_database(results)
    print(f"Max Version is {str(maxVersion)}")
    update_version_for_tables(results, maxVersion)
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
