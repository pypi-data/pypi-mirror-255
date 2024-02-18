"""Initialize the cdc_metadata_service subpackage of cdh_dav_python package"""
# allow absolute import from the root folder
# whatever its name is.
from cdh_dav_python.cdc_metadata_service import pipeline_metadata
from cdh_dav_python.cdc_metadata_service import logging_metadata
from cdh_dav_python.cdc_metadata_service import job_metadata
from cdh_dav_python.cdc_metadata_service import environment_metadata
from cdh_dav_python.cdc_metadata_service import dataset_metadata

import sys  # don't remove required for error handling
import os

# Import from sibling directory ..\databricks_service
OS_NAME = os.name

sys.path.append("..")
if OS_NAME.lower() == "nt":
    print("cdc_metadata_service: windows")
    sys.path.append(os.path.dirname(os.path.abspath(__file__ + "\\..")))
    sys.path.append(os.path.dirname(os.path.abspath(__file__ + "\\..\\..")))
    sys.path.append(os.path.dirname(os.path.abspath(__file__ + "\\..\\..\\..")))
else:
    print("cdc_metadata_service: non windows")
    sys.path.append(os.path.dirname(os.path.abspath(__file__ + "/..")))
    sys.path.append(os.path.dirname(os.path.abspath(__file__ + "/../..")))
    sys.path.append(os.path.dirname(os.path.abspath(__file__ + "/../../..")))


import cdh_dav_python.cdc_admin_service.environment_logging
import cdh_dav_python.cdc_admin_service.environment_tracing
import cdh_dav_python.databricks_service.notebook

__all__ = [
    "dataset_metadata",
    "environment_metadata",
    "job_metadata",
    "logging_metadata",
    "pipeline_metadata",
]
