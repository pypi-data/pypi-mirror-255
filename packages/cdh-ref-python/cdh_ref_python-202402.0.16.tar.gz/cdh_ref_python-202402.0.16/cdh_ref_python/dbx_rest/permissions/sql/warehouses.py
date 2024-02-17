from cdh_ref_python.dbx_rest import ApiClient
from cdh_ref_python.rest.permissions.crud import PermissionsCrud

__all__ = ["SqlWarehouses"]


class SqlWarehouses(PermissionsCrud):
    valid_permissions = ["CAN_USE", "CAN_MANAGE"]

    def __init__(self, client: ApiClient):
        super().__init__(client, "2.0/permissions/sql/endpoints", "endpoints")
