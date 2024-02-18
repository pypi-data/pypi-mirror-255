# Databricks notebook source
# mandatory parameters and names. The orchestrator will always pass these
dbutils.widgets.text("data_source", "")
dbutils.widgets.text("delivery_date", "")
dbutils.widgets.text("request_id", "")
dbutils.widgets.text("workflow_id", "ISOLATED")
dbutils.widgets.text("storage_account_name", "")

# optional parameters. Add as many as needed for execution of notebook.

# where are we reading the files from
dbutils.widgets.text("source_folder", "")
# where are we writing the files to
dbutils.widgets.text("destination_folder", "")
# staging database name
dbutils.widgets.text("stage_database_name", "")

# what is the file extension for the files we are copying eg for covid19_20204_genlab.txt.gz it will be gz
dbutils.widgets.text("source_files_extension", "")
# what is the character we split the file name on. eg for covid19_20204_genlab.txt.gz it will be _
# dbutils.widgets.text('file_name_split_character', '')
# Regex array for extracting the table name from the file name. System will remove the matches to end up with the table name
dbutils.widgets.text("table_name_regex_replace", "")  # for pcc _.*$

# what type of files are we converting from - csv or json
dbutils.widgets.dropdown("source_files_format", "csv", ["csv", "parquet"])
# does the source file contain header
dbutils.widgets.text("source_files_has_header", "")
# what is the delimiter for the source files
dbutils.widgets.text("source_files_delimiter", "")
# for csv files, is it multiline (OMOP ABFM)
dbutils.widgets.text("source_files_is_multiline", "True")
dbutils.widgets.text("source_files_escape_character", "")
dbutils.widgets.text("source_files_infer_schema", "True")


# which tables to exclude from attempting to convert to parquet eg manifest etc- comma separated - blank means None
dbutils.widgets.text("exclude_tables_from_parquet_conversion", "")

# which tables should be partitioned - comma separated - blank means all
dbutils.widgets.text("partitioned_tables_include", "")
# which tables should NOT be partitioned - comma separated - blank means None will be excluded. 'all' means to exclude all tables from partitioning
dbutils.widgets.text("partitioned_tables_exclude", "")

# partitioning
# what is the partiioning strategy being used
dbutils.widgets.dropdown(
    "partitioning_scheme", "none", ["none", "file_based", "column_based"]
)
# if file based - what regex to apply to get the datetime component
dbutils.widgets.text("partitioning_scheme_file_based_datetime_extract_regex", "")
# if there are multiple matches when applying the above regex, which index in the array do we get.
# eg for premier covid19_20192_patbill when the above regex is applied it gives back two elements 19 and 20192. We want the 2nd element (0 based) hence 1
dbutils.widgets.text(
    "partitioning_scheme_file_based_datetime_extract_index_after_regex", "0"
)
# if column is used for extracting datetime - what is the column name eg part_mth for HV
dbutils.widgets.text("partitioning_scheme_column_based_table_column_name", "")

# partitioning_scheme_column_based_partioning_column_name
# year
# if table is being partioned then at what index is the datetime string we want to extract
# dbutils.widgets.text('datetime_index_after_file_name_split', '')
# partitioning
dbutils.widgets.text("partition_by", "")
dbutils.widgets.text("year_start_index", "")
dbutils.widgets.text("year_length", "")
dbutils.widgets.text("quarter_start_index", "")
dbutils.widgets.text("quarter_length", "")
dbutils.widgets.text("month_start_index", "")
dbutils.widgets.text("month_length", "")

# table renamings - format <table1_original_name>=<table1_new_name>|<table2_original_name>=<table2_new_name>
dbutils.widgets.text("table_renaming_map", "")


# COMMAND ----------

from pyspark.sql.types import *
from pyspark.sql.functions import *
from pathlib import Path
from datetime import datetime, timezone
import os
import re
import json
from multiprocessing.pool import ThreadPool
import multiprocessing as mp
import cdc_azure.databricks.etl.shared.cdh_helper as cdh_helper

# COMMAND ----------

