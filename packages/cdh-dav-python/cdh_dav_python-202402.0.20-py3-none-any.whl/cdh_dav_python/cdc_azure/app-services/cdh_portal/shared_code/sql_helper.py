from databricks import sql

from shared_code import app_config


def get_running_workflows(workflow_ids):
    query_sql = f""" select s.*,h.tracking_start_utc as workflow_start_utc, h.tracking_status as workflow_status from cdh_engineering.etl_workflow_service s
                    inner join cdh_engineering.etl_workflow_header h on h.workflow_id = s.workflow_id
                    where s.workflow_id in ({workflow_ids})
                    order by h.workflow_id ,h.tracking_start_utc
    """

    responses = []
    with sql.connect(server_hostname=app_config.DATABRICKS_SERVER_HOSTNAME,
                     http_path=app_config.DATABRICKS_HTTP_PATH,
                     access_token=app_config.DATABRICKS_TOKEN) as connection:
        with connection.cursor() as cursor:
            cursor.execute(query_sql)
            result = cursor.fetchall()
            for row in result:
                data = {
                    "dataset_name": row["dataset_name"],
                    "delivery_date": row["data_delivery_date"],
                    "workflow_id": row["workflow_id"],
                    "display_name": row["display_name"],
                    "target_system": row["target_system"],
                    "target_resource_name": row["target_resource_name"],
                    "tracking_status": row["tracking_status"],
                    "tracking_start_utc": row["tracking_start_utc"],
                    "workflow_start_utc": row["workflow_start_utc"],
                }
                responses.append(data)

    return responses


def get_completed_workflows():
    query_sql = f""" select distinct h.dataset_name as data_source, h.data_delivery_date as delivery_date,to_date(h1.latest_processed_start) as processed_at, h.tracking_status as status,h.workflow_id
                    from cdh_engineering.etl_workflow_header h
                    inner join (
                      select dataset_name, max(tracking_start_utc) as latest_processed_start from cdh_engineering.etl_workflow_header
                      group by dataset_name
                    ) h1 on h1.dataset_name = h.dataset_name and h1.latest_processed_start = h.tracking_start_utc
                    where h.tracking_status in ('Succeeded','Rejected' )
                    order by data_source

    """

    responses = []
    with sql.connect(server_hostname=app_config.DATABRICKS_SERVER_HOSTNAME,
                     http_path=app_config.DATABRICKS_HTTP_PATH,
                     access_token=app_config.DATABRICKS_TOKEN) as connection:
        with connection.cursor() as cursor:
            cursor.execute(query_sql)
            result = cursor.fetchall()
            for row in result:
                data = {
                    "data_source": row["data_source"],
                    "delivery_date": row["delivery_date"],
                    "workflow_id": row["workflow_id"],
                    "processed_at": row["processed_at"],
                    "status": row["status"]
                }
                responses.append(data)

    return responses


def get_completed_workflows():
    query_sql = f""" select distinct h.dataset_name as data_source, h.data_delivery_date as delivery_date,to_date(h1.latest_processed_start) as processed_at, h.tracking_status as status,h.workflow_id
                    from cdh_engineering.etl_workflow_header h
                    inner join (
                      select dataset_name, max(tracking_start_utc) as latest_processed_start from cdh_engineering.etl_workflow_header
                      where tracking_status in ('Succeeded','Rejected' )
                      group by dataset_name
                    ) h1 on h1.dataset_name = h.dataset_name and h1.latest_processed_start = h.tracking_start_utc
                    order by data_source

    """

    responses = []
    with sql.connect(server_hostname=app_config.DATABRICKS_SERVER_HOSTNAME,
                     http_path=app_config.DATABRICKS_HTTP_PATH,
                     access_token=app_config.DATABRICKS_TOKEN) as connection:
        with connection.cursor() as cursor:
            cursor.execute(query_sql)
            result = cursor.fetchall()
            for row in result:
                data = {
                    "data_source": row["data_source"],
                    "delivery_date": row["delivery_date"],
                    "workflow_id": row["workflow_id"],
                    "processed_at": row["processed_at"],
                    "status": row["status"]
                }
                responses.append(data)

    return responses


def get_completed_workflows_by_data_source(data_source):
    query_sql = f"""select * from cdh_engineering.etl_workflow_header
where dataset_name = '{data_source}'
and tracking_status in ('Succeeded','Rejected' )
order by tracking_start_utc desc
limit 50

    """

    responses = []
    with sql.connect(server_hostname=app_config.DATABRICKS_SERVER_HOSTNAME,
                     http_path=app_config.DATABRICKS_HTTP_PATH,
                     access_token=app_config.DATABRICKS_TOKEN) as connection:
        with connection.cursor() as cursor:
            cursor.execute(query_sql)
            result = cursor.fetchall()
            for row in result:
                data = {
                    "data_source": row["dataset_name"],
                    "delivery_date": row["data_delivery_date"],
                    "workflow_id": row["workflow_id"],
                    "start": row["tracking_start_utc"],
                    "end": row["tracking_end_utc"],
                    "status": row["tracking_status"]
                }
                responses.append(data)

    return responses


def is_delivery_date_valid_to_process(data_source, delivery_date):
    query_sql = f"""select count(1) as result  from cdh_engineering.etl_workflow_header
where dataset_name = '{data_source}'
and cast(data_delivery_date as int) >= {delivery_date}
    """

    with sql.connect(server_hostname=app_config.DATABRICKS_SERVER_HOSTNAME,
                     http_path=app_config.DATABRICKS_HTTP_PATH,
                     access_token=app_config.DATABRICKS_TOKEN) as connection:
        with connection.cursor() as cursor:
            cursor.execute(query_sql)
            result = cursor.fetchall()
            count = int(result[0][0])
            return True if count == 0 else False
