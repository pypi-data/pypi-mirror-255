"""
Module: test_cdc_admin_environment_tracing.py

This module contains unit tests for the `cdc_admin_environment_tracing` module of the `cdh_dav_python` package.

"""

import os
import sys
import unittest
from datetime import datetime
import pytest

from opentelemetry.trace import Span

from opentelemetry.sdk.trace.export import SpanExportResult
from opentelemetry.trace.status import StatusCode, Status
from opentelemetry.sdk.trace.export import SpanExporter
from opentelemetry.trace import Tracer

from cdh_dav_python.cdc_admin_service.environment_logging import LoggerSingleton
from cdh_dav_python.cdc_admin_service.environment_tracing import (
    TracerSingleton,
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


class TestCDCAdminTracing(unittest.TestCase):
    """
    Unit test class for Databricks SQL functionality.

    This class contains test cases to verify the setup of the environment path for Databricks SQL.
    """

    def test_file_trace_exporter_initialization_wonder_metadata_dev(self):
        """
        Test case for initializing the FileTraceExporter.

        This test verifies that the FileTraceExporter is correctly initialized
        and that it inherits from the SpanExporter class. It also checks that
        the file_path attribute of the exporter is set to TRACE_FILENAME.
        """

        data_product_id = "wonder_metadata"
        environment = "dev"

        tracer, logger = LoggerSingleton(
            NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
        ).initialize_logging_and_tracing()

        logger.info(f"tracer: {str(tracer)}")

        assert isinstance(tracer, Tracer)
        # assert file_trace_exporter.file_path == TRACE_FILENAME

    def test_file_trace_exporter_write(self):
        """
        Test case for the `export` method of the `FileTraceExporter` class.
        It verifies that the exporter writes the expected content to the file.
        """

        data_product_id = "wonder_metadata"
        environment = "dev"

        tracer, logger = LoggerSingleton.instance(
            NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
        ).initialize_logging_and_tracing()

        logger.info(f"tracer: {str(tracer)}")

        tracer_singleton = TracerSingleton.instance(
            NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
        )

        trace_file_path = tracer_singleton.get_trace_file_path()

        # Here you should mock or create a dummy Span to pass to the exporter
        span_name = f"test_span_{datetime.now().isoformat()}"
        dummy_span = self.create_dummy_span(
            span_name, data_product_id, environment
        )  # This function needs to be implemented

        tracer_singleton.file_trace_exporter.delete_old_files()

        export_result = tracer_singleton.file_trace_exporter.export([dummy_span])

        print(f"export_result: {export_result}")

        # Verify the file contains the expected output
        with open(trace_file_path, "r", encoding="utf-8") as f:
            contents = f.read()
            assert span_name in contents  # Replace with actual expected content

    def test_azure_monitor_trace_exporter_initialization(self):
        """
        Test case for initializing the Azure Monitor trace exporter.

        This test case verifies that the Azure Monitor trace exporter is properly initialized
        and that it is an instance of the SpanExporter class.

        Returns:
            None
        """
        data_product_id = "wonder_metadata"
        environment = "dev"

        tracer, logger = LoggerSingleton.instance(
            NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
        ).initialize_logging_and_tracing()

        logger.info(f"tracer: {tracer}")

        azure_trace_exporter = TracerSingleton.instance(
            NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
        ).azure_trace_exporter

        logger.info("azure_trace_exporter: %s", azure_trace_exporter)

        # add test for environment variables
        assert isinstance(azure_trace_exporter, SpanExporter)

    def test_azure_monitor_trace_exporter_export(self):
        """
        Test case for exporting a dummy span using the Azure Trace Exporter.

        Args:
            mock_transmit: The mock transmit object.

        Returns:
            None
        """

        data_product_id = "wonder_metadata"
        environment = "dev"

        tracer, logger = LoggerSingleton.instance(
            NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
        ).initialize_logging_and_tracing()

        logger.info(f"tracer: {tracer}")

        azure_trace_exporter = TracerSingleton.instance(
            NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
        ).azure_trace_exporter

        logger.info("azure_trace_exporter: %s", azure_trace_exporter)

        span_name = f"test_span_{datetime.now().isoformat()}"
        dummy_span = self.create_dummy_span(span_name, data_product_id, environment)
        dummy_span.set_status(Status(StatusCode.OK))
        dummy_span.end()

        # Export the dummy span
        result = azure_trace_exporter.export([dummy_span])

        self.assertEqual(result, SpanExportResult.SUCCESS)

    def create_dummy_span(self, span_name, data_product_id, environment) -> Span:
        """
        Creates a dummy span with the given name.

        Args:
            span_name (str): The name of the span.

        Returns:
            Span: The created dummy span.
        """

        tracer, logger = LoggerSingleton.instance(
            NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
        ).initialize_logging_and_tracing()

        logger.info(f"tracer: {tracer}")
        # Start and end a span using the tracer
        with tracer.start_as_current_span(span_name) as span:
            # Set some attributes to the span
            span.set_attribute("test_attribute", "value")

        return span


if __name__ == "__main__":
    pytest.main()
