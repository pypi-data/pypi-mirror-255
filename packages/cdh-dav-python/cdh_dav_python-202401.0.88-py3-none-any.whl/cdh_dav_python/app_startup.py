"""
This module contains the startup code for the CDH DAV Python application.
It imports necessary modules, defines functions for changing directories, retrieving environment variables,
creating the Flask API, and creating and configuring the Flask application instance.
"""

# Rest of the code...
from flask import Flask
from flask_restx import Api
from pathlib import Path
from dotenv import load_dotenv
import os
import sys
from werkzeug.middleware.proxy_fix import ProxyFix
import importlib

# Importing necessary modules from cdh_dav_python package
# These modules seem to be related to environment metadata, tracing and logging.
from cdh_dav_python.cdc_metadata_service import (
    environment_metadata as cdc_env_metadata,
)
from cdh_dav_python.cdc_admin_service.environment_logging import LoggerSingleton

# Constant indicating if the application is running inside Windows Subsystem for Linux (WSL)
RUNNING_IN_WSL = False
# Get the currently running file name
NAMESPACE_NAME = os.path.basename(os.path.dirname(__file__))
# Get the parent folder name of the running file
SERVICE_NAME = os.path.basename(__file__)


def change_to_root_directory():
    """
    Change the current working directory to the project root directory.
    """

    # Get the absolute path of the current script
    current_script_path = os.path.abspath(__file__)

    # Get the project root directory by going up one or more levels
    project_root = os.path.dirname(os.path.dirname(current_script_path))

    # Change the current working directory to the project root directory
    os.chdir(project_root)


def change_to_flask_directory():
    current_directory = os.getcwd()  # get current directory
    base_directory = os.path.basename(current_directory)  # get the base directory

    if base_directory != "cdh_dav_python":
        # path to the directory you want to change to
        new_directory = os.path.join(current_directory, "cdh_dav_python/cdh_dav_python")

        # change to new directory
        os.chdir(new_directory)
        print(f"Directory changed to {os.getcwd()}")
    else:
        print("Current directory is already 'cdh_dav_python'")

    # Create the path to the child directory
    child_directory = os.path.join(current_directory, "cdh_dav_python")

    # Check if the child directory exists
    if os.path.exists(child_directory) and os.path.isdir(child_directory):
        new_directory = os.path.join(current_directory, "cdh_dav_python")
        # change to new directory
        os.chdir(new_directory)


def get_environment_name():
    """
    Retrieves the value of the 'POSIT_ENV_NAME' environment variable.

    Raises:
        ValueError: If the 'POSIT_ENV_NAME' environment variable is not set.

    Returns:
        str: The value of the 'POSIT_ENV_NAME' environment variable.
    """

    environment_name = os.environ.get("POSIT_ENV_NAME")
    if environment_name is None:
        environment_name = os.environ.get("FLASK_ENV")
        if environment_name is None:
            raise ValueError("The POSIT_ENV_NAME environment variable is not set.")
    if environment_name == "development":
        environment_name = "dev"
    if environment_name == "production":
        environment_name = "prod"
    return environment_name


