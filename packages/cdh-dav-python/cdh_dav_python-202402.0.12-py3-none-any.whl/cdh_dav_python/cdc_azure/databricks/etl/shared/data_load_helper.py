from datetime import datetime
from random import randint
import time
import json

from pyspark.dbutils import DBUtils
from pyspark.sql import SparkSession
from pyspark.sql.functions import *


spark = SparkSession.builder.getOrCreate()
dbutils = DBUtils(spark)


def isTableExists(tableName):
    try:
        if spark.catalog._jcatalog.tableExists(tableName):
            return True
        else:
            return False
    except Exception as err:
        return False


def cast_type(target_data_type, source_data_type):
    print("Target datatype:", target_data_type)
    print("Source datatype:", source_data_type)
    cast_type = "string"
    type = "forward"
    cast = {
        "bigint": ["cdhallint", "int", "tinyint"],
        "int": ["cdhallint", "tinyint"],
        "cdhallint": ["tinyint"],
        "double": ["int", "cdhallint", "tinyint", "decimal", "float"],
        "float": ["int", "cdhallint", "tinyint", "decimal", "double"],
        "timestamp": ["date"],
        "string": ["binary", "boolean"],
    }
    for key in cast:
        if source_data_type == key and target_data_type in cast[key]:
            print("cast forward")
            cast_type = key
            type = "forward"
        elif target_data_type == key and source_data_type in cast[key]:
            print("cast backward")
            cast_type = key
            type = "backward"
    return (cast_type, type)

def insert_process_logs(log_control_tb, process_name, logs_json):
    logs_json['process_name'] = process_name
    #print("logs_json:",logs_json)
    df = spark.read.json(spark.sparkContext.parallelize([json.dumps(logs_json)]))
    df = df.withColumn("process_start_time",col("process_start_time").cast("timestamp")).withColumn("process_end_time",col("process_end_time").cast("timestamp"))
    df.write.format("delta").option("mergeSchema", "true").mode("append").saveAsTable(log_control_tb)
    return True

def upCast(sourcedF):
    cast = {"double":["int", "smallint", "tinyint", "bigint", "cdhallint", "decimal", "float"],"timestamp":["date"]}
    schema_drift_json = []
    sourceSchemaJSON = {}
    for field in sourcedF.schema.fields:
        sourceSchemaJSON[field.name] = str(field.dataType.simpleString())
        #display(sourceSchemaJSON)
        if column in sourcedF.columns:
            for key in cast:
                if sourceSchemaJSON[column] in cast[Key]:
                    sourcedF = sourcedF.withColumn(column, col(column).cast(key))
                    schema_drift_json.append({"column": column,"column_old_type": sourceSchemaJSON[column],"column_new_type": key})
    return (sourcedF, schema_drift_json)


def dataTypedriftRewrite(
    sourcedF, targetdF, targetTable, partition_column,drift_manage_type, created_timestamp
):
    t1_schemas = []
    t2_schemas = []
    targetSchemaJSON = {}
    for field in sourcedF.schema.fields:
        t2_schemas.append(field.name + "," + str(field.dataType.simpleString()))
    for field in targetdF.schema.fields:
        t1_schemas.append(field.name + "," + str(field.dataType.simpleString()))
        targetSchemaJSON[field.name] = str(field.dataType.simpleString())
    missing_schemas = set(t2_schemas) - set(t1_schemas)
    schema_drift_json = []
    schema_update_type = "mergeSchema"
    cast_logic = ""
    for schema in missing_schemas:
        column = schema.split(",")[0]
        dataType = schema.split(",")[1]
        # print(column)
        if column in targetdF.columns:
            castType = cast_type(targetSchemaJSON[column], dataType)
            if castType[1] == "forward":
                targetdF = targetdF.withColumn(column, col(column).cast(castType[0]))
                sourcedF = sourcedF.withColumn(column, col(column).cast(castType[0]))
                if targetSchemaJSON[column] != "StringType":
                    schema_drift_json.append(
                        {
                            "column": column,
                            "column_old_type": targetSchemaJSON[column],
                            "column_new_type": castType[0],
                        }
                    )
                    schema_update_type = "overwriteSchema"
                    cast_logic = str(castType[0])
            elif castType[1] == "backward":
                sourcedF = sourcedF.withColumn(column, col(column).cast(castType[0]))
                cast_logic = str(castType[0])
    # print(targetdF.printSchema())
    # targetdF.show()
    #if len(schema_drift_json) >= 1:
    if len(schema_drift_json) >= 1 and drift_manage_type == 'apply':
        targetdF.write.partitionBy(partition_column).option(
            "delta.deletedFileRetentionDuration", "0 day"
        ).option(
            "delta.logRetentionDuration", "0 day"
        ).format(
            "delta"
        ).mode(
            "overwrite"
        ).option(
            "overwriteSchema", "true"
        ).saveAsTable(
            targetTable
        )
    return (sourcedF, schema_drift_json, schema_update_type, cast_logic)


