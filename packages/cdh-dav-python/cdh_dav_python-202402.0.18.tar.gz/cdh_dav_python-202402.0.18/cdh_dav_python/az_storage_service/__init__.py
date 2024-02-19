"""Initialize the az_storage subpackage of cdh_dav_python package"""
# allow absolute import from the root folder
# whatever its name is.
import sys  # don't remove required for error handling
import os


# Import from sibling directory ..\databricks_service
OS_NAME = os.name

sys.path.append("..")
if OS_NAME.lower() == "nt":
    print("az_storage_service: windows")
    sys.path.append(os.path.dirname(os.path.abspath(__file__ + "\\..")))
    sys.path.append(os.path.dirname(os.path.abspath(__file__ + "\\..\\..")))
    sys.path.append(os.path.dirname(os.path.abspath(__file__ + "\\..\\..\\..")))
else:
    print("az_storage_service: non windows")
    sys.path.append(os.path.dirname(os.path.abspath(__file__ + "/..")))
    sys.path.append(os.path.dirname(os.path.abspath(__file__ + "/../..")))
    sys.path.append(os.path.dirname(os.path.abspath(__file__ + "/../../..")))

from cdh_dav_python.cdc_admin_service import environment_logging
from cdh_dav_python.cdc_admin_service import environment_tracing

import cdh_dav_python.az_storage_service.az_storage_queue
import cdh_dav_python.az_storage_service.az_storage_file

__all__ = ["az_storage_queue", "az_storage_file"]
