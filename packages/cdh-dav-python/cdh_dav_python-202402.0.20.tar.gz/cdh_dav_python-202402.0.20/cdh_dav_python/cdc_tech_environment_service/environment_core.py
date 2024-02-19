""" Module for spark and os environment for cdc_tech_environment_service with minimal dependencies. """

import os
import subprocess
from typing import Tuple
from pathlib import Path

# library management
from importlib import util  # library management

# error handling
from subprocess import check_output, Popen, PIPE, CalledProcessError

#  data
os.environ["PYARROW_IGNORE_TIMEZONE"] = "1"
pyspark_pandas_loader = util.find_spec("pyspark.pandas")
pyspark_pandas_found = pyspark_pandas_loader is not None


# Get the currently running file name
NAMESPACE_NAME = os.path.basename(os.path.dirname(__file__))
# Get the parent folder name of the running file
SERVICE_NAME = os.path.basename(__file__)


class EnvironmentCore:
    """EnvironmentCore class with minimal dependencies for the developer service.
    - This class is used to configure the python environment.
    - This class also provides a broad set of generic utility functions.
    """

    @staticmethod
    def get_environment_name() -> Tuple[str, str, str]:
        """Returns the environment, project id and virtual environment name

        The function assumes that the virtual environment name is in the format `project_environment`,
        where `project` represents the project id and `environment` represents the environment (like 'dev', 'prod', etc.)

        Returns:
            Tuple[str, str, str]: A tuple where the first element is the environment,
            the second element is the project id and the third element is the virtual environment name.
            Returns None for all if no virtual environment is active.
        """
        env_path = os.getenv("VIRTUAL_ENV")

        if not env_path:
            return None, None, None

        virtual_env = os.path.basename(env_path)

        if "_" not in virtual_env:
            path = Path(env_path)
            if len(path.parts) > 2:
                data_product_id = os.path.basename(os.path.normpath(path))
                virtual_env = data_product_id + "_dev"
            else:
                virtual_env = "wonder_metadata_dev"
                data_product_id = "ocio_cdh"
            environment = "dev"
        else:
            virtual_env = virtual_env.lower()
            parts = virtual_env.rsplit("_", 2)
            if len(parts) > 2:
                data_product_id = parts[0] + "_" + parts[1]
                environment = parts[2]
                virtual_env = data_product_id + "_" + environment
            else:
                virtual_env = "wonder_metadata_dev"
                data_product_id = "ocio_cdh"

        return environment, data_product_id, virtual_env

    @staticmethod
    def get_environment_variable(variable_name: str) -> str:
        """Get an environment variable value from the operating system based on variable_name.
        If the variable name has unacceptable characters, convert them to _.

        Args:
            variable_name (str): The name of the environment variable.

        Returns:
            str: The value of the environment variable.
        """
        variable_name = variable_name.replace(" ", "_")
        variable_name = "".join(
            c if c.isalnum() or c == "_" else "_" for c in variable_name
        )
        return os.getenv(variable_name)