data_source = dbutils.widgets.get("data_source")
delivery_date = dbutils.widgets.get("delivery_date")
request_id = dbutils.widgets.get("request_id")
workflow_id = dbutils.widgets.get("workflow_id")
storage_account_name = dbutils.widgets.get("storage_account_name")
destination_folder = dbutils.widgets.get("destination_folder")
stage_database_name = dbutils.widgets.get("stage_database_name")
source_files_extension = dbutils.widgets.get("source_files_extension")
source_folder = dbutils.widgets.get("source_folder")
source_files_format = dbutils.widgets.get("source_files_format")
source_files_delimiter = dbutils.widgets.get("source_files_delimiter")
source_files_has_header = dbutils.widgets.get("source_files_has_header")
source_files_is_multiline = dbutils.widgets.get("source_files_is_multiline")
source_files_escape_character = dbutils.widgets.get("source_files_escape_character")
source_files_infer_schema = dbutils.widgets.get("source_files_infer_schema")

table_name_regex_replace = dbutils.widgets.get("table_name_regex_replace")
exclude_tables_from_parquet_conversion = dbutils.widgets.get(
    "exclude_tables_from_parquet_conversion"
)
partitioned_tables_include = dbutils.widgets.get("partitioned_tables_include")
partitioned_tables_exclude = dbutils.widgets.get("partitioned_tables_exclude")
# partitioning options
partition_by = dbutils.widgets.get("partition_by")  # ["year", "quarter"]
year_start_index = dbutils.widgets.get("year_start_index")  # "1"
year_length = dbutils.widgets.get("year_length")  # "4"
quarter_start_index = dbutils.widgets.get("quarter_start_index")  # "5"
quarter_length = dbutils.widgets.get("quarter_length")  # "1"
month_start_index = dbutils.widgets.get("month_start_index")  # ""
month_length = dbutils.widgets.get("month_length")  # ""
table_renaming_map = dbutils.widgets.get("table_renaming_map")

partitioning_scheme = dbutils.widgets.get("partitioning_scheme")
partitioning_scheme_file_based_datetime_extract_regex = dbutils.widgets.get(
    "partitioning_scheme_file_based_datetime_extract_regex"
)
partitioning_scheme_file_based_datetime_extract_index_after_regex = dbutils.widgets.get(
    "partitioning_scheme_file_based_datetime_extract_index_after_regex"
)
partitioning_scheme_column_based_table_column_name = dbutils.widgets.get(
    "partitioning_scheme_column_based_table_column_name"
)

table_name_regex_replace_array = (
    []
    if table_name_regex_replace is None or len(table_name_regex_replace) == 0
    else table_name_regex_replace.split(",")
)

exclude_tables_from_parquet_conversion_array = (
    []
    if exclude_tables_from_parquet_conversion is None
    or len(exclude_tables_from_parquet_conversion) == 0
    else exclude_tables_from_parquet_conversion.split(",")
)
exclude_tables_from_parquet_conversion_array = [
    item.strip().lower() for item in exclude_tables_from_parquet_conversion_array
]

partitioned_tables_include_array = (
    []
    if partitioned_tables_include is None or len(partitioned_tables_include) == 0
    else partitioned_tables_include.split(",")
)
partitioned_tables_include_array = [
    item.strip().lower() for item in partitioned_tables_include_array
]

partitioned_tables_exclude_array = (
    []
    if partitioned_tables_exclude is None or len(partitioned_tables_exclude) == 0
    else partitioned_tables_exclude.split(",")
)
partitioned_tables_exclude_array = [
    item.strip().lower() for item in partitioned_tables_exclude_array
]

partition_by_array = (
    [] if partition_by is None or len(partition_by) == 0 else partition_by.split(",")
)
partition_by_array = [item.strip().lower() for item in partition_by_array]

table_renaming_map_array = (
    []
    if table_renaming_map is None or len(table_renaming_map) == 0
    else table_renaming_map.split("|")
)
table_renaming_map_dict = {}
if len(table_renaming_map) > 0:
    for item in table_renaming_map_array:
        table_renaming_map_dict[item.split("=")[0]] = item.split("=")[1]

# partitioning_scheme_column_based_table_column_map_array = [] if partitioning_scheme_column_based_table_column_map is None or len(partitioning_scheme_column_based_table_column_map) == 0 else #partitioning_scheme_column_based_table_column_map.split('|')

