import os
import sys
from unittest.mock import patch, Mock
from cdh_dav_python.omop_service.omop_concept_class import OmopConceptClass
from cdh_dav_python.cdc_admin_service.environment_logging import LoggerSingleton
import requests
from cdh_dav_python.cdc_tech_environment_service.environment_http import EnvironmentHttp
from cdh_dav_python.cdc_admin_service.environment_logging import LoggerSingleton


# Get the currently running file name
NAMESPACE_NAME = os.path.basename(os.path.dirname(__file__))
# Get the parent folder name of the running file
SERVICE_NAME = os.path.basename(__file__)


class TestOmopConceptClass:
    @patch("requests.get")
    def test_fetch_concepts_by_query(self, mock_get):
        """
        Test fetching concepts by query string using a mock response.
        """
        tracer, logger = LoggerSingleton.instance(
            NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
        ).initialize_logging_and_tracing()

        with tracer.start_as_current_span("fetch_concepts_by_query"):
            try:

                logger.info("Setting up mock response data")

                # Mock response data
                mock_response_data = {
                    "empty": False,
                    "content": [
                        {
                            "id": "1",
                            "code": "123",
                            "name": "Aspirin",
                            "className": "Drug",
                            "standardConcept": "C",
                            "invalidReason": None,
                            "domain": "Drug",
                            "vocabulary": "RXNORM",
                            "score": 1.0,
                        }
                    ],
                }

                logger.info("Setting up mock")
                # Setup mock
                mock_get.return_value = Mock(ok=True)
                mock_get.return_value.json.return_value = mock_response_data
                mock_get.return_value.raise_for_status = (
                    Mock()
                )  # Explicitly show no exception for raise_for_status

                logger.info("Execute the function")
                # Execute the function
                query_string = "aspirin"
                data_product_id = "cdh_reference"
                environment = "dev"

                logger.info("Fetch concepts by query")
                omop_concept_class = OmopConceptClass()
                result = omop_concept_class.fetch_concepts_by_query(
                    query_string,
                    page_size=1,
                    data_product_id=data_product_id,
                    environment=environment,
                )

                logger.info(
                    "Additional verification to ensure raise_for_status was called"
                )
                mock_get.return_value.raise_for_status.assert_called_once()

                # Verify
                assert not result.empty, "Expected non-empty DataFrame"
                assert len(result) == 1, "Expected exactly 1 result"
                expected_columns = [
                    "id",
                    "code",
                    "name",
                    "className",
                    "standardConcept",
                    "invalidReason",
                    "domain",
                    "vocabulary",
                    "score",
                ]
                assert (
                    list(result.columns) == expected_columns
                ), "DataFrame should have the correct columns"

            except Exception as ex_:
                error_msg = "Error: %s", str(ex_)
                exc_info = sys.exc_info()
                LoggerSingleton.instance(
                    NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
                ).error_with_exception(error_msg, exc_info)
                raise

    @patch("requests.get")
    def test_fetch_concepts_for_class(self, mock_get):
        """
        Test fetching concepts for a specific class using a mock response.
        """
        # Mock response data for a concept class
        mock_response_data = {
            "empty": False,
            "content": [
                {
                    "id": "2",
                    "code": "456",
                    "name": "Ibuprofen",
                    "className": "Drug",
                    "standardConcept": "C",
                    "invalidReason": None,
                    "domain": "Drug",
                    "vocabulary": "RXNORM",
                    "score": 1.0,
                }
            ],
        }

        # Setup mock
        mock_get.return_value = Mock(ok=True)
        mock_get.return_value.json.return_value = mock_response_data

        # Execute the function
        concept_class = "Drug"
        result = OmopConceptClass.fetch_concepts_for_class(concept_class, page_size=1)

        # Verify
        assert not result.empty, "Expected non-empty DataFrame"
        assert len(result) == 1, "Expected exactly 1 result"
        expected_columns = [
            "id",
            "code",
            "name",
            "className",
            "standardConcept",
            "invalidReason",
            "domain",
            "vocabulary",
            "score",
        ]
        assert (
            list(result.columns) == expected_columns
        ), "DataFrame should have the correct columns"


# Note: Replace 'your_module' with the actual name of the Python file where your OmopConceptClass is defined.
