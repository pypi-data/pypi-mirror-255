import requests
import urllib.parse
from cdh_lava_core.alation_service.endpoint import Endpoint

import os

# Get the currently running file name
NAMESPACE_NAME = os.path.basename(os.path.dirname(__file__))
# Get the parent folder name of the running file
SERVICE_NAME = os.path.basename(__file__)


class Tags(Endpoint):
    """
    A class for interacting with the Alation V2 API to add tags to objects.

    This is a subclass of Endpoint, so users should instantiate the class by providing an API token
    and the base URL of the Alation server to work with.
    """

    TAGS_ENDPOINT = "/integration/tag"

    def apply(self, object_type, object_id, tag):
        """
        Apply a tag to an object in Alation

        Parameters
        ----------
        object_type: string
            The Alation object type: "schema", "table" or "attribute". Note that columns are called
            attributes in Alation.
        object_id: int
            The ID of the object in Alation.
        tag: string
            The tag to apply to the object.
        """

        request_body = {"oid": object_id, "otype": object_type}

        url = "{base_url}{tags_endpoint}/{tag}/subject/".format(
            base_url=self.base_url,
            tags_endpoint=self.TAGS_ENDPOINT,
            tag=urllib.parse.quote(tag),
        )
        response = requests.post(
            url, headers=self.method_with_body_headers(), json=request_body, verify=True
        )
        response.raise_for_status()