# partitioning_scheme_column_based_table_column_map_dict = {}
# if len(partitioning_scheme_column_based_table_column_map) > 0:
#     for item in partitioning_scheme_column_based_table_column_map_array :
#         partitioning_scheme_column_based_table_column_map_dict[item.split("=")[0]] = item.split("=")[1]


print(f"partitioning_scheme : {partitioning_scheme}")
print(f"table_name_regex_replace_array : {table_name_regex_replace_array}")
print(
    f"exclude_tables_from_parquet_conversion_array : {exclude_tables_from_parquet_conversion_array}"
)
print(f"partitioned_tables_include_array : {partitioned_tables_include_array}")
print(f"partitioned_tables_exclude_array : {partitioned_tables_exclude_array}")
print(f"table_renaming_map_dict : {table_renaming_map_dict}")
# print(f"partitioning_scheme_column_based_table_column_map_dict : {partitioning_scheme_column_based_table_column_map_dict}")


file_based_partition_dates_df_schema = StructType(
    [
        StructField("file_path", StringType(), False),
        StructField("file_name", StringType(), False),
        StructField("date_time", StringType(), False),
        StructField("year", ShortType(), False),
        StructField("quarter", ShortType(), False),
        StructField("month", ShortType(), False),
    ]
)
emptyRDD = spark.sparkContext.emptyRDD()
file_based_partition_dates_df = spark.createDataFrame(
    emptyRDD, file_based_partition_dates_df_schema
)

if stage_database_name is None or stage_database_name == "":
    stage_database_name = f"cdh_{data_source}_stage"

adlsContainerName = "cdh"
adlsFolderName = "raw"
baseLocation = (
    "abfss://" + "cdh" + "@" + storage_account_name + ".dfs.core.windows.net/"
)
output_file_directory = os.path.join(
    baseLocation, f"work/datahub/completed/{data_source}/{workflow_id}/misc/"
)
audit_log_output_array = []

# TODO: this may need to be a parameter with default value as True
partitioning_scheme_column_based_drop_original_column = False

# COMMAND ----------


def should_table_be_partitioned(table_name):

    if partitioning_scheme.casefold() == "none":
        return False

    if (
        len(partitioned_tables_include_array) == 0
        and len(partitioned_tables_exclude_array) == 0
    ):
        return True

    if table_name.casefold() in partitioned_tables_include_array:
        return True

    if (
        table_name.casefold() in partitioned_tables_exclude_array
        or "all" in partitioned_tables_exclude_array
    ):
        return False

    return True


def get_table_to_source_files_map(source_files_paths: any):
    table_to_files = {}
    for source_file_path in source_files_paths:
        file_name_with_extension = os.path.basename(source_file_path)
        if file_name_with_extension != "":
            file_name = Path(file_name_with_extension).stem
            file_extension = file_name_with_extension.split(".")[-1]
            if file_extension.casefold() == source_files_extension.casefold():
                table_name = file_name
                for index in table_name_regex_replace_array:
                    table_name = re.sub(index, "", table_name)

                if table_renaming_map_dict.get(table_name) is not None:
                    new_name = table_renaming_map_dict[table_name]
                    print(f"Renaming {table_name} as {new_name}")
                    table_name = new_name

                if (
                    table_name.casefold()
                    not in exclude_tables_from_parquet_conversion_array
                ):
                    if table_name in table_to_files.keys():
                        table_source_files = table_to_files.get(table_name)
                        table_source_files.append(source_file_path)
                    else:
                        table_to_files[table_name] = [source_file_path]
                else:
                    print(f"Excluded for conversion - {table_name}")

    # print(f"Files to process : {table_to_files}")
    return table_to_files


def copy_file(source_to_dest_tuple):
    print(source_to_dest_tuple)
    dbutils.fs.cp(source_to_dest_tuple[0], source_to_dest_tuple[1])


# COMMAND ----------


def get_file_count_and_size_in_mb(files: [str] = [], directory: str = ""):
    if len(files) > 0:
        size_bytes = 0
        for a_file in files:
            info = dbutils.fs.ls(a_file)[0]
            size_bytes = size_bytes + info.size

        return len(files), size_bytes / 1000000

    if len(directory) > 0:
        all_files = list(cdh_helper.get_file_info_in_directory(directory))
        size_bytes = 0
        for a_file in all_files:
            size_bytes = size_bytes + a_file.size

        return len(all_files), size_bytes / 1000000


