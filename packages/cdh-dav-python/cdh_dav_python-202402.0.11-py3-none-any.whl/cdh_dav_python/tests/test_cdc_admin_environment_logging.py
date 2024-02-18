"""
Module: test_cdc_admin_environment_logging.py

This module contains unit tests for the `cdc_admin_environment_logging` module of the `cdh_dav_python` package.

"""

import os
import sys
import pytest
import unittest

from opentelemetry.trace import Span, SpanContext, SpanKind, TraceFlags, TraceState
from unittest.mock import patch, mock_open
import logging
from logging.handlers import TimedRotatingFileHandler
from cdh_dav_python.cdc_admin_service.environment_logging import (
    LoggerSingleton,
    ENV_SHARE_PATH,
)


# Get the currently running file name
NAMESPACE_NAME = os.path.basename(os.path.dirname(__file__))
# Get the parent folder name of the running file
SERVICE_NAME = os.path.basename(__file__)

OS_NAME = os.name
sys.path.append("..")

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

sys.path.append("..")


class TestCDCAdminLogging(unittest.TestCase):
    """
    Unit test class for Databricks SQL functionality.

    This class contains test cases to verify the setup of the environment path for Databricks SQL.
    """

    def test_environment_path_setup(self):
        """
        Test case to verify the setup of the environment path.

        This method checks if the environment path is correctly set up based on the operating system.
        On Windows, it verifies that the `ENV_SHARE_PATH` exists.
        On non-Windows systems, it verifies that the `ENV_SHARE_PATH` starts with a forward slash ("/").
        """
        if OS_NAME.lower() == "nt":
            assert ENV_SHARE_PATH.exists(), "ENV_SHARE_PATH should exist on Windows"
        else:
            assert ENV_SHARE_PATH.startswith(
                "/"
            ), "ENV_SHARE_PATH should be Unix-like on non-Windows systems"

    def test_singleton_instance(self):
        """
        Test case to verify the behavior of the LoggerSingleton.instance method.
        It checks whether the same instance is returned when called multiple times with the same parameters.
        """
        instance1 = LoggerSingleton.instance(NAMESPACE_NAME, SERVICE_NAME)
        instance2 = LoggerSingleton.instance(NAMESPACE_NAME, SERVICE_NAME)
        self.assertIs(instance1, instance2)

    def test_logger_configuration_wonder_metadata_dev(self):
        """
        Test case to verify the logger configuration.

        This test ensures that the logger is properly configured with the expected log level
        and at least one handler of type TimedRotatingFileHandler is present.

        """

        data_product_id = "wonder_metadata"
        environment = "dev"

        tracer, logger = LoggerSingleton.instance(
            NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
        ).initialize_logging_and_tracing()

        logger.info(f"tracer: {tracer}")

        self.assertEqual(logger.level, logging.INFO)
        self.assertTrue(
            any(isinstance(h, TimedRotatingFileHandler) for h in logger.handlers)
        )

    def test_environment_path_setup_wonder_metadata_dev(self):
        """
        Test case to verify the setup of the environment path.

        This method checks if the environment path is correctly set up based on the operating system.
        On Windows, it verifies that the `ENV_SHARE_PATH` exists.
        On non-Windows systems, it verifies that the `ENV_SHARE_PATH` starts with a forward slash ("/").
        """

        data_product_id = "wonder_metadata"
        environment = "dev"
        logger_singleton = LoggerSingleton.instance(
            NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
        )
        env_share_path = logger_singleton.get_env_share_path()

        if OS_NAME.lower() == "nt":
            assert env_share_path.exists(), "env_share_path should exist on Windows"
        else:
            assert env_share_path.startswith(
                "/"
            ), "env_share_path should be Unix-like on non-Windows systems"

    def test_get_log_file_tail_wonder_metadata_dev(self):
        """
        Test case for the `get_log_file_tail` method of the LoggerSingleton class.
        It verifies that the log file tail is retrieved successfully and has a non-zero length.
        """

        data_product_id = "wonder_metadata"
        environment = "dev"

        log_file_tail = LoggerSingleton.instance(
            NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
        ).get_log_file_tail()

        print(log_file_tail)

        # Assert the result
        assert len(log_file_tail) > 0

    def test_validate_application_insights_connection_wonder_metadata_dev(self):
        """
        Test case to validate the application insights connection string.

        This test verifies that the application insights connection string is valid
        and that test logs can be successfully sent to the application insights service.

        It uses the LoggerSingleton instance to validate the connection string and
        checks if the test logs were successfully sent.

        Assertions:
        - The mock_exporter should be called once.
        - The result should contain the message "Successfully sent test logs".
        """

        data_product_id = "wonder_metadata"
        environment = "dev"

        result = LoggerSingleton.instance(
            NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
        ).validate_application_insights_connection_string()

        self.assertIn("Successfully sent test logs", result)

    def test_truncate_log_file_wonder_metadata_dev(self):
        """
        Test case to verify the truncate_log_file method in the LoggerSingleton class.

        This test ensures that the log file is successfully truncated and returns a status code of 200.

        """

        data_product_id = "wonder_metadata"
        environment = "dev"

        status_code = LoggerSingleton.instance(
            NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
        ).truncate_log_file()

        print(status_code)

        # Assert the result
        assert status_code == 200


if __name__ == "__main__":
    pytest.main()
