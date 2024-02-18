# Databricks notebook source
dbutils.widgets.text("data_source", "")
dbutils.widgets.text("delivery_date", "")
dbutils.widgets.text("source_folder", "")
dbutils.widgets.text("manifest_file_path", "")
dbutils.widgets.text("storage_account_name", "")
dbutils.widgets.text("workflow_id", "")
dbutils.widgets.text("adjust_metrics_range", "True")

# Remove test widgets
# dbutils.widgets.removeAll()

# COMMAND ----------

# MAGIC %pip install great-expectations==0.16.3
# MAGIC %pip install azure-storage-blob
# MAGIC %pip install azure.identity

# COMMAND ----------

# Developing in Great Expectations Version 0.16.3

from pyspark.sql.types import *
from pyspark.sql.functions import *
from ruamel import yaml
from datetime import datetime as dt
from operator import itemgetter
import json
import os
import re

from great_expectations.core.batch import RuntimeBatchRequest
from great_expectations.core import ExpectationConfiguration
from great_expectations.util import get_context
from great_expectations.data_context.types.base import DataContextConfig

# Azure Service Libaries
from azure import identity
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient

# Spark and Utility Libraries
import cdc_azure.databricks.etl.shared.cdh_helper as cdh_helper
from cdc_azure.databricks.etl.shared import constants


# COMMAND ----------

data_source = dbutils.widgets.get("data_source")
delivery_date = dbutils.widgets.get("delivery_date")
source_folder = dbutils.widgets.get("source_folder")
manifest_file_path = dbutils.widgets.get("manifest_file_path")
storage_account_name = dbutils.widgets.get("storage_account_name")
workflow_id = dbutils.widgets.get("workflow_id")
adjust_metrics_range = bool(dbutils.widgets.get("adjust_metrics_range"))

base_path = f"abfss://cdh@{storage_account_name}.dfs.core.windows.net/"
source_folder_location = os.path.join(base_path, source_folder)
output_file_directory = os.path.join(
    base_path, f"work/datahub/completed/{data_source}/{workflow_id}/misc"
)
manifest_file_full_path = manifest_file_path
data_tables = []

# Initialize variables for our run; Parameters passed by ADF or orchestrator
checkpoint_name = f"{data_source}_{delivery_date}_{workflow_id}_checkpoint"
run_id = f"{data_source}_{dt.today().strftime('%Y%m%d_%H:%M:%S')}"
run_name_template = f"{delivery_date}_{workflow_id}"  # f"{delivery_date}_run"
az_account_url = f"https://{storage_account_name}.blob.core.windows.net"
container = "cdh"

print(manifest_file_full_path)


# COMMAND ----------


def spark_setup():
    cdh_helper.secure_connect_spark_adls()
    secret_scope = constants.get_secret_scope()
    os.environ["AZURE_CLIENT_SECRET"] = dbutils.secrets.get(
        scope=secret_scope, key="cdh-adb-client-secret"
    )
    os.environ["AZURE_TENANT_ID"] = dbutils.secrets.get(
        scope=secret_scope, key="cdh-adb-tenant-id"
    )
    os.environ["az_sub_client_id"] = dbutils.secrets.get(
        scope=secret_scope, key="cdh-adb-client-id"
    )


# COMMAND ----------

# MAGIC %md ### Create Data Context
# MAGIC Setting up an "in code" Data Context. Instead of defining the Data Context via great_expectations.yml, we can do so by instantiating BaseDataContext with a config. In Databricks, we can do either, but we're using the code version below.
# MAGIC
# MAGIC - The method for authentication here is done via the `DefaultAzureCredential` class, running with Service Principal Credentials
# MAGIC - That class is pulling from 3 environment variables we specified earlier and authenticating via the client, secret, tenant ids from the `dbs-scope-dev-kv-CDH` secrets scope

# COMMAND ----------

