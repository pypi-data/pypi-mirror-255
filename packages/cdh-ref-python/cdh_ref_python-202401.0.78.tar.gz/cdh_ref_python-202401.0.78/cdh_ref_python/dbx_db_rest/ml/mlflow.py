from cdh_ref_python.dbx_db_rest import cdh_ref_pythonRestClient
from cdh_ref_python.dbx_rest import ApiContainer


class MLflowClient(ApiContainer):
    """
    A client for interacting with MLflow endpoints.

    Args:
        client (cdh_ref_pythonRestClient): The REST client used for making API requests.

    Attributes:
        client (cdh_ref_pythonRestClient): The REST client used for making API requests.
        base_uri (str): The base URI for MLflow API endpoints.

    """

    def __init__(self, client: cdh_ref_pythonRestClient):
`       """
        Initializes an instance of the MLFlow class.

        Args:
            client (cdh_ref_pythonRestClient): The REST client used to communicate with the CDH Reference Python API.
        """
        self.client = client
        self.base_uri = f"{self.client.endpoint}/api/2.0/preview/mlflow/"

    def get_endpoint_status(self, model_name):
        """
        Retrieves the status of an MLflow endpoint for a given model.

        Args:
            model_name (str): The name of the registered model.

        Returns:
            str: The status of the MLflow endpoint.
        """
        url = f"{self.base_uri}/endpoints/get-status?registered_model_name={model_name}"
        return self.client.execute_get_json(url).get("endpoint_status")

    def wait_for_endpoint(self, model_name, delay_seconds=10):
        import time

        while True:
            endpoint_status = self.get_endpoint_status(model_name)
            state = endpoint_status.get("state")
            if state == "ENDPOINT_STATE_READY":
                time.sleep(
                    delay_seconds
                )  # Give it a couple extra seconds to complete the transition
                return print(f"Endpoint is ready ({state})")

            print(f"Endpoint not ready ({state}), waiting {delay_seconds} seconds")
            time.sleep(delay_seconds)  # Wait N seconds

    def list_endpoint_versions(self, model_name):
        url = f"{self.base_uri}/endpoints/list-versions"
        if model_name is not None:
            url += f"?registered_model_name={model_name}"

        return self.client.execute_get_json(url).get("endpoint_versions", [])

    def wait_for_endpoint_version(self, model_name, version_name, delay_seconds=10):
        import time

        while True:
            for version in self.list_endpoint_versions(model_name):
                if version.get("endpoint_version_name") == str(version_name):
                    state = version.get("state")
                    if state == "VERSION_STATE_READY":
                        time.sleep(
                            delay_seconds
                        )  # Give it a couple extra seconds to complete the transition
                        return print(f"Endpoint version is ready ({state})")
                    else:
                        print(
                            f"Version not ready ({state}), waiting {delay_seconds} seconds"
                        )
                        time.sleep(delay_seconds)