def create_api(app, api_description):
    """
    Creates and initializes an API and its namespaces for a given app.

        Args:
            app (Flask): The Flask application instance for which the API will be created.

        Returns:
            api (FlaskRestful.Api): An instance of the Flask-Restful Api that has been initialized for the given app.

            ns_welcome (flask_restplus.Namespace): A namespace for handling welcome-related routes.

            ns_alation (flask_restplus.Namespace): A namespace for handling alation-related routes.

            ns_jira (flask_restplus.Namespace): A namespace for handling Jira-related routes.

            ns_posit (flask_restplus.Namespace): A namespace for handling Posit-related routes.

    """

    api = Api(
        app,
        version="1.0",
        title="CDC Data Hub LAVA Flask API",
        description=api_description,
        doc="/api/swagger",
        url="/api/swagger",
    )

    ns_welcome = api.namespace(
        "welcome", description="Welcome to the CDC CDC Data Hub LAVA API"
    )

    TECH_ENVIRONMENT_DESCRIPTION = (
        "The tech-environment service manages the technical environment in which "
        "the data products and associated services are developed, deployed, and "
        "managed. This package contains datasets that provide critical information "
        "for understanding the technical architecture, components, and "
        "resources used to support the data products and associated services."
    )

    ns_tech_environment = api.namespace(
        "tech_environment",
        description=TECH_ENVIRONMENT_DESCRIPTION,
    )

    CDC_SECURITY_DESCRIPTION = (
        "The security service manages security of the data products and associated "
        "services. The package contains datasets that provide critical information "
        "for ensuring the confidentiality, integrity, and availability of the data "
        "products and associated services."
    )

    ns_cdc_security = api.namespace(
        "cdc_security",
        description=CDC_SECURITY_DESCRIPTION,
    )

    BUSINESS_DESCRIPTION = (
        "The business service manages the business context and meaning of the data "
        "products and associated services. This package contains datasets that "
        "provide critical information for understanding the business context, "
        "meaning, and usage of the data products and associated services."
    )

    ns_business = api.namespace(
        "business",
        description=BUSINESS_DESCRIPTION,
    )

    CDC_ADMIN_DESCRIPTION = (
        "The admin service manages and monitors data products and associated logs. "
        "This package contains datasets that provide critical information for "
        "ensuring the availability, performance, and quality of the data products "
        "and related services."
    )

    ns_cdc_admin = api.namespace(
        "cdc_admin",
        description=CDC_ADMIN_DESCRIPTION,
    )

    ALATION_DESCRIPTION = "The Alation service manages and monitors Alation."
    ns_alation = api.namespace("alation", description=ALATION_DESCRIPTION)

    JIRA_DESCRIPTION = (
        "The JIRA service provides read-only reporting and query services for JIRA."
    )

    ns_jira = api.namespace(
        "jira",
        description=JIRA_DESCRIPTION,
    )

    POSIT_DESCRIPTION = (
        "The POSIT service provides read-only reporting and query services for "
        "POSIT.  It also provides methods for automated app creation and publication "
        "of web applications via ManifestJson files."
    )

    ns_posit = api.namespace(
        "posit",
        description=POSIT_DESCRIPTION,
    )

    api.add_namespace(ns_welcome)
    api.add_namespace(ns_tech_environment)
    api.add_namespace(ns_cdc_security)
    api.add_namespace(ns_business)
    api.add_namespace(ns_cdc_admin)
    api.add_namespace(ns_jira)
    api.add_namespace(ns_alation)
    api.add_namespace(ns_posit)

    return (
        api,
        ns_welcome,
        ns_alation,
        ns_jira,
        ns_posit,
        ns_cdc_admin,
        ns_cdc_security,
    )


# def get_connect_api_key(config, az_client_secret, running_interactive):
#     # Get the connect_api_key from the environment variable
#     connect_api_key = os.environ.get("DEV_CDH_PREMIER_EXPLORATORY_POSIT_CONNECT_SECRET")

#     tenant_id = config.get("tenant_id")
#     client_id = config.get("client_id")
#     az_kv_key_vault_name = config.get("az_kv_key_vault_name")


#     # If the environment variable is blank or not set, fetch the secret from Azure Key Vault
#     if not connect_api_key:
#         print("Could not find enviornment variable DEV_CDH_PREMIER_EXPLORATORY_POSIT_CONNECT_SECRET")
#         connect_api_key = az_key_vault.get_secret(
#             "OCIO-CDH-DEV-POSIT-CONNECT-SECRET")

#     return connect_api_key