# Setting the config for our Data Context, to include the locations our various stores on the cdh/ container, denoted in the 'prefix' keys below
data_context_config = DataContextConfig(
    config_version=3,
    plugins_directory=None,
    config_variables_file_path=None,
    #     concurrency={'enabled':True},                                   # Enable checkpoint validations to run parallel with multithreading - This is broken
    stores={
        "expectations_AZ_store": {
            "class_name": "ExpectationsStore",
            "store_backend": {
                "class_name": "TupleAzureBlobStoreBackend",  # Class name for Azure Blob Storage Backend
                "container": container,  # The container within our storage account
                "prefix": f"work/great-expectations/{data_source}/expectations",  # The folder in the container where Expectation files will be located
                # "prefix": f"work/datahub/inprogress/{workflow_id}/great-expectations/expectations",
                "account_url": az_account_url,
            },
        },
        "validations_AZ_store": {
            "class_name": "ValidationsStore",
            "store_backend": {
                "class_name": "TupleAzureBlobStoreBackend",
                "container": container,
                "prefix": f"work/great-expectations/{data_source}/validations",  # work/datahub/inprogress maybe as parameter
                # "prefix": f"work/datahub/inprogress/{workflow_id}/great-expectations/validations",
                "account_url": az_account_url,
            },
        },
        "checkpoints_AZ_store": {
            "class_name": "CheckpointStore",
            "store_backend": {
                "class_name": "TupleAzureBlobStoreBackend",
                "container": container,
                "prefix": f"work/great-expectations/{data_source}/checkpoints",
                # "prefix": f"work/datahub/inprogress/{workflow_id}/great-expectations/checkpoints",
                "account_url": az_account_url,
            },
        },
        "evaluation_parameter_AZ_store": {
            "class_name": "EvaluationParameterStore",
            "store_backend": {
                "class_name": "TupleAzureBlobStoreBackend",
                "container": container,
                "prefix": f"work/great-expectations/{data_source}/evaluation-parameters",
                # "prefix": f"work/datahub/inprogress/{workflow_id}/great-expectations/evaluation-parameters",
                "account_url": az_account_url,
            },
        },
        "profiler_AZ_store": {
            "class_name": "ProfilerStore",
            "store_backend": {
                "class_name": "TupleAzureBlobStoreBackend",
                "container": container,
                "prefix": f"work/great-expectations/{data_source}/profilers",
                # "prefix": f"work/datahub/inprogress/{workflow_id}/great-expectations/profilers",
                "account_url": az_account_url,
            },
        },
        #         "metrics_AZ_store": {              # MetricStores can store metrics computed during validation. Tracks run_id of validation and expectation suite
        #             "class_name": "MetricStore",
        #             "store_backend": {
        #                 "class_name": "TupleAzureBlobStoreBackend", # Can only use Postgres at this time, but keep an eye on this feature for future Azure support
        #                 "container": container,
        #                 "prefix": "work/great-expectations/metrics-store",
        #                 "account_url": az_account_url
        #            }
        #         },
    },
    expectations_store_name="expectations_AZ_store",
    validations_store_name="validations_AZ_store",
    checkpoint_store_name="checkpoints_AZ_store",
    evaluation_parameter_store_name="evaluation_parameter_AZ_store",
    profiler_store_name="profiler_AZ_store",
    data_docs_sites={
        "AZ_site": {
            "class_name": "SiteBuilder",
            "store_backend": {
                "class_name": "TupleAzureBlobStoreBackend",
                "container": container,
                # "prefix":  "work/great-expectations/uncommitted/data_docs/local_site",
                "prefix": f"work/great-expectations/{data_source}/data_docs/local_site",
                "account_url": az_account_url,
            },
            "site_index_builder": {
                "class_name": "DefaultSiteIndexBuilder",
                "show_cta_footer": True,
            },
        }
    },
    validation_operators={
        "action_list_operator": {
            "class_name": "ActionListValidationOperator",
            "action_list": [
                {
                    "name": "store_validation_result",
                    "action": {"class_name": "StoreValidationResultAction"},
                },
                {
                    "name": "store_evaluation_params",
                    "action": {"class_name": "StoreEvaluationParametersAction"},
                },
                {
                    "name": "update_data_docs",
                    "action": {"class_name": "UpdateDataDocsAction"},
                },
                #               #  For potential future azure support for MetricStore
                #                 {
                #                     "name": "store_metrics",
                #                     "action": {"class_name": "StoreMetricsAction",
                #                                "target_store_name": "metrics_AZ_store",
                #                                "requested_metrics": {
                #                                    "*":  [
                #                                        "statistics.evaluated_expectations",
                #                                        "statistics.success_percent",
                #                                        "statistics.unsuccessful_expectations"
                #                                    ]
                #                                }
                #                     },
                #                 },
            ],
        }
    },
)


# COMMAND ----------


