from cdh_lava_core.databricks_service.dbx_db_rest import RestClient
from cdh_lava_core.databricks_service.dbx_rest.common import ApiContainer


class UcClient(ApiContainer):
    def __init__(self, client: RestClient):
        self.client = client

    def metastore_summary(self):
        return self.client.execute_get_json(
            f"{self.client.endpoint}/api/2.0/unity-catalog/metastore_summary"
        )

    def set_default_metastore(self, workspace_id, catalog_name, metastore_id) -> str:
        payload = {"default_catalog_name": catalog_name, "metastore_id": metastore_id}
        return self.client.execute_put_json(
            f"{self.client.endpoint}/api/2.0/unity-catalog/workspaces/{workspace_id}/metastore",
            payload,
        )
