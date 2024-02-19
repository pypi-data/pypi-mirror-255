from cdh_lava_core.databricks_service.dbx_db_rest import RestClient
from cdh_lava_core.databricks_service.dbx_rest.common import ApiContainer


class ScimClient(ApiContainer):
    def __init__(self, client: RestClient):
        self.client = client  # Client API exposing other operations to this class

        from cdh_lava_core.dbx_db_rest.scim.users import ScimUsersClient

        self.users = ScimUsersClient(self.client)

        from cdh_lava_core.dbx_db_rest.scim.service_principals import (
            ScimServicePrincipalsClient,
        )

        self.service_principals = ScimServicePrincipalsClient(self.client)

        from cdh_lava_core.dbx_db_rest.scim.groups import ScimGroupsClient

        self.groups = ScimGroupsClient(self.client)

    @property
    def me(self):
        raise Exception("The me() client is not yet supported.")
        # from cdh_lava_core.dbx_db_rest.scim.me import ScimMeClient
        # return ScimMeClient(self, self)
