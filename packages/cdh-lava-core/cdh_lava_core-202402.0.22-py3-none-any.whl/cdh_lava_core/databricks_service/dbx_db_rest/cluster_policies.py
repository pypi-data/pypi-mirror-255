"""
This module provides a client for managing Databricks cluster policies through REST API calls.
It encapsulates functionalities to create, update, list, and delete cluster policies, allowing for
easy interaction with the Databricks cluster policies API. Users can perform operations like getting
a policy by its ID or name, listing all policies, creating new policies with specific definitions,
and updating or deleting existing policies. The module aims to simplify the management of cluster
policies in a Databricks environment by abstracting the underlying API calls into a set of
convenient methods.

Classes:
    ClustersPolicyClient: A client class for interacting with the Databricks cluster policies API.

Usage:
    The ClustersPolicyClient class requires a RestClient instance upon initialization. This client
    can then be used to perform various operations on cluster policies, such as creating a policy,
    updating it by name or ID, deleting policies, and listing all policies within the Databricks
    environment. The class methods are designed to handle the specifics of the Databricks REST API
    calls, including request making, parameter passing, and response handling, thereby providing
    a higher-level interface for cluster policy management.
"""

from cdh_lava_core.databricks_service.dbx_db_rest import RestClient
from cdh_lava_core.databricks_service.dbx_rest.common import ApiContainer


class ClustersPolicyClient(ApiContainer):
    """A client for managing cluster policies in Databricks."""

    def __init__(self, client: RestClient):
        """
        Initialize the ClustersPolicyClient.

        Args:
            client (RestClient): The REST client used to communicate with the Databricks API.
        """
        self.client = client
        self.base_uri = f"{self.client.endpoint}/api/2.0/policies/clusters"

    def get_by_id(self, policy_id):
        """
        Get a cluster policy by its ID.

        Args:
            policy_id (str): The ID of the cluster policy.

        Returns:
            dict: The cluster policy information.
        """
        return self.client.execute_get_json(
            f"{self.base_uri}/get?policy_id={policy_id}"
        )

    def get_by_name(self, name):
        """
        Get a cluster policy by its name.

        Args:
            name (str): The name of the cluster policy.

        Returns:
            dict: The cluster policy information.
        """
        policies = self.list()
        for policy in policies:
            if policy.get("name") == name:
                return self.get_by_id(policy.get("policy_id"))
        return None

    def list(self):
        """
        List all cluster policies.

        Returns:
            list: A list of cluster policies.
        """
        # Does not support pagination
        return self.client.execute_get_json(f"{self.base_uri}/list").get("policies", [])

    def create(self, name: str, definition: dict):
        """
        Create a new cluster policy.

        Args:
            name (str): The name of the cluster policy.
            definition (dict): The definition of the cluster policy.

        Returns:
            dict: The created cluster policy information.
        """
        import json

        assert type(name) == str, f"Expected name to be of type str, found {type(name)}"
        assert (
            type(definition) == dict
        ), f"Expected definition to be of type dict, found {type(definition)}"

        params = {"name": name, "definition": json.dumps(definition)}
        response = self.client.execute_post_json(
            f"{self.base_uri}/create", params=params
        )
        policy_id = response.get("policy_id")
        return self.get_by_id(policy_id)

    def update_by_name(self, name: str, definition: dict):
        """
        Update a cluster policy by its name.

        Args:
            name (str): The name of the cluster policy.
            definition (dict): The updated definition of the cluster policy.

        Returns:
            dict: The updated cluster policy information.
        """
        policy = self.get_by_name(name)
        assert policy is not None, f'A policy named "{name}" was not found.'

        policy_id = policy.get("policy_id")

        return self.update_by_id(policy_id, name, definition)

    def update_by_id(self, policy_id: str, name: str, definition: dict):
        """
        Update a cluster policy by its ID.

        Args:
            policy_id (str): The ID of the cluster policy.
            name (str): The updated name of the cluster policy.
            definition (dict): The updated definition of the cluster policy.

        Returns:
            dict: The updated cluster policy information.
        """
        import json

        assert (
            type(policy_id) == str
        ), f"Expected id to be of type str, found {type(policy_id)}"
        assert type(name) == str, f"Expected name to be of type str, found {type(name)}"
        assert (
            type(definition) == dict
        ), f"Expected definition to be of type dict, found {type(definition)}"

        params = {
            "policy_id": policy_id,
            "name": name,
            "definition": json.dumps(definition),
        }
        self.client.execute_post_json(f"{self.base_uri}/edit", params=params)
        return self.get_by_id(policy_id)

    def create_or_update(self, name, definition):
        """
        Create or update a cluster policy.

        If a policy with the given name already exists, it will be updated.
        Otherwise, a new policy will be created.

        Args:
            name (str): The name of the cluster policy.
            definition (dict): The definition of the cluster policy.

        Returns:
            dict: The created or updated cluster policy information.
        """
        policy = self.get_by_name(name)

        if policy is None:
            return self.create(name, definition)
        else:
            policy_id = policy.get("policy_id")
            return self.update_by_id(policy_id, name, definition)

    def delete_by_id(self, policy_id):
        """
        Delete a cluster policy by its ID.

        Args:
            policy_id (str): The ID of the cluster policy.

        Returns:
            dict: The response from the API.
        """
        return self.client.execute_post_json(
            f"{self.base_uri}/delete", params={"policy_id": policy_id}
        )

    def delete_by_name(self, name):
        """
        Delete a cluster policy by its name.

        Args:
            name (str): The name of the cluster policy.

        Returns:
            dict: The response from the API.
        """
        policy = self.get_by_name(name)
        assert policy is not None, f'A policy named "{name}" was not found.'

        policy_id = policy.get("policy_id")
        return self.delete_by_id(policy_id)
