from dotenv import load_dotenv
import os
import sys
from unittest import mock

import pytest

import cdh_dav_python.az_client_service.azd_client as pase_azd_client
import cdh_dav_python.cdc_admin_service.environment_logging as environment_logging
import cdh_dav_python.cdc_admin_service.environment_tracing as environment_tracing
import cdh_dav_python.cdc_metadata_service.environment_metadata as cdc_env_metadata

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path)


def test_download_and_install_azd():

    # Call the method
    azd_client = pase_azd_client.AzdClient()
    azd_client.download_and_install_azd()