def insert_delivery_control(
    dataset,
    database,
    reload_flag,
    delivery_date,
    delivery_control,
    delivery_type,
    paths,
    paths_files,
    paths_size,
    pipeline_run_type
):
    try:
        delivery_control_all = ""
        for path in paths:

            file_count = len(paths_files[path])
            file_size = paths_size[path]
            partitions = path.split("|")[1]
            path = path.split("|")[0]
            today_date = datetime.now()
            array = path.split("/")
            hist_database_name = database + "_history"
            tableName = array[len(array) - 1]
            delivery_control_id = spark.sql(
                f"SELECT MD5('{dataset}{database}{tableName}{delivery_type}{path}{delivery_date}{today_date}')"
            ).collect()[0][0]
            print("Table Name:", tableName)
            history_delivery_count = 0
            current_delivery_count = 0
            if reload_flag == "Y" and delivery_type == "full":
                sql = (
                    f"DELETE FROM "
                    + delivery_control
                    + " WHERE dataset_name = '"
                    + dataset
                    + "' AND table_name='"
                    + tableName
                    + "' AND database_name IN('"
                    + database
                    + "','"
                    + hist_database_name
                    + "') AND data_delivery_date = '"
                    + delivery_date
                    + "'"
                )
                # print(sql)
                spark.sql(sql)
            elif reload_flag == "Y" and delivery_type == "incremental":
                sql = (
                    f"DELETE FROM "
                    + delivery_control
                    + " WHERE dataset_name = '"
                    + dataset
                    + "' AND table_name='"
                    + tableName
                    + "' AND database_name = '"
                    + database
                    + "' AND data_delivery_date = '"
                    + delivery_date
                    + "'"
                )
                spark.sql(sql)
                # print(sql)
            current_delivery_count = spark.sql(
                f"SELECT 1 FROM  "
                + delivery_control
                + " WHERE dataset_name = '"
                + dataset
                + "' AND table_name='"
                + tableName
                + "' AND database_name = '"
                + database
                + "' AND data_delivery_date = '"
                + delivery_date
                + "' AND delivery_type ='"
                + delivery_type
                + "'"
            ).count()
            delivery_controlDF = (
                spark.createDataFrame(
                    [
                        [
                            delivery_control_id,
                            dataset,
                            database,
                            tableName,
                            delivery_type,
                            path,
                            delivery_date,
                            partitions,
                            today_date,
                            file_count,
                            file_size,
                            "",
                            "",
                            "",
                            "",
                        ]
                    ],
                    schema=[
                        "delivery_control_id",
                        "dataset_name",
                        "database_name",
                        "table_name",
                        "delivery_type",
                        "delivery_path",
                        "data_delivery_date",
                        "business_partitions",
                        "created_date",
                        "file_count",
                        "file_size",
                        "source_count",
                        "target_count",
                        "cdh_process_start_date",
                        "cdh_process_end_date"
                    ],
                )
                .withColumn("source_count", lit(None))
                .withColumn("target_count", lit(None))
                .withColumn("cdh_process_start_date", lit(None))
                .withColumn("cdh_process_end_date", lit(None))
            )
            # print(current_delivery_count)
			# This section we add current delivery control load when the pipeline run type flag is N and current_delivery_count is zero
            if current_delivery_count == 0 and ( pipeline_run_type == 'current' or pipeline_run_type == 'both') :
                # delivery_controlDF.repartition(1).write.format("delta").mode("append").saveAsTable(delivery_control)
                delivery_control_all = (
                    delivery_controlDF
                    if delivery_control_all == ""
                    else delivery_control_all.union(delivery_controlDF)
                )
            if delivery_type == "full":
                history_delivery_count = spark.sql(
                    f"SELECT *FROM  "
                    + delivery_control
                    + " WHERE dataset_name = '"
                    + dataset
                    + "' AND table_name='"
                    + tableName
                    + "' AND database_name = '"
                    + hist_database_name
                    + "'  AND data_delivery_date = '"
                    + delivery_date
                    + "'AND delivery_type = 'full'"
                ).count()
                delivery_controlDF = (
                    spark.createDataFrame(
                        [
                            [
                                delivery_control_id,
                                dataset,
                                hist_database_name,
                                tableName,
                                delivery_type,
                                path,
                                delivery_date,
                                partitions,
                                today_date,
                                file_count,
                                file_size,
                                "",
                                "",
                                "",
                                "",
                            ]
                        ],
                        schema=[
                            "delivery_control_id",
                            "dataset_name",
                            "database_name",
                            "table_name",
                            "delivery_type",
                            "delivery_path",
                            "data_delivery_date",
                            "business_partitions",
                            "created_date",
                            "file_count",
                            "file_size",
                            "source_count",
                            "target_count",
                            "cdh_process_start_date",
                            "cdh_process_end_date"
                        ],
                    )
                    .withColumn("source_count", lit(None))
                    .withColumn("target_count", lit(None))
                    .withColumn("cdh_process_start_date", lit(None))
                    .withColumn("cdh_process_end_date", lit(None))
                )
                # display(delivery_controlDF)
                # delivery_controlDF = delivery_controlDF.withColumn("database_name", hist_database_name)
                # print(history_delivery_count)
				# This section we add history delivery control load when history_delivery_count is zero
                if history_delivery_count == 0 and ( pipeline_run_type == 'history' or pipeline_run_type == 'both'):
                    # display(delivery_controlDF)
                    # delivery_controlDF.repartition(1).write.format("delta").mode("append").saveAsTable(delivery_control)
                    delivery_control_all = (
                        delivery_controlDF
                        if delivery_control_all == ""
                        else delivery_control_all.union(delivery_controlDF)
                    )
        delivery_control_all.repartition(1).write.format("delta").mode(
            "append"
        ).saveAsTable(delivery_control)
    except Exception as err:
        print(err)
        print(
            "Exception occurred while inserting data into the delivery control table for dataset "
            + str(dataset)
            + " "
        )

        
def insert_raw_delivery_metrics_table_level(data_source,delivery_date,workflow_id,canonical_final_dest_path):
    time_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    raw_delivery_metrics_table_name = "cdh_engineering.cdm_raw_delivery_metrics_table_level"
    df = spark.read.format("csv") \
                    .option("inferSchema", True) \
                    .option("header", True) \
                    .option("sep",",") \
                    .load(canonical_final_dest_path)
    
    dataCollect = df.collect()
    sql_header = f"INSERT INTO {raw_delivery_metrics_table_name} (dataset_name,data_delivery_date,workflow_id,table_name,row_count,created_date) VALUES \n"
    sql_array = []
    for row in dataCollect:
        table_name = row["table_name"]
        row_count = row["row_count"]
        sql_array.append(f" ('{data_source}', '{delivery_date}', '{workflow_id}','{table_name}',{row_count},'{time_now}')")
    
    
    sql = f"DELETE FROM {raw_delivery_metrics_table_name} WHERE dataset_name = '{data_source}' AND data_delivery_date = '{delivery_date}'"
    spark.sql(sql)
    sql =  sql_header + ", \n".join(sql_array) + ";"
    print(sql)  
    spark.sql(sql)        
