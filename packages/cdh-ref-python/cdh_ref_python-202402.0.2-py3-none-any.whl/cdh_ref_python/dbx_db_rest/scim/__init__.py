from cdh_ref_python.dbx_db_rest import cdh_ref_pythonRestClient
from cdh_ref_python.dbx_rest import ApiContainer


class ScimClient(ApiContainer):
    def __init__(self, client: cdh_ref_pythonRestClient):
        self.client = client  # Client API exposing other operations to this class

        from cdh_ref_python.dbx_db_rest.scim.users import ScimUsersClient

        self.users = ScimUsersClient(self.client)

        from cdh_ref_python.dbx_db_rest.scim.service_principals import (
            ScimServicePrincipalsClient,
        )

        self.service_principals = ScimServicePrincipalsClient(self.client)

        from cdh_ref_python.dbx_db_rest.scim.groups import ScimGroupsClient

        self.groups = ScimGroupsClient(self.client)

    @property
    def me(self):
        raise Exception("The me() client is not yet supported.")
        # from cdh_ref_python.dbx_db_rest.scim.me import ScimMeClient
        # return ScimMeClient(self, self)
