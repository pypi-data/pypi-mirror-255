import os

# Get the currently running file name
NAMESPACE_NAME = os.path.basename(os.path.dirname(__file__))
# Get the parent folder name of the running file
SERVICE_NAME = os.path.basename(__file__)


class Endpoint:
    """
    A base class for interacting with Alation. It provides a location for the base URL
    and API token. It also has some helper methods for setting up request headers.
    """

    def __init__(self, token, base_url):
        """
        Initialize the Endpoint object.

        Args:
            token (str): The authentication token for accessing the endpoint.
            base_url (str): The base URL of the endpoint.

        Returns:
            None
        """
        self.updates = []
        self.token = token
        self.base_url = base_url

    def base_headers(self):
        """
        Create the basic HTTP headers needed to access the Alation API. This function sets the API token
        and the Accept type to JSON.

        This should be used when the HTTP call does not have a request body, such as a GET request.

        Returns
        -------
        dict
            Dictionary that can be supplied to the requests library as HTTP headers
        """
        return {"Token": self.token, "Accept": "application/json"}

    def method_with_body_headers(self):
        """
        Roughly the same as base_headers, but also sets the Content-Type for the request to JSON.

        This should be used when the HTTP call does has a request body, such as a POST or PUT request.

        Returns
        -------
        dict
            Dictionary that can be supplied to the requests library as HTTP headers
        """
        headers = self.base_headers()
        headers["Content-Type"] = "application/json"
        return headers
