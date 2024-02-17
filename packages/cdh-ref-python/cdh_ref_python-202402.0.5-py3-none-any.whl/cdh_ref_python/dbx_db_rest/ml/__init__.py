from cdh_ref_python.dbx_db_rest import cdh_ref_pythonRestClient
from cdh_ref_python.dbx_rest import ApiContainer


class MlClient(ApiContainer):
    def __init__(self, client: cdh_ref_pythonRestClient):
        self.client = client  # Client API exposing other operations to this class

        from cdh_ref_python.dbx_db_rest.ml.feature_store import FeatureStoreClient

        self.feature_store = FeatureStoreClient(self.client)

        from cdh_ref_python.dbx_db_rest.ml.mlflow import MLflowClient

        self.mlflow = MLflowClient(self.client)
