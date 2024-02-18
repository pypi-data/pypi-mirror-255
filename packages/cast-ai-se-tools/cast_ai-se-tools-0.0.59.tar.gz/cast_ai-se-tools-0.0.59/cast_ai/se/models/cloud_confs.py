import logging
from azure.identity import ClientSecretCredential


class EksConfig:
    def __init__(self, eks_conf: dict):
        self._logger = self._logger = logging.getLogger(__name__)
        try:
            self.region = eks_conf["REGION"]
            self.asg = eks_conf["AUTOSCALING_GROUP"]
            self.ng = eks_conf["NODE_GROUP"]
            self.cluster_name = eks_conf["CLUSTER_NAME"]
            self.access_key = eks_conf["ACCESS_KEY"]
            self.access_secret_key = eks_conf["ACCESS_SECRET_KEY"]
        except Exception as e:
            self._logger.critical(f"Was not able to initialize eks config:{str(e)}")
            raise RuntimeError(f"Was not able to initialize eks config:{str(e)}")


class AksConfig:
    def __init__(self, aks_conf: dict):
        self._logger = self._logger = logging.getLogger(__name__)
        try:
            self.k8s_context = aks_conf["K8S_CONTEXT"]
            self.tenant_id = aks_conf["TENANT_ID"]
            self.node_pool = aks_conf["NODE_POOL"]
            self.client_id = aks_conf["CLIENT_ID"]
            self.client_secret = aks_conf["CLIENT_SECRET"]
            self.credential = ClientSecretCredential(self.tenant_id, self.client_id, self.client_secret)
            self.subscription_id = aks_conf["SUBSCRIPTION_ID"]
            self.cluster_name = aks_conf["CLUSTER_NAME"]
            self.resource_group = aks_conf["RESOURCE_GROUP"]
        except Exception as e:
            self._logger.critical(f"Was not able to initialize aks config:{str(e)}")
            raise RuntimeError(f"Was not able to initialize aks config:{str(e)}")


class GkeConfig:
    def __init__(self, gke_conf: dict):
        self._logger = self._logger = logging.getLogger(__name__)
        try:
            self.k8s_context = gke_conf["K8S_CONTEXT"]
            self.project_id = gke_conf["PROJECT_ID"]
            self.zone = gke_conf["ZONE"]
            self.node_pool = gke_conf["NODE_POOL"]
            self.cluster_name = gke_conf["CLUSTER_NAME"]
            self.json_path = gke_conf["JSON_KEY_PATH"]
        except Exception as e:
            self._logger.critical(f"Was not able to initialize gke config:{str(e)}")
            raise RuntimeError(f"Was not able to initialize gke config:{str(e)}")
