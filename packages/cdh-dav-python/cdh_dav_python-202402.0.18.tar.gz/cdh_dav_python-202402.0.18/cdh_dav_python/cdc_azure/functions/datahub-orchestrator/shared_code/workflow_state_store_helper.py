import logging
import uuid
from datetime import datetime, timezone
from databricks import sql
from shared_code import app_config


def __get_header_sql(data_source: str, workflow_id: str, delivery_date: str, config_json: any):
    time_now = datetime.now(tz=timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    tracking_status = config_json["tracking"]["status"]
    tracking_start_utc = config_json["tracking"]["start_utc"]
    # datetime.now(tz=timezone.utc)
    tracking_end_utc = config_json["tracking"]["end_utc"] if config_json["tracking"].get(
        "end_utc") is not None else "SHOULD_BE_NULL"
    triggerred_by = config_json["triggerred_by"] if config_json.get(
        "triggerred_by") is not None else ""
    target_database = config_json["target_database"] if config_json.get(
        "target_database") is not None else ""

    upsert_sql = f"""MERGE INTO cdh_engineering.etl_workflow_header as target
        USING ( select
        '{data_source}' as dataset_name,'{delivery_date}' as  data_delivery_date ,
         '{workflow_id}' as workflow_id, '{tracking_status}' as tracking_status , 
          '{tracking_start_utc}' as tracking_start_utc, '{tracking_end_utc}' as tracking_end_utc,
          '{triggerred_by}' as triggerred_by, '{target_database}' as target_database
        )as source
        ON source.workflow_id = target.workflow_id
        WHEN MATCHED THEN
          UPDATE SET
            dataset_name = source.dataset_name,
            data_delivery_date = source.data_delivery_date,
            tracking_status = source.tracking_status,
            tracking_start_utc = source.tracking_start_utc,
            tracking_end_utc = source.tracking_end_utc,
            workflow_id = source.workflow_id,
            triggerred_by = source.triggerred_by,
            target_database = source.target_database,
            last_updated_date_utc = '{time_now}'
            
        WHEN NOT MATCHED
          THEN INSERT (
            dataset_name,
            data_delivery_date,
            tracking_status,
            tracking_start_utc,
            tracking_end_utc,
            workflow_id,
            last_updated_date_utc,
            triggerred_by,
            target_database
          )
          VALUES (
            source.dataset_name,
            source.data_delivery_date,
            source.tracking_status,
            source.tracking_start_utc,
            source.tracking_end_utc,
            source.workflow_id,
            '{time_now}',
            triggerred_by,
            target_database
  )"""

    upsert_sql = upsert_sql.replace("'SHOULD_BE_NULL'", "null")
    return upsert_sql


def __get_detail_sql(data_source: str, workflow_id: str, delivery_date: str, config_json: any):
    time_now = datetime.now(tz=timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    services = config_json["services"]
    sql_array = []
    for service in services:
        service_name = service["display_name"]
        if service.get("tracking") is not None:
            tracking_status = service["tracking"]["status"]
            tracking_start_utc = service["tracking"]["start_utc"]
            tracking_end_utc = service["tracking"]["end_utc"] if service.get("tracking") is not None and service[
                "tracking"].get("end_utc") is not None else "SHOULD_BE_NULL"
            tracking_request_id = service["tracking"]["request_id"]
            tracking_response_id = service["tracking"]["response_id"] if service["tracking"].get(
                "response_id") is not None else ""

            display_name = service["display_name"]
            target_system = service["target_system"]
            target_resource_name = service["target_resource_name"]

            sql_array.append(
                f"""SELECT '{data_source}' as dataset_name, '{delivery_date}' as data_delivery_date, 
                '{workflow_id}' as workflow_id, '{display_name}' as display_name, '{target_system}' as target_system,
                '{target_resource_name}' as target_resource_name, '{tracking_status}' as tracking_status, 
                '{tracking_start_utc}' as tracking_start_utc, '{tracking_end_utc}' as tracking_end_utc,
                '{tracking_request_id}' as tracking_request_id,'{tracking_response_id}' as tracking_response_id
                \n                
                """
            )

    value_sql = "UNION \n".join(sql_array)
    value_sql = value_sql.replace("'SHOULD_BE_NULL'", "null")

    upsert_sql = f"""MERGE INTO cdh_engineering.etl_workflow_service as target
            USING ( {value_sql}
            )as source
            ON source.workflow_id = target.workflow_id and source.tracking_request_id = target.tracking_request_id
            WHEN MATCHED THEN
              UPDATE SET
                dataset_name = source.dataset_name,
                data_delivery_date = source.data_delivery_date,
                workflow_id = source.workflow_id,
                display_name = source.display_name,
                target_system = source.target_system,
                target_resource_name = source.target_resource_name,
                tracking_status = source.tracking_status,
                tracking_start_utc = source.tracking_start_utc,
                tracking_end_utc = source.tracking_end_utc,
                tracking_request_id = source.tracking_request_id,
                tracking_response_id = source.tracking_response_id,                
                last_updated_date_utc = '{time_now}'

            WHEN NOT MATCHED
              THEN INSERT (
                dataset_name,
                data_delivery_date ,
                workflow_id,
                display_name ,
                target_system ,
                target_resource_name,
                tracking_status,
                tracking_start_utc,
                tracking_end_utc ,
                tracking_request_id, 
                tracking_response_id,
                last_updated_date_utc 
              )
              VALUES (
                source.dataset_name,
                source.data_delivery_date ,
                source.workflow_id,
                source.display_name ,
                source.target_system ,
                source.target_resource_name,
                source.tracking_status,
                source.tracking_start_utc,
                source.tracking_end_utc ,
                source.tracking_request_id, 
                source.tracking_response_id,
                '{time_now}'
      )"""
    return upsert_sql


def upsert_workflow_status(data_source: str, workflow_id: str, delivery_date: str, config_json: any):
    try:
        header_sql = __get_header_sql(data_source=data_source, workflow_id=workflow_id, delivery_date=delivery_date,
                                      config_json=config_json)

        detail_sql = __get_detail_sql(data_source=data_source, workflow_id=workflow_id, delivery_date=delivery_date,
                                      config_json=config_json)

        logging.info(f"{workflow_id}: upsert_workflow_status header upsert: {header_sql}")
        logging.info(f"{workflow_id}: upsert_workflow_status detail upsert: {detail_sql}")
        with sql.connect(server_hostname=app_config.DATABRICKS_SERVER_HOSTNAME,
                         http_path=app_config.DATABRICKS_HTTP_PATH,
                         access_token=app_config.DATABRICKS_TOKEN) as connection:
            with connection.cursor() as cursor:
                cursor.execute(header_sql)
                cursor.execute(detail_sql)
    except Exception as ex:
        logging.error(f"[{workflow_id}]Error calling upsert_workflow_status. \n \n error: " + str(ex))


def insert_scheduled_status(data_source: str, workflow_id: str, delivery_date: str, service_json: any):
    request_id = service_json["tracking"]["request_id"]
    prevent_run_window_start_time_et = service_json["schedule"]["prevent_run_window_start_time_et"]
    prevent_run_window_end_time_et = service_json["schedule"]["prevent_run_window_end_time_et"]
    display_name = service_json["display_name"]
    target_system = service_json["target_system"]
    target_resource_name = service_json["target_resource_name"]
    time_now = datetime.now(tz=timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')

    delete_sql = f"""delete from cdh_engineering.etl_workflow_service_scheduled
                    where workflow_id = '{workflow_id}' and request_id = '{request_id}'"""

    insert_sql = f"""insert into cdh_engineering.etl_workflow_service_scheduled
                (dataset_name,
                data_delivery_date,
                workflow_id,
                request_id,
                display_name,
                target_system,
                target_resource_name,
                prevent_run_window_start_time_et,
                prevent_run_window_end_time_et,
                processed_id,
                last_updated_date_utc)
                values('{data_source}',
                        '{delivery_date}',
                        '{workflow_id}',
                        '{request_id}',
                        '{display_name}',
                        '{target_system}',
                        '{target_resource_name}',
                        '{prevent_run_window_start_time_et}',
                        '{prevent_run_window_end_time_et}',
                        null,
                        '{time_now}')"""

    logging.info(f"{workflow_id}: insert_scheduled_status delete: {delete_sql}")
    logging.info(f"{workflow_id}: insert_scheduled_status insert: {insert_sql}")
    with sql.connect(server_hostname=app_config.DATABRICKS_SERVER_HOSTNAME,
                     http_path=app_config.DATABRICKS_HTTP_PATH,
                     access_token=app_config.DATABRICKS_TOKEN) as connection:
        with connection.cursor() as cursor:
            cursor.execute(delete_sql)
            cursor.execute(insert_sql)


def get_expired_scheduled_services():
    lock_id = uuid.uuid4().hex
    lock_rows_sql = f"""update 
                    cdh_engineering.etl_workflow_service_scheduled
                    set processed_id = '{lock_id}', last_updated_date_utc = now()
                    where request_id in (select request_id 
                                         from cdh_engineering.etl_workflow_service_scheduled 
                                         where from_utc_timestamp(now(), 'US/Eastern') > prevent_run_window_end_time_et
                                         and processed_id is null
                                         );
                     """

    query_sql = f""" select dataset_name as data_source, workflow_id, request_id,processed_id
                         from cdh_engineering.etl_workflow_service_scheduled
                         where processed_id = '{lock_id}'
    """

    responses = []
    with sql.connect(server_hostname=app_config.DATABRICKS_SERVER_HOSTNAME,
                     http_path=app_config.DATABRICKS_HTTP_PATH,
                     access_token=app_config.DATABRICKS_TOKEN) as connection:
        with connection.cursor() as cursor:
            cursor.execute(lock_rows_sql)
            cursor.execute(query_sql)
            result = cursor.fetchall()
            for row in result:
                data = {
                    "data_source": row["data_source"],
                    "workflow_id": row["workflow_id"],
                    "request_id": row["request_id"],
                    "processed_id":  row["processed_id"]
                }
                responses.append(data)

    return  responses