def generate_ge_expectations():
    # Iterate through each table in the table list and add/update their expectation suite
    for table in tables:
        expectation_suite_name = f"{table}_expectation_suite"
        print(f"Building: {expectation_suite_name}")
        # Create Expectation Suite
        context.create_expectation_suite(
            expectation_suite_name=expectation_suite_name, overwrite_existing=True
        )

        # Extract Expectation Suite object from data context
        suite = context.add_or_update_expectation_suite(expectation_suite_name)
        # Filter manifest for the batch request we're updating
        # display(df)
        df_table = df.filter(lower("data_object") == table.casefold())
        # display(df_table)
        for row in df_table.collect():
            column = row["data_element"]
            metric = row["metric"]
            value = row["metric_value"]

            # for data_element, metric, metric_value in zip( df_table['data_element'], df_table['metric'], df_table['metric_value'] ):

            print("\t- ", column, metric, value)
            value = int(value)
            try:
                if metric.casefold() == "total_count":
                    expectation_configuration = ExpectationConfiguration(
                        expectation_type="expect_table_row_count_to_equal",
                        kwargs={"value": value},
                    )
                    suite.add_expectation(
                        expectation_configuration=expectation_configuration
                    )

                elif metric.casefold() == "unique_value_count":
                    expectation_configuration = ExpectationConfiguration(
                        expectation_type="expect_column_unique_value_count_to_be_between",
                        kwargs={
                            "column": column,
                            "min_value": value,
                            "max_value": value,
                        },
                    )
                    suite.add_expectation(
                        expectation_configuration=expectation_configuration
                    )

                elif metric.casefold() == "max_value":
                    if adjust_metrics_range:
                        min_value = float(value) - 1
                        max_value = float(value) + 1
                    else:
                        min_value = value
                        max_value = value

                    expectation_configuration = ExpectationConfiguration(
                        expectation_type="expect_column_max_to_be_between",
                        kwargs={
                            "column": column,
                            "min_value": min_value,
                            "max_value": max_value,
                        },
                    )
                    suite.add_expectation(
                        expectation_configuration=expectation_configuration
                    )

                elif metric.casefold() == "min_value":
                    if adjust_metrics_range:
                        min_value = float(value) - 1
                        max_value = float(value) + 1
                    else:
                        min_value = value
                        max_value = value

                    expectation_configuration = ExpectationConfiguration(
                        expectation_type="expect_column_min_to_be_between",
                        kwargs={
                            "column": column,
                            "min_value": min_value,
                            "max_value": max_value,
                        },
                    )
                    suite.add_expectation(
                        expectation_configuration=expectation_configuration
                    )

                elif metric.casefold() == "mean_value":
                    if adjust_metrics_range:
                        min_value = float(value) - 1
                        max_value = float(value) + 1
                    else:
                        min_value = value
                        max_value = value

                    expectation_configuration = ExpectationConfiguration(
                        expectation_type="expect_column_mean_to_be_between",
                        kwargs={
                            "column": column,
                            "min_value": min_value,
                            "max_value": max_value,
                        },
                    )
                    suite.add_expectation(
                        expectation_configuration=expectation_configuration
                    )
            except:
                pass

        # Save the Expectation Suite to our Expectation Store
        context.save_expectation_suite(
            expectation_suite=suite,
            expectation_suite_name=expectation_suite_name,
            overwrite_existing=True,
        )
        print(f"  {expectation_suite_name} saved to expectation store \n")


# COMMAND ----------


def generate_ge_batch_requests():
    # Initialize Empty list to store batch requests, which we will collectively pass to our checkpoint at runtime
    batch_requests = []

    # Iterate through the tables in the vendor directory, register their config, and create a BatchRequest for each table.
    for table in tables:
        # Data Source configuration
        my_spark_datasource_config = {
            "name": data_source,  # Datasource Name.
            "class_name": "Datasource",
            "execution_engine": {
                "class_name": "SparkDFExecutionEngine"
            },  # This defines our execution engine, handles the processing of data and computes our metrics
            "data_connectors": {
                "runtime_data_connector": {  # Data Connector Name.
                    "module_name": "great_expectations.datasource.data_connector",
                    "class_name": "RuntimeDataConnector",
                    "batch_identifiers": [
                        "pipeline_stage",
                        "run_id",
                    ],
                }
            },
        }
        # Convert my_spark_datasource_config to yaml and check the data source for errors
        context.test_yaml_config(yaml.dump(my_spark_datasource_config))
        # print(f'Data Source Config for {table} Passes \n')
        # Add the Datasource to the context
        context.add_datasource(**my_spark_datasource_config)

        table_location = os.path.join(source_folder_location, table)
        batch_request = RuntimeBatchRequest(
            datasource_name=data_source,  # Use Datasource name as specified in my_spark_datasource_config
            data_connector_name="runtime_data_connector",
            data_asset_name=table,  # This can be anything that identifies this data_asset. We use name of our 'table' here
            batch_identifiers={
                "pipeline_stage": "stage",
                "run_id": run_id,
            },
            runtime_parameters={
                "batch_data": spark.read.parquet(
                    f"{table_location}"
                )  # in memory dataframe goes here
            },
        )
        print(f"Batch Request Created Referencing: {table_location} \n")

        batch_requests.append(batch_request)

    # Quick Sanity Check
    print(f"{len(batch_requests)} Total Batch Requests in this Job \n")
    return batch_requests