def save_metadata_to_db():
    ingest_table = "cdh_engineering.cdm_process_transform"
    time_now = datetime.now(tz=timezone.utc)

    spark.sql(
        f"DELETE from {ingest_table} where workflow_id= '{workflow_id}' and dataset_name='{data_source}'"
    )
    sql_header = f"""insert into {ingest_table}(workflow_id , dataset_name ,table_name, source_path , source_file_count ,source_file_format, source_file_size_mb ,target_path ,  target_file_count ,target_file_format, target_file_size_mb ,start_time , end_time , created_time ) values \n"""
    sql_array = []
    for row in audit_log_output_array:
        table_name = row["table_name"]
        source_path = row["source_path"]
        source_file_count = row["source_file_count"]
        source_file_format = row["source_file_format"]
        source_file_size_mb = row["source_file_size_mb"]
        target_path = row["target_path"]
        target_file_count = row["target_file_count"]
        target_file_format = row["target_file_format"]
        target_file_size_mb = row["target_file_size_mb"]
        start_time = row["start_time"]
        end_time = row["end_time"]

        sql_array.append(
            f" ('{workflow_id}', '{data_source}',\
                            '{table_name}',\
                            '{source_path}',\
                            '{source_file_count}',\
                            '{source_file_format}',\
                            '{source_file_size_mb}',\
                            '{target_path}',\
                            '{target_file_count}',\
                            '{target_file_format}',\
                            '{target_file_size_mb}',\
                            '{start_time}',\
                            '{end_time}',\
                            '{time_now}')"
        )

    sql = sql_header + ", \n".join(sql_array) + ";"
    print(f"\n{sql}")
    spark.sql(sql)


# COMMAND ----------


def generate_file_name_to_year_quarter_month_partition_dataframe(source_files_paths):
    source_file_partition_array = []

    for source_files_path in source_files_paths:
        file_name_with_extension = source_files_path.split("/")[-1]
        file_name = file_name_with_extension.split(".")[0]
        date_time_re = re.findall(
            partitioning_scheme_file_based_datetime_extract_regex, file_name
        )
        date_time = (
            date_time_re[
                int(partitioning_scheme_file_based_datetime_extract_index_after_regex)
            ]
        ).strip()
        if year_start_index is not None and len(year_start_index) > 0:
            year = (
                date_time[int(year_start_index) : int(year_length)]
                if int(year_length) > 0
                else date_time[int(year_start_index)]
            )
        else:
            year = 0
        if quarter_start_index is not None and len(quarter_start_index) > 0:
            quarter = (
                date_time[int(quarter_start_index) : int(quarter_length)]
                if int(quarter_length) > 0
                else date_time[int(quarter_start_index)]
            )
        else:
            quarter = 0
        if month_start_index is not None and len(month_start_index) > 0:
            month = (
                date_time[int(month_start_index) : int(month_length)]
                if int(month_length) > 0
                else date_time[int(month_start_index)]
            )
        else:
            month = 0

        if len(year) == 2:
            year = "20" + year

        source_file_partition_array.append(
            [
                source_files_path,
                file_name,
                date_time,
                int(year),
                int(quarter),
                int(month),
            ]
        )

    df_dates = spark.createDataFrame(
        data=source_file_partition_array, schema=file_based_partition_dates_df_schema
    )
    # display(df_dates)
    return df_dates


