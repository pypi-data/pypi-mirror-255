from cdh_ref_python.dbx_rest import ApiClient
from cdh_ref_python.rest.permissions.crud import PermissionsCrud

__all__ = ["ClusterPolicies"]


class ClusterPolicies(PermissionsCrud):
    valid_permissions = ["CAN_USE"]

    def __init__(self, client: ApiClient):
        super().__init__(
            client, "2.0/preview/permissions/cluster-policies", "cluster-policies"
        )