# COMMAND ----------


def generate_ge_validation_requests(batch_requests):
    # Initialize empty list to store our validation configuration for our checkpoint
    validations = []

    # For every BatchRequest, associate the generic expectation suite and append to our validations list
    for batch_request in batch_requests:
        data_asset_name = batch_request["data_asset_name"]
        expectation_suite_name = f"{data_asset_name}_expectation_suite"
        #     print(data_asset_name, expectation_suite_name)

        # If there is an existing expectation suite for the dataset in the expectation store, add it to the validation configuration
        # print(expectation_suite_name)
        if expectation_suite_name in context.list_expectation_suite_names():
            #         print(data_asset_name, expectation_suite_name, '\n')

            # Since we cannot use more than one suite per validation, we create another batch to execute the dataset specific suite against our data
            validation = {
                "batch_request": batch_request,
                "expectation_suite_name": expectation_suite_name,
            }

            validations.append(validation)

    return validations


# COMMAND ----------


def setup_ge_checkpoint():
    # If the checkpoint for this vendor already exists, skip this step and proceed.
    if checkpoint_name not in context.list_checkpoints():
        # Here we will create and store a Checkpoint with no defined validations, then pass in our DataFrame at runtime. Checkpoints produce Validation Results
        checkpoint_config = {
            "name": checkpoint_name,
            "config_version": 1.0,
            "class_name": "SimpleCheckpoint",  # The SimpleCheckpoint contains an UpdateDataDocsAction which automatically renders the Data Docs from the validation we're about to run
            "run_name_template": run_name_template,  # This will show up as the run name in the Data Docs viewer
        }

        # Test our checkpoint config syntax
        my_checkpoint = context.test_yaml_config(yaml.dump(checkpoint_config))

        # *We get a message that the checkpoint contains no validations. This is ok because we will pass them at runtime, as we see when we call context.run_checkpoint()

        # Add the checkpoint
        context.add_or_update_checkpoint(**checkpoint_config)


# COMMAND ----------


def run_ge(validations):
    validation_results = []
    for validation in validations:
        expectation_suite_name = validation["expectation_suite_name"]
        print(expectation_suite_name)

        checkpoint_result = context.run_checkpoint(
            checkpoint_name=checkpoint_name, validations=[validation]
        )

        validation_result = context.get_validation_result(expectation_suite_name)

        validation_results.append(validation_result)

    return validation_results


# COMMAND ----------