def csv_to_parquet_transform(source_to_dest):
    table_name = source_to_dest[0]
    badRecordsPath = os.path.join(output_file_directory, "badRecords", table_name)
    start_time = datetime.now(tz=timezone.utc)
    try:
        source_files = source_to_dest[1]

        print(f"{table_name}: Starting processing ")

        clean_staging_table_and_directory(table_name)
        df = (
            spark.read.options(
                delimiter=source_files_delimiter,
                header=source_files_has_header,
                inferSchema=source_files_infer_schema,
                multiline=source_files_is_multiline,
                escape=source_files_escape_character,
                badRecordsPath=badRecordsPath,
            )
            .csv(source_files)
            .withColumn("full_input_file", input_file_name())
        )

        # for col in df.columns:
        #     df = df.withColumnRenamed(col, col.lower())

        destination_table_folder = os.path.join(
            baseLocation, destination_folder, table_name
        )
        partition_and_save_staging_table(
            df=df,
            table_name=table_name,
            source_files=source_files,
            destination_table_folder=destination_table_folder,
        )

        end_time = datetime.now(tz=timezone.utc)
        src_file_count, src_file_size_mb = get_file_count_and_size_in_mb(
            files=source_files
        )
        dest_file_count, dest_file_size_mb = get_file_count_and_size_in_mb(
            directory=destination_table_folder
        )
        audit_entry = {
            "table_name": table_name,
            "source_path": source_folder,
            "source_file_count": src_file_count,
            "source_file_format": source_files_format,
            "source_file_size_mb": src_file_size_mb,
            "target_path": os.path.join(destination_folder, table_name),
            "target_file_count": dest_file_count,
            "target_file_format": "parquet",
            "target_file_size_mb": dest_file_size_mb,
            "start_time": start_time,
            "end_time": end_time,
        }

        audit_log_output_array.append(audit_entry)

        print(f"\n {audit_entry}")
    except:
        print(f"{table_name}: ERROR ")
        raise


def parquet_to_parquet_transform(source_to_dest):
    table_name = source_to_dest[0]
    source_path = source_to_dest[1]

    start_time = datetime.now(tz=timezone.utc)
    clean_staging_table_and_directory(table_name)
    df = spark.read.parquet(source_path).withColumn(
        "full_input_file", input_file_name()
    )
    destination_table_folder = os.path.join(
        baseLocation, destination_folder, table_name
    )
    partition_and_save_staging_table(
        df=df,
        table_name=table_name,
        source_files=None,
        destination_table_folder=destination_table_folder,
    )

    end_time = datetime.now(tz=timezone.utc)
    src_file_count, src_file_size_mb = get_file_count_and_size_in_mb(
        directory=source_path
    )
    dest_file_count, dest_file_size_mb = get_file_count_and_size_in_mb(
        directory=destination_table_folder
    )
    audit_entry = {
        "table_name": table_name,
        "source_path": source_path,
        "source_file_count": src_file_count,
        "source_file_format": source_files_format,
        "source_file_size_mb": src_file_size_mb,
        "target_path": os.path.join(destination_folder, table_name),
        "target_file_count": dest_file_count,
        "target_file_format": "parquet",
        "target_file_size_mb": dest_file_size_mb,
        "start_time": start_time,
        "end_time": end_time,
    }

    audit_log_output_array.append(audit_entry)

    print(f"\n {audit_entry}")


def clean_staging_table_and_directory(table_name: str):
    destination_table_folder = os.path.join(
        baseLocation, destination_folder, table_name
    )
    drop_table_sql = f"DROP TABLE IF EXISTS {stage_database_name}.{table_name}"
    spark.sql(drop_table_sql)
    dbutils.fs.rm(destination_table_folder, True)
    print(
        f"Finished dropping database and deleting directory: {destination_table_folder}"
    )


