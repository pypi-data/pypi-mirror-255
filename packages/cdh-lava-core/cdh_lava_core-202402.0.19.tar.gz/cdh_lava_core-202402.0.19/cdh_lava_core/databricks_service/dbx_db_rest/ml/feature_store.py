from cdh_lava_core.databricks_service.dbx_db_rest import RestClient
from cdh_lava_core.databricks_service.dbx_rest.common import ApiContainer


class FeatureStoreClient(ApiContainer):
    """
    A client for interacting with the feature store API.

    Args:
        client (RestClient): The REST client used for making API requests.

    Attributes:
        client (RestClient): The REST client used for making API requests.
        base_uri (str): The base URI for the feature store API.
    """

    def __init__(self, client: RestClient):
        """
        Initializes a FeatureStore object.

        Args:
            client (RestClient): The REST client used to communicate with the feature store API.
        """
        self.client = client
        self.base_uri = f"{self.client.endpoint}/api/2.0/feature-store/"

    def search_tables(self, max_results: int = 10) -> dict:
        """
        Search for feature tables in the feature store.

        Args:
            max_results (int): The maximum number of results to return. Defaults to 10.

        Returns:
            dict: A dictionary containing the search results, or an empty list if no results are found.
        """
        results = self.client.execute_get_json(
            f"{self.base_uri}/feature-tables/search?max_results={max_results}"
        )
        return results.get("feature_tables", [])