def create_app():
    """
    This function is used to create and configure a Flask application instance.

    Returns:
        app (flask.Flask): The Flask application instance.

    Example:
        app = create_app()

    Note:
        This function currently has no functionality. You should add Flask app creation and configuration logic inside it.

    """
    # Add your Flask app creation and configuration logic here

    # Get the path to the .env file

    CURRENT_USER_NAME = os.getenv("USERNAME") or os.getenv("USER")
    API_PATH = "/data-ecosystem-services/cdh_dav_python"

    dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
    # Load the .env file
    load_dotenv(dotenv_path)

    # set_key(dotenv_path, "PYARROW_IGNORE_TIMEZONE",
    #        "1")
    # set_key(dotenv_path, "APPLICATIONINSIGHTS_CONNECTION_STRING",
    #        f"InstrumentationKey={instrumentation_key};IngestionEndpoint=https://eastus-8.in.applicationinsights.azure.com/;LiveEndpoint=https://eastus.livediagnostics.monitor.azure.com/")
    # set_key(dotenv_path, "APPINSIGHTS_INSTRUMENTATIONKEY",
    #        instrumentation_key)
    # Reload the updated .env file
    # load_dotenv(dotenv_path)

    environment = get_environment_name()
    data_product_id = "wonder_metadata"

    # try:
    tracer, logger = LoggerSingleton.instance(
        NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
    ).initialize_logging_and_tracing()

    app = None

    try:
        with tracer.start_as_current_span("create_app"):
            # Get the absolute path of the directory of the current script
            dir_path = os.path.dirname(os.path.realpath(__file__))

            # Add this path to PYTHONPATH
            sys.path.insert(0, dir_path)

            logger.info("ran create_app")

            obj_env_metadata = cdc_env_metadata.EnvironmentMetaData()

            running_local = True
            change_to_root_directory()
            path = Path(os.getcwd())
            repository_path_default = str(path)

            logger.info(f"repository_path_default:{repository_path_default}")

            parameters = {
                "data_product_id": data_product_id,
                "data_product_id_root": "wonder",
                "data_product_id_individual": "metadata",
                "environment": environment,
                "az_sub_client_secret_key": "apps-client-secret",
                "repository_path": repository_path_default,
                "running_local": running_local,
            }
            config = obj_env_metadata.get_configuration_common(
                parameters, None, data_product_id, environment
            )

            logger.info(f"config_length:{len(config)}")

            app = Flask(__name__)

            app.wsgi_app = ProxyFix(
                app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1
            )

            app.env = "development"
            app.debug = True  # Enable debug mode

            app.cdc_config = config
            env_file_path = config.get("env_file_path")

            # shutil.copy(env_file_path, app.root_path)
            load_dotenv(env_file_path)

            az_sub_client_secret_key = config.get("az_sub_client_secret_key")
            az_kv_az_sub_client_secret_env_key = az_sub_client_secret_key.replace(
                "-", "_"
            )
            client_secret = os.getenv(az_kv_az_sub_client_secret_env_key)
            logger.info(
                f"az_kv_az_sub_client_secret_env_key:{az_kv_az_sub_client_secret_env_key}"
            )

            logger.info(f"az_sub_client_secret_key:{az_sub_client_secret_key}")
            logger.info(f"client_secret length:{len(client_secret)}")

            app.secret_key = client_secret

            # SET THE MICROSOFT REQUIRED ENVIRONMENT VARIABLE FOR SECRET
            os.environ["AZURE_CLIENT_SECRET"] = client_secret

            # Set the new value
            # set_key(dotenv_path, "FLASK_DEBUG", "1")
            # set_key(dotenv_path, "PYARROW_IGNORE_TIMEZONE", "1")

            # Reload the updated .env file
            # load_dotenv(dotenv_path)

            # Trim leading and trailing whitespace from client_secret
            if client_secret is None:
                logger.warning("client_secret is None")
            else:
                client_secret = client_secret.strip()

            # Check if the client_secret is None or a zero-length string
            if not client_secret:
                running_interactive = True

            # set_key(dotenv_path, az_sub_client_secret_key, client_secret)
            # set_key(dotenv_path, "CONNECT_API_KEY", connect_api_key)

            logger.info(f"env_file_path:{env_file_path}")

            try:
                importlib.import_module("cdh_dav_python")
                logger.info("cdh_dav_python is module in pythonpath")
            except ImportError:
                logger.warning("cdh_dav_python is not a module in pythonpath")

            if RUNNING_IN_WSL is True:
                sys.path.append(f"/home/{CURRENT_USER_NAME}{API_PATH}")
                logger.info(f"RUNNING_IN_WSL: {RUNNING_IN_WSL}")
                logger.info(f"/home/{CURRENT_USER_NAME}{API_PATH}")
            else:
                sys.path.append(os.path.abspath(__file__ + "/../../../cdh_dav_python/"))
                logger.info(f"RUNNING_IN_WSL: {RUNNING_IN_WSL}")
                logger.info(os.path.abspath(__file__ + "/../../../cdh_dav_python/"))

            app.tracer = tracer
            app.logger = logger

            return app
    except Exception as ex:
        if app is not None:
            error_msg = "Error: %s", ex
            exc_info = sys.exc_info()
            LoggerSingleton.instance(
                NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
            ).error_with_exception(error_msg, exc_info)

        raise