def partition_and_save_staging_table(
    df: any, table_name: str, source_files: any, destination_table_folder: str
):
    do_partition_table = should_table_be_partitioned(table_name)
    # destination_table_folder = os.path.join(baseLocation,destination_folder,table_name)
    if do_partition_table:
        print(f"{table_name}: table should be partitioned.")
        if partitioning_scheme.casefold() == "file_based":
            listColumns = df.columns
            listColumns = [col.casefold() for col in listColumns]

            if "year" in listColumns:
                print(
                    f"{table_name}: year column exists already. Using the existing column."
                )
                df2 = df
                df2 = df2.drop("full_input_file").drop("file_path")
            else:
                file_based_partition_dates_df = (
                    generate_file_name_to_year_quarter_month_partition_dataframe(
                        source_files
                    )
                )
                df2 = df.join(
                    file_based_partition_dates_df,
                    df.full_input_file == file_based_partition_dates_df.file_path,
                    "leftouter",
                )
                df2 = (
                    df2.drop("full_input_file")
                    .drop("file_path")
                    .drop("file_name")
                    .drop("date_time")
                )
                df2 = (
                    df2.drop("quarter") if "quarter" not in partition_by_array else df2
                )
                df2 = df2.drop("month") if "month" not in partition_by_array else df2

            df2.write.format("parquet").partitionBy(partition_by_array).mode(
                "overwrite"
            ).option("path", destination_table_folder).saveAsTable(
                f"{stage_database_name}.{table_name}"
            )

        if partitioning_scheme.casefold() == "column_based":
            if year_start_index is not None and len(year_start_index) > 0:
                df = df.withColumn(
                    "year",
                    substring(
                        partitioning_scheme_column_based_table_column_name,
                        int(year_start_index),
                        int(year_length),
                    ).cast("int"),
                )

            if quarter_start_index is not None and len(quarter_start_index) > 0:
                df = df.withColumn(
                    "quarter",
                    substring(
                        partitioning_scheme_column_based_table_column_name,
                        int(quarter_start_index),
                        int(quarter_length),
                    ).cast("int"),
                )

            if month_start_index is not None and len(month_start_index) > 0:
                df = df.withColumn(
                    "month",
                    substring(
                        partitioning_scheme_column_based_table_column_name,
                        int(month_start_index),
                        int(month_length),
                    ).cast("int"),
                )

            if partitioning_scheme_column_based_drop_original_column == True:
                df = df.drop(partitioning_scheme_column_based_table_column_name)

            df = df.drop("full_input_file")
            df.write.format("parquet").partitionBy(partition_by_array).mode(
                "overwrite"
            ).option("path", destination_table_folder).saveAsTable(
                f"{stage_database_name}.{table_name}"
            )

    else:
        print(f"{table_name}: table should NOT be partitioned.")
        df = df.drop("full_input_file")
        df.write.format("parquet").mode("overwrite").option(
            "path", destination_table_folder
        ).saveAsTable(f"{stage_database_name}.{table_name}")

    # df.show(2, False)
    # print(f'{table_name}: Assigning owner permissions on Hive Table ')
    # table_sql = f"ALTER TABLE {stage_database_name}.`{table_name}`  OWNER TO `gp-u-EDAV-CDH-ADMIN-AAD`;"
    # spark.sql(table_sql)
    print(f"{table_name}: Finished processing ")


# COMMAND ----------


def process():
    source_folder_location = f"abfss://{adlsContainerName}@{storage_account_name}.dfs.core.windows.net/{source_folder}"
    full_output_path = os.path.join(output_file_directory, "_files_to_table_map.json")
    if source_files_format.casefold() == "csv":
        source_files_paths = cdh_helper.get_all_files_in_directory(
            source_folder_location
        )
        source_to_dest_map = get_table_to_source_files_map(source_files_paths)
        source_to_dest_list = list(source_to_dest_map.items())
        print(f"\nCSV source_to_dest_list saved to : {full_output_path} \n")
        dbutils.fs.put(full_output_path, json.dumps(source_to_dest_list), True)

        if partitioning_scheme.casefold() == "file_based":
            print(
                f"\nfile_based partioning. \n\t year from {year_start_index} with length {year_length} \n\t quarter from {quarter_start_index} with length {quarter_length} \n\t month from {month_start_index} with length {month_length} \n"
            )

        pool = ThreadPool(mp.cpu_count())
        opt = pool.map(csv_to_parquet_transform, source_to_dest_list)
    elif source_files_format.casefold() == "parquet":
        tables = cdh_helper.get_first_level_subfolders(source_folder_location)
        table_to_table_location = {}
        for table in tables:
            table_to_table_location[table] = os.path.join(source_folder_location, table)

        table_to_table_location_list = list(table_to_table_location.items())
        print(f"\nParquet tables map saved to : {full_output_path} \n")
        dbutils.fs.put(full_output_path, json.dumps(table_to_table_location_list), True)
        pool = ThreadPool(mp.cpu_count())
        opt = pool.map(parquet_to_parquet_transform, table_to_table_location_list)

    else:
        raise Exception(f"file format {source_files_format} is not supported.")

    print(f"\n audit_log_output_array: {audit_log_output_array}")
    save_metadata_to_db()


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
