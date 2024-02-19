from cdh_dav_python.databricks_service.dbx_db_rest import RestClient
from cdh_dav_python.databricks_service.dbx_rest.common import ApiContainer


class MlClient(ApiContainer):
    def __init__(self, client: RestClient):
        self.client = client  # Client API exposing other operations to this class

        from cdh_dav_python.dbx_db_rest.ml.feature_store import FeatureStoreClient

        self.feature_store = FeatureStoreClient(self.client)

        from cdh_dav_python.dbx_db_rest.ml.mlflow import MLflowClient

        self.mlflow = MLflowClient(self.client)
