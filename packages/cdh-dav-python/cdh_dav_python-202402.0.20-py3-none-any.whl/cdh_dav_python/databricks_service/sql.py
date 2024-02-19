"""
This module provides functionality for interacting with Databricks SQL queries.
It includes a class, DatabricksSQL, that contains methods for fetching and saving pipelines,
handling exceptions, and preprocessing query text.

The module also imports various libraries and modules required for error handling, logging,
web scraping, and environment management.

"""

from pathlib import Path
import json
import base64
import re
import os
import sys
from html.parser import HTMLParser  # web scraping html
from string import Formatter
from importlib import util  # library management
import requests

# spark
# https://superuser.com/questions/1436855/port-binding-error-in-pyspark

pyspark_pandas_loader = util.find_spec("pyspark.pandas")
pyspark_pandas_found = pyspark_pandas_loader is not None

from cdh_dav_python.cdc_admin_service.environment_logging import LoggerSingleton
import cdh_dav_python.cdc_tech_environment_service.environment_file as cdc_env_file
import cdh_dav_python.cdc_tech_environment_service.environment_http as cdc_env_http

OS_NAME = os.name
sys.path.append("../..")

if OS_NAME.lower() == "nt":
    print("environment_logging: windows")
    sys.path.append(os.path.dirname(os.path.abspath(__file__ + "\\..")))
    sys.path.append(os.path.dirname(os.path.abspath(__file__ + "\\..\\..")))
    sys.path.append(os.path.dirname(os.path.abspath(__file__ + "\\..\\..\\..")))
else:
    print("environment_logging: non windows")
    sys.path.append(os.path.dirname(os.path.abspath(__file__ + "/..")))
    sys.path.append(os.path.dirname(os.path.abspath(__file__ + "/../..")))
    sys.path.append(os.path.dirname(os.path.abspath(__file__ + "/../../..")))


# Get the currently running file name
NAMESPACE_NAME = os.path.basename(os.path.dirname(__file__))
# Get the parent folder name of the running file
SERVICE_NAME = os.path.basename(__file__)


