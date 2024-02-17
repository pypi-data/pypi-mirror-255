from cdh_ref_python.dbx_rest import ApiClient, ApiContainer

__all__ = ["Sql"]


class Sql(ApiContainer):
    def __init__(self, client: ApiClient):
        super().__init__()

        from cdh_ref_python.rest.permissions.sql.warehouses import SqlWarehouses

        self.warehouses = SqlWarehouses(client)
        self.endpoints = self.warehouses

        from cdh_ref_python.rest.permissions.sql.crud import SqlCrud

        self.queries = SqlCrud(client, "query", "queries")
        self.dashboards = SqlCrud(client, "dashboard")
        self.data_sources = SqlCrud(client, "data_source")
        self.alerts = SqlCrud(client, "alert")
