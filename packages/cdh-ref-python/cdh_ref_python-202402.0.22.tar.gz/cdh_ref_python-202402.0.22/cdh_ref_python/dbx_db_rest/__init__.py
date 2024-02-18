from cdh_ref_python.dbx_rest.common import ApiClient


class cdh_ref_pythonRestClient(ApiClient):
    """Databricks Academy REST API client."""

    def __init__(
        self,
        token: str = None,
        endpoint: str = None,
        throttle_seconds: int = 0,
        *,
        user: str = None,
        password: str = None,
        authorization_header: str = None,
        client: ApiClient = None,
        verbose: bool = False,
    ):
        """
        Create a Databricks REST API client.

        This is similar to ApiClient.__init__ except the parameter order is different to ensure backwards compatibility.

        Args:
            endpoint: The common base URL to the API endpoints.  e.g. https://workspace.cloud.databricks.com/API/
            token: The API authentication token.  Defaults to None.
            user: The authentication username.  Defaults to None.
            password: The authentication password.  Defaults to None.
            authorization_header: The header to use for authentication.
                By default, it's generated from the token or password.
            client: A parent ApiClient from which to clone settings.
            throttle_seconds: Number of seconds to sleep between requests.
        """
        if endpoint is None:
            from cdh_ref_python_gems import dbgems

            endpoint = dbgems.get_notebooks_api_endpoint()

        if not any((authorization_header, token, password)):
            from cdh_ref_python_gems import dbgems

            token = dbgems.get_notebooks_api_token()
            if verbose:
                print(f"Using notebook token.")
        else:
            if verbose:
                print(f"Using caller-provided token.")

        url = endpoint.rstrip("/") + "/api/"

        super().__init__(
            url,
            token=token,
            user=user,
            password=password,
            authorization_header=authorization_header,
            client=client,
            throttle_seconds=throttle_seconds,
            verbose=verbose,
        )

        self.endpoint = endpoint

        from cdh_ref_python.dbx_db_rest.clusters import ClustersClient

        self.clusters = ClustersClient(self)

        from cdh_ref_python.dbx_db_rest.cluster_policies import ClustersPolicyClient

        self.cluster_policies = ClustersPolicyClient(self)

        from cdh_ref_python.dbx_db_rest.instance_pools import InstancePoolsClient

        self.instance_pools = InstancePoolsClient(self)

        from cdh_ref_python.dbx_db_rest.jobs import JobsClient

        self.jobs = JobsClient(self)

        from cdh_ref_python.dbx_db_rest.ml import MlClient

        self.ml = MlClient(self)

        from cdh_ref_python.rest.permissions import Permissions

        self.permissions = Permissions(self)

        from cdh_ref_python.dbx_db_rest.pipelines import PipelinesClient

        self.pipelines = PipelinesClient(self)

        from cdh_ref_python.dbx_db_rest.repos import ReposClient

        self.repos = ReposClient(self)

        from cdh_ref_python.dbx_db_rest.runs import RunsClient

        self.runs = RunsClient(self)

        from cdh_ref_python.dbx_db_rest.scim import ScimClient

        self.scim = ScimClient(self)

        from cdh_ref_python.dbx_db_rest.sql import SqlClient

        self.sql = SqlClient(self)

        from cdh_ref_python.dbx_db_rest.tokens import TokensClient

        self.tokens = TokensClient(self)

        from cdh_ref_python.dbx_db_rest.token_management import TokenManagementClient

        self.token_management = TokenManagementClient(self)

        from cdh_ref_python.dbx_db_rest.uc import UcClient

        self.uc = UcClient(self)

        from cdh_ref_python.dbx_db_rest.workspace import WorkspaceClient

        self.workspace = WorkspaceClient(self)

    def vprint(self, what):
        if self.verbose:
            print(what)