class DatabricksSQL:
    """
    A class that provides methods for interacting with Databricks SQL queries.
    """

    @classmethod
    def fetch_and_save_pipeline(
        cls,
        databricks_access_token,
        repository_path,
        environment,
        databricks_instance_id,
        data_product_id_root,
        data_product_id,
        query_name,
        pipeline_name,
        execute_results_flag,
        arg_dictionary,
        running_local,
        yyyy_param,
        mm_param,
        dd_param,
        transmission_period,
        cdh_databricks_repository_path,
    ):
        """
        Fetches the SQL query, generates Python code for the pipeline, saves the pipeline code,
        saves the SQL query, and returns 'success' if successful.

        Args:
            cls: The class object.
            databricks_access_token (str): The access token for Databricks.
            repository_path (str): The path to the repository.
            environment (str): The environment name.
            databricks_instance_id (str): The ID of the Databricks instance.
            data_product_id_root (str): The root ID of the data product.
            data_product_id (str): The ID of the data product.
            query_name (str): The name of the SQL query.
            pipeline_name (str): The name of the pipeline.
            execute_results_flag (bool): Flag indicating whether to execute the results.
            arg_dictionary (dict): Dictionary of arguments for the pipeline.
            running_local (bool): Flag indicating whether the pipeline is running locally.
            yyyy_param (str): The year parameter.
            mm_param (str): The month parameter.
            dd_param (str): The day parameter.
            transmission_period (str): The transmission period.
            cdh_databricks_repository_path (str): The path to the CDH Databricks repository.

        Returns:
            str: The string 'success' if successful.

        Raises:
            Exception: If an error occurs during the process.
        """
        tracer, logger = LoggerSingleton.instance(
            NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
        ).initialize_logging_and_tracing()

        with tracer.start_as_current_span("fetch_and_save_pipeline"):
            try:
                logger.info("------- fetch_sql ----------------")
                (query_text, variable_text) = cls.fetch_sql(
                    databricks_access_token,
                    databricks_instance_id,
                    query_name,
                    environment,
                    execute_results_flag,
                    data_product_id,
                )

                query_text_python = cls.readd_single_braces(query_text)

                query_text_python = cls.get_pipeline_python(
                    arg_dictionary,
                    environment,
                    query_text_python,
                    variable_text,
                    yyyy_param,
                    mm_param,
                    dd_param,
                    transmission_period,
                    data_product_id,
                )

                logger.info("------- save_pipeline_python----------------")
                cls.save_pipeline_python(
                    environment,
                    query_text_python,
                    databricks_access_token,
                    repository_path,
                    data_product_id,
                    databricks_instance_id,
                    pipeline_name,
                    running_local,
                    data_product_id_root,
                    cdh_databricks_repository_path,
                )

                query_text_sql = cls.readd_double_braces(query_text)

                logger.info("------- save_pipeline_sql----------------")
                cls.save_pipeline_sql(
                    databricks_instance_id,
                    databricks_access_token,
                    query_name,
                    query_text_sql,
                    repository_path,
                    data_product_id_root,
                    data_product_id,
                    environment,
                    cdh_databricks_repository_path,
                )

                return "success"

            except Exception as ex:
                error_msg = "Error: %s", ex
                exc_info = sys.exc_info()
                LoggerSingleton.instance(
                    NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
                ).error_with_exception(error_msg, exc_info)
                raise

    @staticmethod
    def handle_exception(err, data_product_id, environment):
        """
        Handles an exception by logging the error message and exception information.

        Args:
            err: The exception object.

        Returns:
            None
        """
        error_msg = "Error: %s", err
        exc_info = sys.exc_info()
        LoggerSingleton.instance(
            NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
        ).error_with_exception(error_msg, exc_info)

    @staticmethod
    def handle_json_conversion_error(exception_check, response_text_raw, logger):
        """
        Handles the error that occurs when converting response text to JSON.

        Args:
            exception_check (Exception): The exception that occurred during JSON conversion.
            response_text_raw (str): The raw response text.
            logger (Logger): The logger object for logging error messages.

        Returns:
            None
        """
        html_filter = HTMLFilter()
        html_filter.feed(response_text_raw)
        response_text = html_filter.text
        logger.error(f"- response : error - {str(exception_check)}")
        logger.error(f"Error converting response text:{response_text} to json")

    @classmethod
    def get_query_text(cls, data):
        """
        Get the query text from the provided data.

        Args:
            data (dict): The data containing the query information.

        Returns:
            str: The query text.
        """

        query_text = (
            "# Check configuration of view in list - no query content was found"
        )

        for i in data["results"]:
            query_text_original = i["query"]
            query_text = cls.remove_braces(query_text_original)
            return query_text

    @staticmethod
    def remove_braces(query_text_original):
        """
        Preprocesses the query text by replacing special characters to avoid conflicts with string formatting.

        Args:
            query_text_original (str): The original query text.

        Returns:
            str: The preprocessed query text.
        """
        query_text = query_text_original.replace(
            "{{", "TEMPORARY_OPEN_BRACKET"
        ).replace("}}", "TEMPORARY_CLOSE_BRACKET")
        query_text = query_text.lstrip()
        query_text = query_text.rstrip()
        return query_text

    @staticmethod
    def readd_double_braces(query_text_original):
        """
        Replaces the temporary open and close brackets in the query text with double braces.

        Args:
            query_text_original (str): The original query text.

        Returns:
            str: The modified query text with double braces.
        """
        query_text = query_text_original.replace(
            "TEMPORARY_OPEN_BRACKET", "{{"
        ).replace("TEMPORARY_CLOSE_BRACKET", "}}")
        query_text = query_text.lstrip()
        query_text = query_text.rstrip()
        return query_text

    @staticmethod
    def readd_single_braces(query_text_original):
        """
        Replaces the temporary open and close braces in the query text with actual braces.

        Args:
            query_text_original (str): The original query text with temporary braces.

        Returns:
            str: The query text with actual braces.
        """
        query_text = query_text_original.replace("TEMPORARY_OPEN_BRACKET", "{").replace(
            "TEMPORARY_CLOSE_BRACKET", "}"
        )
        query_text = query_text.lstrip()
        query_text = query_text.rstrip()
        return query_text

    @classmethod
    def fetch_sql(
        cls,
        databricks_access_token,
        databricks_instance_id,
        query_name,
        environment,
        execute_results_flag,
        data_product_id,
    ):
        """
        Fetches SQL query text and variable text from DataBricks SQL.

        Args:
            cls (class): The class object.
            databricks_access_token (str): The access token for DataBricks.
            databricks_instance_id (str): The instance ID of DataBricks.
            query_name (str): The name of the SQL query.
            environment (str): The environment in which the query is executed.
            execute_results_flag (bool): Flag indicating whether to execute the query.
            data_product_id (str): The ID of the data product.

        Returns:
            tuple: A tuple containing the query text and variable text.
        """

        tracer, logger = LoggerSingleton.instance(
            NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
        ).initialize_logging_and_tracing()

        with tracer.start_as_current_span("fetch_sql"):
            try:
                api_command = cls.get_api_command(query_name)
                url = cls.get_url(databricks_instance_id, api_command)

                try:
                    logger.info(
                        f"fetch_sql request start for query_name:{query_name} url:{str(url)}"
                    )
                    response = cls.process_request(
                        url, databricks_access_token, data_product_id, environment
                    )
                    logger.info(
                        f"process_response start for query_name:{query_name} url:{str(url)}"
                    )
                    results = cls.process_response(response)
                    response_text = json.dumps(results)
                    logger.info(
                        f"process_response complete for query_name:{query_name} with response_text_legnth {len(response_text)}"
                    )
                except requests.exceptions.HTTPError as http_err:
                    error_msg = "Error: %s", http_err
                    exc_info = sys.exc_info()
                    LoggerSingleton.instance(
                        NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
                    ).error_with_exception(error_msg, exc_info)
                    raise
                except Exception as err:
                    cls.handle_exception(err, data_product_id, environment)
                    raise

                data = None

                try:
                    data = cls.load_json(response)
                    response_text_string = cls.get_response_text_string(
                        response_text, url, query_name
                    )
                    data_count = data["count"] if "count" in data else 0
                    logger.info("- response : success  -")
                    logger.info(f"{response_text_string}")
                except Exception as exception_check:
                    response_text_raw = response.text
                    cls.handle_json_conversion_error(
                        exception_check, response_text_raw, logger
                    )

                variable_text = "Not Set : Data was not loaded"
                query_text_original = "Not Set : Data was not loaded"
                if data is None:
                    logger.info("Error loading sql query:{query_name}")
                    raise ValueError(f"Error loading sql query:{query_name}")
                elif data_count == 0:
                    logger.info(f"query name:{query_name}:")
                    logger.info(
                        f"query_text for {query_name} not found in DataBricks SQL"
                    )
                    raise ValueError(
                        "query_text for {query_name} not found in DataBricks SQL. Check the query name and permissions"
                    )
                else:
                    query_text = cls.get_query_text(data)
                    response = "not set"

                    for i in data["results"]:
                        query_text_original = i["query"]
                        query_text = cls.remove_braces(query_text_original)
                        query_text = cls.escape_double_quote(query_text)
                        query_text = query_text.strip()

                        # remove -- comments
                        query_text = re.sub(
                            r"^--.*\n?", "", query_text, flags=re.MULTILINE
                        )

                        if query_text == "":
                            logger.info(f"query name{query_name}:")
                            logger.info(f"{query_text} not found in DataBricks SQL")
                        else:
                            if not query_text.endswith(";"):
                                query_text += ";"
                        # ph = "TEMPORARY_OPEN_BRACKET"
                        variable_text = (
                            f'execute_results_flag = "{execute_results_flag}"'
                        )

                return (str(query_text), str(variable_text))

            except Exception as ex:
                error_msg = "Error: %s", ex
                exc_info = sys.exc_info()
                LoggerSingleton.instance(
                    NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
                ).error_with_exception(error_msg, exc_info)
                raise

    @classmethod
    def get_python_query_parameters_code(
        cls,
        environment,
        arg_dictionary,
        yyyy_param,
        mm_param,
        dd_param,
        transmission_period,
        query_text_original,
        data_product_id,
    ):
        """
        Generates Python code for setting query parameters and retrieving their values using Databricks widgets.

        Args:
            environment (str): The environment name.
            arg_dictionary (dict): A dictionary containing argument values.
            yyyy_param (str): The year parameter.
            mm_param (str): The month parameter.
            dd_param (str): The day parameter.
            transmission_period (str): The transmission period.
            query_text_original (str): The original query text.
            data_product_id (str): The data product ID.

        Returns:
            str: The generated Python code for setting query parameters and retrieving their values.
        """

        tracer, logger = LoggerSingleton.instance(
            NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
        ).initialize_logging_and_tracing()

        with tracer.start_as_current_span("get_python_query_parameters_code"):
            try:
                query_parse = query_text_original.replace("{{", "{").replace("}}", "}")
                logger.info(f"query_parse:{query_parse}")
                param_list = [
                    fname for _, fname, _, _ in Formatter().parse(query_parse) if fname
                ]

                dict_param_unique = dict()
                for line in list(dict.fromkeys(param_list)):
                    line = line.replace('"', "").replace("'", "")
                    if line.strip() == "environment":
                        dict_param_unique["'" + line.strip() + "'"] = environment
                    else:
                        dict_param_unique["'" + line.strip() + "'"] = (
                            "'enter " + line.strip() + " value'"
                        )

                dict_param_unique["yyyy"] = yyyy_param
                dict_param_unique["mm"] = mm_param
                dict_param_unique["dd"] = dd_param
                dict_param_unique["transmission_period"] = transmission_period

                new_param_code = f"""
from pyspark.sql.functions import col
from pathlib import Path
import os
dbutils_defined = 'dbutils' in locals() or 'dbutils' in globals()
if not dbutils_defined:
    from databricks.connect import DatabricksSession
    from databricks.sdk.core import Config

    databricks_profile = "{data_product_id}_{environment}"
    databricks_profile = databricks_profile.upper()

    user_name = os.environ.get("USER") or os.environ.get("USERNAME")
    os.environ["USER_ID"] = user_name
    config = Config(profile=databricks_profile)
    spark = DatabricksSession.builder.sdkConfig(config).getOrCreate()
                """

                for line in dict_param_unique:
                    line = line.replace('"', "").replace("'", "")
                    if line in arg_dictionary:
                        new_param_code_to_add = f"""
if dbutils_defined:\n
    dbutils.widgets.text('{line}', '{arg_dictionary[line]}')\n
"""
                        new_param_code = new_param_code + new_param_code_to_add
                    else:
                        new_param_code_to_add = f"""
if dbutils_defined:\n
    dbutils.widgets.text('{line}', 'default')\n
"""
                    new_param_code = new_param_code + new_param_code_to_add

                dict_code = ""
                for line in dict_param_unique:
                    line = line.replace('"', "").replace("'", "")
                    if line in arg_dictionary:
                        line_strip = line.strip().replace('"', "")
                        dict_code = (
                            dict_code + f"'{line_strip}':'{arg_dictionary[line]}',"
                        )
                    else:
                        logger.warning(f"{line} not in arg_dictionary")
                        line_strip = line.strip().replace('"', "")
                        dict_code = dict_code + f"'{line_strip}':'default',"

                dict_code = dict_code + f"'environment':'{environment}',"
                dict_parameters = "dict_parameters = {" + dict_code.rstrip(",") + "}\n"

                new_param_code = new_param_code + dict_parameters

                return new_param_code

            except Exception as ex:
                error_msg = "Error: %s", ex
                exc_info = sys.exc_info()
                LoggerSingleton.instance(
                    NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
                ).error_with_exception(error_msg, exc_info)
                raise

    @classmethod
    def get_pipeline_python(
        cls,
        arg_dictionary,
        environment,
        query_text,
        variable_text,
        yyyy_param,
        mm_param,
        dd_param,
        transmission_period,
        data_product_id,
    ):
        """
        Generate content text for a pipeline in Python.

        Args:
            cls: The class object.
            arg_dictionary: A dictionary of arguments.
            environment: The environment.
            query_text: The SQL query text.
            variable_text: The variable text.
            yyyy_param: The year parameter.
            mm_param: The month parameter.
            dd_param: The day parameter.
            transmission_period: The transmission period.
            data_product_id: The data product ID.

        Returns:
            The generated content text for the pipeline.
        """

        # Set query parameters
        new_param_code = cls.get_python_query_parameters_code(
            environment,
            arg_dictionary,
            yyyy_param,
            mm_param,
            dd_param,
            transmission_period,
            query_text,
            data_product_id,
        )

        # Split SQL commands by ';'
        sql_commands = query_text.split(";")
        formatted_sql_commands = []

        for command in sql_commands:
            if command.strip():
                formatted_command = (
                    '"""' + command.strip() + '""".format(**dict_parameters)'
                )
                formatted_sql_commands.append(formatted_command)

        # Generate content text
        print_query_text = f"print({formatted_sql_commands})"
        print_df_results_texts = []

        for formatted_command in formatted_sql_commands:
            print_df_results_text = (
                """
df_results = spark.sql("""
                + formatted_command
                + """)
df_results.show()
listColumns=df_results.columns
#if ("sql_statement"  in listColumns):
#    print(df_results.first().sql_statement)
if (df_results.count() > 0):
    if ("sql_statement" in listColumns):
        df_merge = spark.sql(df_results.first().sql_statement)
        df_merge.show()"""
            )
            print_df_results_text = print_df_results_text.lstrip()
            print_df_results_texts.append(print_df_results_text)
        content_text = f"""
    {new_param_code}
# COMMAND ----------
    """
        for formatted_command, print_df_results_text in zip(
            formatted_sql_commands, print_df_results_texts
        ):
            content_text += f"""
{formatted_command}
# COMMAND ----------
# {print_query_text}
# COMMAND ----------
{variable_text}
# COMMAND ----------
{print_df_results_text}
# COMMAND ----------
    """
        content_text = content_text.lstrip()
        return content_text

    @classmethod
    def save_pipeline_python(
        cls,
        environment,
        content_text,
        databricks_access_token,
        repository_path,
        data_product_id,
        databricks_instance_id,
        pipeline_name,
        running_local,
        data_product_id_root,
        cdh_databricks_repository_path,
    ):
        """
        Saves a Python pipeline to Databricks.

        Args:
            cls: The class object.
            environment (str): The environment name.
            content_text (str): The content of the pipeline.
            databricks_access_token (str): The access token for Databricks.
            repository_path (str): The repository path.
            data_product_id (str): The data product ID.
            databricks_instance_id (str): The Databricks instance ID.
            pipeline_name (str): The name of the pipeline.
            running_local (bool): Indicates whether the code is running locally.
            data_product_id_root (str): The root data product ID.
            cdh_databricks_repository_path (str): The repository path for CDH Databricks.

        Returns:
            None
        """

        tracer, logger = LoggerSingleton.instance(
            NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
        ).initialize_logging_and_tracing()
        logger.info(f"running_local:{running_local}")

        with tracer.start_as_current_span("save_pipeline_python"):
            try:
                # configure api

                base_path_local = cls.get_base_path_local(
                    repository_path, data_product_id_root, data_product_id, environment
                )

                dir_name_python_local = cls.get_dir_name_python_local(
                    base_path_local, data_product_id, environment
                )

                api_version = "/api/2.0"
                api_command = "/workspace/import"
                url = f"https://{databricks_instance_id}{api_version}{api_command}"

                # Prepare File to  Save
                pipeline_name = pipeline_name.replace(".", "")
                if not pipeline_name.startswith(data_product_id):
                    pipeline_name = data_product_id + "_" + pipeline_name

                # Content
                content_python = base64.b64encode(content_text.encode("UTF-8")).decode(
                    "UTF-8"
                )

                if running_local:
                    # save to file system
                    # File Path
                    new_path_python = str(
                        os.path.join(dir_name_python_local, pipeline_name)
                    )
                    if not new_path_python.endswith(".py"):
                        new_path_python = new_path_python + ".py"

                    obj_file = cdc_env_file.EnvironmentFile()
                    if obj_file.file_exists(
                        running_local,
                        new_path_python,
                        data_product_id,
                        environment,
                        None,
                    ):
                        try:
                            os.remove(new_path_python)
                        except OSError as e:
                            logger.error(f"Error: {e.filename} - {e.strerror}.")

                    content_text = cls.unescape_double_quotes(content_text)
                    logger.info(f"Save Python {pipeline_name} to {new_path_python}")
                    obj_file.save_text_to_file(
                        dir_name_python_local,
                        content_text,
                        new_path_python,
                        "py",
                        data_product_id,
                        environment,
                    )

                    # Directory Path
                    sys.path.append(dir_name_python_local)
                    isdir = os.path.isdir(dir_name_python_local)
                    logger.info(f"dir_name_python_local: isdir:{isdir}")
                else:
                    logger.info("Running on server")
                    logger.info(f"dir_name_python_local:{dir_name_python_local}")

                    new_path_python = str(
                        os.path.join(dir_name_python_local, pipeline_name)
                    )
                    logger.info(f"new_path_python:{new_path_python}")
                    if not new_path_python.endswith(".py"):
                        new_path_python = new_path_python + ".py"

                dir_name_python_server = cls.get_dir_name_python_server(
                    base_path_local, data_product_id, environment
                )

                relative_path = cls.get_relative_path(dir_name_python_server, "cdh-dav")

                path_python_server = str(
                    os.path.join(
                        cdh_databricks_repository_path, relative_path, pipeline_name
                    )
                )
                path_python_server = obj_file.convert_to_unix_dir(
                    path_python_server, data_product_id, environment
                )

                path_python_server = path_python_server.rstrip("/")

                if not path_python_server.endswith(".py"):
                    path_python_server = path_python_server + ".py"

                # save to server
                data_python = {
                    "content": content_python,
                    "path": path_python_server,
                    "language": "PYTHON",
                    "overwrite": True,
                    "format": "SOURCE",
                }
                logger.info(f"------- Save Python {pipeline_name}  -------")
                logger.info(f"url:{str(url)}")

                headers_import = cls.get_headers(databricks_access_token)
                headers_redacted = str(headers_import).replace(
                    databricks_access_token, "[databricks_access_token REDACTED]"
                )
                logger.info(f"headers:{headers_redacted}")
                logger.info(f"json:{str(data_python)}")

                # Post to Save File
                obj_http = cdc_env_http.EnvironmentHttp()
                response_python = obj_http.post(
                    url,
                    headers_import,
                    60,
                    data_product_id,
                    environment,
                    json=data_python,
                )

                # Get Response
                try:
                    response_python_text = json.dumps(response_python.json())
                    logger.info("- response : success  -")
                    response_python_text_message = "Received SAVE-PYTHON-RESPONSE : "
                    response_python_text_message += (
                        f"{response_python.text} when posting to : {url}  "
                    )
                    response_python_text_message += (
                        f"to save python pipeline with sql query: {pipeline_name}"
                    )
                    response_python_text_message += f"to {new_path_python}"

                    logger.info(response_python_text)

                except Exception as exception_check:
                    html_filter = HTMLFilter()
                    html_filter.feed(response_python.text)
                    response_python_text = html_filter.text
                    error_msg = f"response : error - {str(exception_check)}"
                    error_msg = (
                        error_msg
                        + f"Error SAVE-PYTHON-RESPONSE converting response text:{response_python_text} to json"
                    )
                    exc_info = sys.exc_info()
                    # Detailed traceback
                    LoggerSingleton.instance(
                        NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
                    ).error_with_exception(error_msg, exc_info)
                    raise
            except requests.exceptions.HTTPError as err:
                # Log error details
                exc_info = sys.exc_info()
                error_msg = f"HTTP Error occurred: {err}"
                error_msg = error_msg + (f"Status Code: {response_python.status_code}")
                error_msg = error_msg + (f"Response Content: {response_python.text}")
                error_msg = error_msg + (f"Request URL: {response_python.url}")
                error_msg = error_msg + (
                    f"Request Headers: {response_python.request.headers}"
                )
                if response_python.request.body:
                    error_msg = error_msg + (
                        f"Request Body: {response_python.request.body}"
                    )

                # Detailed traceback
                LoggerSingleton.instance(
                    NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
                ).error_with_exception(error_msg, exc_info)
                raise

            except Exception as ex:
                error_msg = "Error: %s", ex
                exc_info = sys.exc_info()
                LoggerSingleton.instance(
                    NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
                ).error_with_exception(error_msg, exc_info)
                raise

    @staticmethod
    def get_relative_path(full_path, anchor_dir):
        """
        Extracts a relative path after a specified anchor directory and returns it in Unix format.

        :param full_path: The full file path (str).
        :param anchor_dir: The anchor directory after which the relative path is extracted (str).
        :return: The relative path after the anchor directory in Unix format (str).
        """
        # Normalize path to handle different OS path separators
        normalized_path = os.path.normpath(full_path)

        # Split the path into parts
        path_parts = normalized_path.split(os.sep)

        # Try to find the index of the anchor directory
        try:
            anchor_index = path_parts.index(anchor_dir)
        except ValueError:
            # Return None if the anchor directory is not in the path
            return None

        # Return the relative path after the anchor directory in Unix format
        return "/".join(path_parts[anchor_index + 1 :])

    @classmethod
    def save_pipeline_sql(
        cls,
        databricks_instance_id,
        databricks_access_token,
        query_name,
        query_text,
        repository_path,
        data_product_id_root,
        data_product_id: str,
        environment: str,
        cdh_databricks_repository_path: str,
    ):
        """
        Saves a SQL query to a Databricks workspace.

        Args:
            cls: The class object.
            databricks_instance_id (str): The ID of the Databricks instance.
            databricks_access_token (str): The access token for the Databricks instance.
            dir_name_sql_local (str): The directory name where the SQL query will be saved.
            query_name (str): The name of the SQL query.
            query_text (str): The text of the SQL query.

        Returns:
            dict: A dictionary containing the response from the API call.

        Raises:
            requests.exceptions.HTTPError: If an HTTP error occurs during the API call.
            Exception: If any other error occurs.
        """

        tracer, logger = LoggerSingleton.instance(
            NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
        ).initialize_logging_and_tracing()

        with tracer.start_as_current_span("save_pipeline_sql"):
            try:
                headers = cls.get_headers(databricks_access_token)
                # configure api
                api_version = "/api/2.0"
                api_command_import = "/workspace/import"
                api_command_delete = "/workspace/import"
                import_url = (
                    f"https://{databricks_instance_id}{api_version}{api_command_import}"
                )
                delete_url = (
                    f"https://{databricks_instance_id}{api_version}{api_command_delete}"
                )

                query_name = query_name.replace(".", "_")

                base_path_local = cls.get_base_path_local(
                    repository_path, data_product_id_root, data_product_id, environment
                )

                dir_name_sql_local = cls.get_dir_name_sql_local(
                    base_path_local, data_product_id, environment
                )

                # File Path
                new_path_sql = str(os.path.join(dir_name_sql_local, query_name))
                if not new_path_sql.endswith(".sql"):
                    new_path_sql = new_path_sql + ".sql"

                obj_file = cdc_env_file.EnvironmentFile()
                if obj_file.file_exists(
                    True, new_path_sql, data_product_id, environment
                ):
                    logger.info(f"File exists:{new_path_sql} - will attempt to remove")
                    try:
                        os.remove(new_path_sql)
                    except OSError as e:
                        logger.error(f"Error: {e.filename} - {e.strerror}.")
                else:
                    logger.info(f"File does not exist:{new_path_sql}")

                logger.info(f"Save SQL {query_name} to {new_path_sql}")
                obj_file.save_text_to_file(
                    dir_name_sql_local,
                    query_text,
                    new_path_sql,
                    "sql",
                    data_product_id,
                    environment,
                )

                dir_name_sql_server = cls.get_dir_name_sql_server(
                    base_path_local, data_product_id, environment
                )

                relative_path = cls.get_relative_path(dir_name_sql_server, "cdh-dav")

                path_sql_server = str(
                    os.path.join(
                        cdh_databricks_repository_path, relative_path, query_name
                    )
                )
                path_sql_server = obj_file.convert_to_unix_dir(
                    path_sql_server, data_product_id, environment
                )

                path_sql_server = path_sql_server.rstrip("/")

                if not path_sql_server.endswith(".sql"):
                    path_sql_server = path_sql_server + ".sql"

                # Prepare File to  Save
                content_sql = base64.b64encode(query_text.encode("UTF-8")).decode(
                    "UTF-8"
                )

                data_sql_delete = {"path": path_sql_server, "recursive": False}

                data_sql_import = {
                    "content": content_sql,
                    "path": path_sql_server,
                    "language": "SQL",
                    "overwrite": True,
                    "format": "SOURCE",
                }

                headers_redacted = str(headers).replace(
                    databricks_access_token, "[databricks_access_token REDACTED]"
                )
                logger.info(f"headers:{headers_redacted}")

                # Post to Delete File - Overwrite does not work if file type changed
                logger.info("------- DELETE SQL ----------------")

                logger.info(f"json:{str(data_sql_delete)}")

                # Get Response
                # Post to Save File
                obj_http = cdc_env_http.EnvironmentHttp()
                response_sql = obj_http.post(
                    delete_url,
                    headers,
                    60,
                    data_product_id,
                    environment,
                    data_sql_delete,
                )

                # Skip error checking - if file does not exist, it will not be deleted

                # Post to Save File
                logger.info("------- Save SQL ----------------")
                logger.info(f"url:{str(import_url)}")

                logger.info(f"headers:{headers_redacted}")
                logger.info(f"json:{str(data_sql_import)}")

                # Get Response
                # Post to Save File
                obj_http = cdc_env_http.EnvironmentHttp()
                response_sql = obj_http.post(
                    import_url,
                    headers,
                    60,
                    data_product_id,
                    environment,
                    data_sql_import,
                )

                # Check the status code
                if response_sql.status_code != 200:
                    # Raise an exception if the status code is not 200 (OK)
                    response_sql.raise_for_status()

                # Get Response
                try:
                    response_sql_text = json.dumps(response_sql.json())
                    logger.info("- response : success  -")
                    response_sql_text_message = "Received SAVE-SQL-RESPONSE : "
                    response_sql_text_message += (
                        f"{response_sql.text} when posting to : {import_url}  "
                    )
                    response_sql_text_message += (
                        f"to save python pipeline with sql query: {query_name}"
                    )
                    response_sql_text_message += f"to {new_path_sql}"

                    logger.info(response_sql_text_message)

                except Exception as exception_check:
                    html_filter = HTMLFilter()
                    html_filter.feed(response_sql.text)
                    response_sql_text = html_filter.text
                    error_message = f"response : error - {str(exception_check)}"
                    error_message = (
                        error_message
                        + f"Error SAVE-SQL-RESPONSE converting response text:{response_sql_text} to json"
                    )
                    exc_info = sys.exc_info()
                    # Detailed traceback
                    LoggerSingleton.instance(
                        NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
                    ).error_with_exception(error_message, exc_info)
                    raise
            except requests.exceptions.HTTPError as err:
                # Log error details
                exc_info = sys.exc_info()
                error_msg = f"HTTP Error occurred: {err}"
                error_msg = error_msg + (f"Status Code: {response_sql.status_code}")
                error_msg = error_msg + (f"Response Content: {response_sql.text}")
                error_msg = error_msg + (f"Request URL: {response_sql.url}")
                error_msg = error_msg + (
                    f"Request Headers: {response_sql.request.headers}"
                )
                if response_sql.request.body:
                    error_msg = error_msg + (
                        f"Request Body: {response_sql.request.body}"
                    )

                # Detailed traceback
                LoggerSingleton.instance(
                    NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
                ).error_with_exception(error_msg, exc_info)
                raise

    @staticmethod
    def extract_text_from_html(html_content):
        """
        Extracts text from HTML content.

        Args:
            html_content (str): The HTML content to extract text from.

        Returns:
            str: The extracted text from the HTML content.
        """
        html_filter = HTMLFilter()
        html_filter.feed(html_content)
        return html_filter.text

    # Helper functions
    @staticmethod
    def unescape_double_quotes(string):
        """
        Function to unescape double quotes in a string.

        Args:
        string (str): The string with escaped double quotes.

        Returns:
        str: A string with double quotes unescaped.
        """
        return string.replace('\\"', '"')

    @staticmethod
    def escape_double_quote(query_text):
        """
        Escapes double quotes in the given query text.

        Args:
            query_text (str): The query text to escape.

        Returns:
            str: The query text with double quotes escaped.
        """
        query_text = query_text.replace('"', '\\"')
        return query_text

    @classmethod
    def get_base_path_local(
        cls,
        repository_path,
        data_product_id_root,
        data_product_id: str,
        environment: str,
    ):
        """
        Get the base path for a given repository path, data product ID root, and data product ID.

        Args:
            repository_path (str): The path of the repository.
            data_product_id_root (str): The root ID of the data product.
            data_product_id (str): The ID of the data product.

        Returns:
            str: The base path formed by concatenating the repository path, data product ID root, and data product ID.
        """

        tracer, logger = LoggerSingleton.instance(
            NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
        ).initialize_logging_and_tracing()

        with tracer.start_as_current_span("get_base_path_local"):
            try:
                base_path_local = "".join(
                    [
                        repository_path.rstrip("/"),
                        "/",
                        data_product_id_root,
                        "/",
                        data_product_id,
                        "/",
                    ]
                )
                base_path_local = base_path_local.replace("/Workspace", "")
                logger.info(f"base_path_local:{base_path_local}")
                return base_path_local

            except Exception as ex:
                error_msg = "Error: %s", ex
                exc_info = sys.exc_info()
                LoggerSingleton.instance(
                    NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
                ).error_with_exception(error_msg, exc_info)
                raise

    @classmethod
    def get_dir_name_python_local(
        cls, base_path_local, data_product_id: str, environment: str
    ):
        """
        Get the directory name for Python autogenerated files.

        Args:
            base_path_local (str): The base path for the directory.

        Returns:
            str: The directory name for Python autogenerated files.
        """

        tracer, logger = LoggerSingleton.instance(
            NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
        ).initialize_logging_and_tracing()

        with tracer.start_as_current_span("get_dir_name_python_local"):
            try:
                # Create a Path object
                path = Path(base_path_local)

                # Remove the 'config/' part
                # Here we assume 'config' is always a direct folder and not nested
                new_parts = [part for part in path.parts if part != "config"]

                # Create a new Path object from the remaining parts
                new_path = Path(*new_parts)

                # Convert back to string if needed
                new_path_str = str(new_path)

                dir_name_python_local = "".join(
                    [new_path_str.rstrip("/"), "/autogenerated/python/"]
                )
                obj_file = cdc_env_file.EnvironmentFile()
                dir_name_python_local = obj_file.convert_to_current_os_dir(
                    dir_name_python_local, data_product_id, environment
                )
                logger.info(f"dir_name_python_local:{dir_name_python_local}")
                return dir_name_python_local
            except Exception as ex:
                error_msg = "Error: %s", ex
                exc_info = sys.exc_info()
                LoggerSingleton.instance(
                    NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
                ).error_with_exception(error_msg, exc_info)
                raise

    @classmethod
    def get_dir_name_sql_server(
        cls, base_path_local_server, data_product_id: str, environment: str
    ):
        """
        Returns the directory name for SQL server based on the base path.

        Args:
            base_path_local_server (str): The base path for the SQL server.

        Returns:
            str: The directory name for SQL server.

        Raises:
            Exception: If an error occurs during the process.
        """

        tracer, logger = LoggerSingleton.instance(
            NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
        ).initialize_logging_and_tracing()

        with tracer.start_as_current_span("get_dir_name_sql_server"):
            try:
                # Create a Path object
                path = Path(base_path_local_server)

                # Remove the 'config/' part
                # Here we assume 'config' is always a direct folder and not nested
                new_parts = [part for part in path.parts if part != "config"]

                # Create a new Path object from the remaining parts
                new_path = Path(*new_parts)

                # Convert back to string if needed
                base_path_local_server = str(new_path)

                dir_name_sql_server = "".join(
                    [base_path_local_server.rstrip("/"), "/autogenerated/sql/"]
                )
                dir_name_sql_server = dir_name_sql_server.replace("//", "/")
                logger.info(f"dir_name_sql_server:{dir_name_sql_server}")
                return dir_name_sql_server
            except Exception as ex:
                error_msg = "Error: %s", ex
                exc_info = sys.exc_info()
                LoggerSingleton.instance(
                    NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
                ).error_with_exception(error_msg, exc_info)
                raise

    @classmethod
    def get_dir_name_python_server(
        cls, base_path_local_server, data_product_id: str, environment: str
    ):
        """
        Get the directory name for the Python server.

        Args:
            base_path_local_server (str): The base path of the local server.
            data_product_id (str): The ID of the data product.
            environment (str): The environment.

        Returns:
            str: The directory name for the Python server.
        """

        tracer, logger = LoggerSingleton.instance(
            NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
        ).initialize_logging_and_tracing()

        with tracer.start_as_current_span("get_dir_name_python_server"):
            try:
                # Create a Path object
                path = Path(base_path_local_server)

                # Remove the 'config/' part
                # Here we assume 'config' is always a direct folder and not nested
                new_parts = [part for part in path.parts if part != "config"]

                # Create a new Path object from the remaining parts
                new_path = Path(*new_parts)

                # Convert back to string if needed
                base_path_local_server = str(new_path)

                dir_name_python_server = "".join(
                    [base_path_local_server.rstrip("/"), "/autogenerated/python/"]
                )
                dir_name_python_server = dir_name_python_server.replace("//", "/")
                logger.info(f"dir_name_python_server:{dir_name_python_server}")
                return dir_name_python_server
            except Exception as ex:
                error_msg = "Error: %s", ex
                exc_info = sys.exc_info()
                LoggerSingleton.instance(
                    NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
                ).error_with_exception(error_msg, exc_info)
                raise

    @classmethod
    def get_dir_name_sql_local(
        cls, base_path_local: str, data_product_id: str, environment: str
    ):
        """
        Returns the directory name for SQL files based on the given base path.

        Args:
            base_path_local (str): The base path for the directory.

        Returns:
            str: The directory name for SQL files.

        """

        tracer, logger = LoggerSingleton.instance(
            NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
        ).initialize_logging_and_tracing()

        with tracer.start_as_current_span("get_dir_name_sql_local"):
            try:
                # Create a Path object
                path = Path(base_path_local)

                # Remove the 'config/' part
                # Here we assume 'config' is always a direct folder and not nested
                new_parts = [part for part in path.parts if part != "config"]

                # Create a new Path object from the remaining parts
                new_path = Path(*new_parts)

                # Convert back to string if needed
                base_path_local = str(new_path)

                dir_name_sql_local = "".join(
                    [base_path_local.rstrip("/"), "/autogenerated/sql/"]
                )
                dir_name_sql_local = dir_name_sql_local.replace("//", "/")
                obj_file = cdc_env_file.EnvironmentFile()
                dir_name_sql_local = obj_file.convert_to_current_os_dir(
                    dir_name_sql_local, data_product_id, environment
                )
                logger.info(f"dir_name_sql_local:{dir_name_sql_local}")
                return dir_name_sql_local
            except Exception as ex:
                error_msg = "Error: %s", ex
                exc_info = sys.exc_info()
                LoggerSingleton.instance(
                    NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
                ).error_with_exception(error_msg, exc_info)
                raise

    @staticmethod
    def get_headers(databricks_access_token):
        """
        Returns the headers required for making API requests with the specified access token.

        Parameters:
        databricks_access_token (str): The access token used for authentication.

        Returns:
        dict: The headers dictionary containing the authorization and content-type headers.
        """
        bearer = "Bearer " + databricks_access_token
        headers = {"Authorization": bearer, "Content-Type": "application/json"}
        return headers

    @staticmethod
    def get_api_command(query_name):
        """
        Returns the API command for retrieving a specific query by name.

        Args:
            query_name (str): The name of the query.

        Returns:
            str: The API command for retrieving the query.
        """
        api_command = f"/queries?page_size=50&page=1&order=-executed_at&q={query_name}"
        return api_command

    @staticmethod
    def get_url(databricks_instance_id, api_command):
        """
        Constructs the URL for the SQL API endpoint based on the Databricks instance ID and API command.

        Parameters:
        - databricks_instance_id (str): The ID of the Databricks instance.
        - api_command (str): The API command to be appended to the URL.

        Returns:
        - url (str): The constructed URL for the SQL API endpoint.
        """
        api_version = "/api/2.0/preview/sql"
        url = f"https://{databricks_instance_id}{api_version}{api_command}"
        return url

    @classmethod
    def process_request(
        cls, url, databricks_access_token, data_product_id: str, environment: str
    ):
        """
        Process a request to the specified URL with the provided access token.

        Args:
            url (str): The URL to send the request to.
            databricks_access_token (str): The access token to include in the request headers.

        Returns:
            requests.Response: The response object returned by the request.

        Raises:
            Exception: If an error occurs during the request.
        """

        tracer, logger = LoggerSingleton.instance(
            NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
        ).initialize_logging_and_tracing()

        with tracer.start_as_current_span("process_request"):
            try:
                headers = cls.get_headers(databricks_access_token)
                obj_http = cdc_env_http.EnvironmentHttp()
                response = obj_http.get(
                    url, headers, 60, None, data_product_id, environment
                )
                if response.status_code != 200:
                    # Raise an exception if the status code is not 200 (OK)
                    response.raise_for_status()
                logger.info("------- FETCH-SQL-RESPONSE ----------------")
                return response
            except Exception as ex:
                error_msg = "Error: %s", ex
                exc_info = sys.exc_info()
                LoggerSingleton.instance(
                    NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
                ).error_with_exception(error_msg, exc_info)
                raise

    @staticmethod
    def process_response(response):
        """
        Process the response from an API call and return the results.

        Args:
            response (object): The response object returned from the API call.

        Returns:
            dict: The processed results as a dictionary.
        """
        results = response.json()
        return results

    @staticmethod
    def load_json(response):
        """
        Load JSON data from a response object.

        Args:
            response: The response object containing the JSON data.

        Returns:
            The parsed JSON data.

        """
        data = json.loads(response.text)
        return data

    @staticmethod
    def get_response_text_string(response_text, url, query_name):
        """
        Returns a formatted string describing the response received when fetching SQL query.

        Args:
            response_text (str): The response text received.
            url (str): The URL to which the request was posted.
            query_name (str): The name of the SQL query.

        Returns:
            str: A formatted string describing the response.

        """
        response_text_string = (
            f"Received FETCH-SQL with length : {len(str(response_text))}"
        )
        response_text_string += (
            f" when posting to : {url} to fetch sql query: {query_name}"
        )
        return response_text_string


class HTMLFilter(HTMLParser):
    """
    A class that filters HTML content and extracts text data.

    Attributes:
        text (str): The extracted text from the HTML content.
    """

    text = ""

    def handle_data(self, data):
        self.text += data


class CDHObject(object):
    """
    Represents a CDH object.
    """

    pass
