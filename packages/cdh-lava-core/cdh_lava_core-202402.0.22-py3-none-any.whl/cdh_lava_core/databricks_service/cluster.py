""" Module for rep_core for it_cdc_admin_service that handles repository and cluster functions with minimal dependencies. """

import os
import json
from html.parser import HTMLParser  # web scraping html
import requests

from cdh_lava_core.cdc_log_service.environment_logging import LoggerSingleton

# Get the currently running file name
NAMESPACE_NAME = os.path.basename(os.path.dirname(__file__))
# Get the parent folder name of the running file
SERVICE_NAME = os.path.basename(__file__)


class DbxCluster:
    """
    A class representing a Databricks cluster.

    This class provides methods to interact with a Databricks cluster, such as retrieving the status of a library installed on the cluster and installing a library on the cluster.

    Attributes:
        None

    Methods:
        describe_cluster_library_state(library_object, cluster_id, status):
            Converts cluster library status response to a verbose message.

        get_cluster_library_status(config, library_source, properties, verbose=True):
            Retrieves the status of a library installed on a Databricks cluster.

        install_cluster_library(config, library_source, content_data):
            Installs a cluster library given correct source and properties are provided.

        call_databricks_install_api(config, end_point, body, method="GET", verbose=True):
            Calls the Databricks install API to install a library on a cluster.

        import_file(config, content_data, content_type, file_path) -> bool:
            Imports file from abfss to repo library.
    """

    @staticmethod
    def describe_cluster_library_state(library_object, cluster_id, status):
        """
        Returns a descriptive message based on the library state.

        Args:
            library_object (str): The name of the library object.
            cluster_id (str): The ID of the cluster.
            status (str): The status of the library.

        Returns:
            str: A descriptive message based on the library state.

        Raises:
            KeyError: If the status is not one of the predefined values.

        """

        lib_title = library_object.title()
        lib_obj = library_object
        ni_msg = f"{lib_title} library is not installed on cluster {cluster_id}."
        inst_msg = f"{lib_obj} library is already installed on cluster {cluster_id}."
        pend_msg = "Pending installation of {} library on cluster {} . . ."
        resolve_msg = f"Retrieving metadata for the installation of {lib_obj} library on cluster {cluster_id} . . ."
        install_msg = f"Installing {lib_obj} library on cluster {cluster_id} . . ."
        failed_msg = f"{lib_title} library failed to install on cluster {cluster_id}."
        uninst_msg = f"{lib_title} library installed on cluster {cluster_id} has been marked for removal upon restart."

        result_map = {
            "NOT_INSTALLED": ni_msg,
            "INSTALLED": inst_msg,
            "PENDING": pend_msg,
            "RESOLVING": resolve_msg,
            "INSTALLING": install_msg,
            "FAILED": failed_msg,
            "UNINSTALL_ON_RESTART": uninst_msg,
        }

        return result_map[status.upper()]

    @classmethod
    def get_cluster_library_status(
        cls, config, library_source, properties, verbose=True
    ):
        """
        Retrieves the status of a library installed on a Databricks cluster.

        Args:
            config (dict): The configuration settings for the Databricks cluster.
            library_source (str): The source of the library. Valid sources are: jar, egg, whl, pypi, maven, cran.
            properties (dict): The properties associated with the library.
            verbose (bool, optional): Whether to display verbose output. Defaults to True.

        Returns:
            dict: The status of the library installation on the cluster.
        """
        library_source = library_source.lower()

        # Validate input
        error_message_1 = "Error: Invalid library source specified. Valid sources are: jar, egg, whl, pypi, maven, cran"
        assert library_source in (
            "jar",
            "egg",
            "whl",
            "pypi",
            "maven",
            "cran",
        ), error_message_1
        assert properties is not None, "Error: Empty properties provided"

        # Get the cluster ID from the Spark environment
        cluster_id = config["cdh_databricks_cluster"]

        # Set default result to not installed
        result = cls.describe_cluster_library_state(
            library_source, cluster_id, "NOT_INSTALLED"
        )

        # Execute REST API request to get the library statuses
        endpoint = f"2.0/libraries/cluster-status?cluster_id={cluster_id}"
        result = cls.call_databricks_install_api(config, endpoint, None, "GET", verbose)

        return result

    @classmethod
    def install_cluster_library(cls, config, library_source, content_data):
        """
        Installs a cluster library given correct source and properties are provided
        For examples see https://docs.databricks.com/api/latest/libraries.html#install

        :param cls: The class object.
        :param config: The configuration object containing the necessary information.
        :param library_source: The source of the library to be installed.
        :param content_data: The content data of the library file.
        :return: The status of the installation process.
        """

        library_file = content_data
        library_source = library_source.lower()

        # Validate input
        err_msg = "Error: Invalid library source specified. Valid sources are: jar, egg, whl, pypi, maven, cran"
        assert library_source in (
            "jar",
            "egg",
            "whl",
            "pypi",
            "maven",
            "cran",
        ), err_msg
        assert library_file is not None, "Error: Empty library_file provided"

        # Get the cluster ID from the Spark environment
        cluster_id = config["cdh_databricks_cluster"]

        status = cls.get_cluster_library_status(
            config, library_source, library_file, False
        ).upper()
        if status != "INSTALLED":
            # Create the HTTP request body based on the cluster ID, library source and properties
            libraries = f'"{library_source}": "{library_file}"'
            json_string = (
                '{"cluster_id": "'
                + cluster_id
                + '", "libraries":[{'
                + libraries
                + "}]}"
            )
            print(f"json_string:{json_string}")
            body = json.loads(json_string)
            # Execute REST API request to install the library
            result = cls.call_databricks_install_api(
                config, "2.0/libraries/install", body, "POST"
            )
            if result == "- response : success  -":
                print("Installation started . . .")
            else:
                print(result)
        else:
            print(
                cls.describe_cluster_library_state(library_source, cluster_id, status)
            )

        return status

    @classmethod
    def call_databricks_install_api(
        cls, config, end_point, body, method="GET", verbose=True
    ):
        """
        Calls the Databricks install API to install a library on a cluster.

        Args:
            cls (class): The class object.
            config (dict): The configuration dictionary containing access token, Databricks instance ID, and cluster ID.
            end_point (str): The API endpoint to call.
            body (dict): The JSON body to send in the API request.
            method (str, optional): The HTTP method to use. Defaults to "GET".
            verbose (bool, optional): Whether to print verbose output. Defaults to True.

        Returns:
            str: The response message from the API call.
        """

        token = config["access_token"]
        domain = config.get("cdh_databricks_instance_id")
        base_url = f"https://{domain}/api/"
        cluster_id = config["cdh_databricks_cluster"]

        bearer = "Bearer " + token
        headers = {"Authorization": bearer, "Content-Type": "application/json"}

        method = method.upper()
        url = base_url + end_point

        if method == "GET":
            response_install = requests.get(url, headers=headers, json=body)
        elif method == "POST":
            response_install = requests.post(url, headers=headers, json=body)

        data = None

        try:
            data = json.loads(response_install.text)
            response_install_text = json.dumps(response_install.json())
            print("- response : success  -")
            response_install_text_message = "Received Cluster API Response : "
            response_install_text_message += (
                f"{response_install_text} when posting to : {url}  "
            )
            response_install_text_message += f"to install library: {body}"
            response_install_text_message += f"to {response_install}"

            if response_install.status_code == 200:
                statuses = response_install.json()
                if "library_statuses" in statuses:
                    for status in statuses["library_statuses"]:
                        if status["library"] == "TODO":
                            if verbose is True:
                                msg = cls.describe_cluster_library_state(
                                    "library_source",
                                    cluster_id,
                                    status["status"],
                                )
                                response_install_text_message += msg
                            else:
                                response_install_text_message += status["status"]
                        else:
                            response_install_text_message += str(status)

        except Exception as exception_check:
            html_filter = HTMLFilter()
            html_filter.feed(response_install.text)
            response_install_text_message = html_filter.text
            print(f"- response : error - {str(exception_check)}")
            print("Error SAVE-PYTHON-RESPONSE converting response")
            print(f"text:{response_install} to json")

        if data is None:
            response_install_text_message = "Error Install Library"

        return response_install_text_message


class HTMLFilter(HTMLParser):
    text = ""

    def handle_data(self, data):
        self.text += data


class CDHObject(object):
    pass