def generate_summarized_outputs(validation_results):
    # Intitialize empty dictionary to store our output metrics
    summarized_output = []

    # We aggregate total passing and failing expectations
    num_exp_pass = 0
    num_exp_fail = 0

    # For every expectation suite validation result, append success flag and statistics to our output. Suite name is the key
    for result in validation_results:
        # - - - Extract table name, success flag, and validation statistics - - -
        table_name = result["meta"]["active_batch_definition"]["data_asset_name"]
        success = result["success"]

        evaluated_tests = result["statistics"]["evaluated_expectations"]
        success_percent = result["statistics"]["success_percent"]
        successful_tests = result["statistics"]["successful_expectations"]
        unsuccessful_tests = result["statistics"]["unsuccessful_expectations"]
        expectation_types = []
        for expectation_result in result["results"]:
            expectation_type = expectation_result["expectation_config"][
                "expectation_type"
            ]
            expectation_success = expectation_result["success"]
            col_name = (
                expectation_result["expectation_config"]["kwargs"]["column"]
                if expectation_result["expectation_config"]["kwargs"].get("column")
                is not None
                else ""
            )
            expected_values = []
            for kwarg in expectation_result["expectation_config"]["kwargs"].keys():
                if "value" in kwarg.casefold():
                    expected_values.append(
                        f"{kwarg} : {expectation_result['expectation_config']['kwargs'][kwarg]}"
                    )

            observed_value = (
                expectation_result["result"]["observed_value"]
                if expectation_result["result"].get("observed_value") is not None
                else ""
            )
            test_name = (
                expectation_type
                if col_name == ""
                else f"{expectation_type}({col_name})"
            )
            expectation_types.append(
                {
                    "test_name": test_name,
                    "success": expectation_success,
                    "expected_value": "<br/>".join(expected_values),
                    "observed_value": observed_value,
                }
            )

        statistics = {
            "evaluated_tests": evaluated_tests,
            "success_percent": success_percent,
            "successful_tests": successful_tests,
            "unsuccessful_tests": unsuccessful_tests,
            "details": expectation_types,
        }

        num_exp_pass += successful_tests
        num_exp_fail += unsuccessful_tests

        # - - - Build URL pointing to the raw json file of our validation result - - -
        expectation_suite_name = f"{table_name}_expectation_suite"
        # We need to massage the time_executed a bit since the time in the result file have slightly differing formats than the directory name GE generates
        run_time = result["meta"]["run_id"]["run_time"]
        time_executed = f"{re.sub(r'[-:+]', '', run_time)[:-4]}Z"
        if len(result["results"]) > 0:
            batch_id = result["results"][0]["expectation_config"]["kwargs"]["batch_id"]
            raw_json_url = f"work/great-expectations/{data_source}/validations/{expectation_suite_name}/{run_name_template}/{time_executed}/{batch_id}.json"
            summarized_output.append(
                {
                    "table_name": table_name,
                    "success": success,
                    "statistics": statistics,
                    "path": raw_json_url,
                }
            )

        # validation_result_url = f'https://{storage_account_name}.dfs.core.windows.net/cdh/work/datahub/inprogress/{workflow_id}/data-quality/uncommitted/validations/{expectation_suite_name}/{run_name_template}/{time_executed}/{batch_id}.json'

    # Calculate some nice to have user defined summary metrics
    total_expectations = num_exp_pass + num_exp_fail
    pass_rate = (num_exp_pass / total_expectations) * 100
    fail_rate = (num_exp_fail / total_expectations) * 100

    # Append those metrics to our output dictionary with the key, 'summary'
    # output['summary'] = {'total_evaluated': total_expectations, 'pass_rate': pass_rate, 'fail_rate': fail_rate}
    # summarized_output['total_evaluated'] = total_expectations
    # summarized_output['pass_rate'] = pass_rate
    # summarized_output['fail_rate'] = fail_rate
    summarized_output = sorted(summarized_output, key=itemgetter("success"))

    summary_status = "Succeeded" if pass_rate == 100 else "Failed"
    summarized_output.append(
        {
            "table_name": "_summary",
            "total_evaluated": total_expectations,
            "status": summary_status,
            "pass_rate": pass_rate,
            "fail_rate": fail_rate,
        }
    )

    # Put our output in a dataframe so we can write it to storage and convert output to json object to return to orchestrator
    # output = json.dumps(output)
    # output_df = spark.createDataFrame([{'output': output}]).withColumn('time_processed', current_timestamp())

    # Sanity Check
    print(f"Total Expectations Evaluated: {total_expectations}")
    print(f"Pass Rate: {pass_rate:.2f}%")
    print(f"Fail Rate: {fail_rate:.2f}% \n")
    print(f"Output: \n {summarized_output} \n")
    print(f"Output DataFrame written to Storage:\n")

    return summarized_output
    # display(output_df)


# COMMAND ----------

success = True
error = ""
json_object = ""
try:
    spark_setup()
    context = get_context(project_config=data_context_config)

    print(
        "\n getting a list of tables to process and reading in the canonical manifest file...."
    )
    tables = cdh_helper.get_first_level_subfolders(source_folder_location)
    # read manifesst file as csv df
    df = (
        spark.read.format("csv")
        .option("inferSchema", True)
        .option("header", True)
        .option("sep", ",")
        .load(manifest_file_full_path)
    )

    # tables = tables[:2]
    print(tables)
    display(df)

    # Overview of our context and where various GE artifacts are stored
    # print(context)

    print("\n generating expectations....")
    generate_ge_expectations()

    print("\n setting up checkpoint....")
    setup_ge_checkpoint()

    print("\n generating batch requests....")
    batch_requests = generate_ge_batch_requests()
    print(batch_requests)

    print("\n generating validations....")
    validations = generate_ge_validation_requests(batch_requests)

    print("\n running ge....")
    validation_results = run_ge(validations)

    print("Validation Results: \n")
    print(validation_results)
    print(" \n")

    print("\n aggregating results....")
    summarized_output = generate_summarized_outputs(validation_results)

    json_object = json.dumps(summarized_output, indent=4)
    full_output_path = os.path.join(output_file_directory, "ge_staging_validation.json")
    dbutils.fs.put(full_output_path, json_object, True)
except Exception as ex:
    print(ex)
    success = False
    error = str(ex)

# COMMAND ----------

dbutils.notebook.exit(
    json.dumps(
        {
            "success": success,
            "output": json_object,
            "error": error,
        }
    )
)
