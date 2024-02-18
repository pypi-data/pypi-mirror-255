import json
import logging
import subprocess

from google.cloud import container_v1
from google.oauth2 import service_account

from cast_ai.se.contollers.cloud_controller import CloudController
from cast_ai.se.models.cloud_confs import GkeConfig
from cast_ai.se.models.execution_status import ExecutionStatus

from cast_ai.se.constants import GCP_AUTH_SCOPE


class GKEController(CloudController):
    def __init__(self, gke_conf: GkeConfig):
        try:
            self._conf = gke_conf
            self._logger = logging.getLogger(__name__)
            credentials = service_account.Credentials.from_service_account_file(self._conf.json_path,
                                                                                scopes=[GCP_AUTH_SCOPE])
            self._client = container_v1.ClusterManagerClient(credentials=credentials)
        except Exception as e:
            self._logger.critical(f"An error occurred during GKEController initialization: {str(e)}")
            raise RuntimeError(f"An error occurred during GKEController initialization: {str(e)}")

    def disable_autoscaler(self) -> ExecutionStatus:
        # TODO: ...implement this method
        return ExecutionStatus()

    def get_node_count(self) -> int:
        try:
            command = f"kubectl --context {self._conf.k8s_context} get nodes -o=json"
            result = subprocess.run(command, shell=True, capture_output=True, text=True, check=True)
            nodes = json.loads(result.stdout)
            node_count = sum(1 for node in nodes.get('items', []) if node.get('metadata', {}).get('labels', {}).get(
                'cloud.google.com/gke-nodepool') == self._conf.node_pool)
            return node_count
        except subprocess.CalledProcessError as e:
            self._logger.exception(f"Error trying to get node count on nodepool {self._conf.node_pool}: {str(e)}")
            raise RuntimeError(f"Error trying to get node count on nodepool {self._conf.node_pool}: {str(e)}")

    def _get_node_pool_path(self):
        cluster_path = f"projects/{self._conf.project_id}/locations/{self._conf.zone}/clusters/{self._conf.cluster_name}"
        node_pool_path = f"{cluster_path}/nodePools/{self._conf.node_pool}"
        return node_pool_path

    def scale(self, node_count: int) -> ExecutionStatus:
        try:
            node_pool_path = self._get_node_pool_path()
            update_request = container_v1.SetNodePoolSizeRequest(name=node_pool_path, node_count=node_count)
            self._client.set_node_pool_size(request=update_request)
            return ExecutionStatus()
        except Exception as e:
            self._logger.critical(f"An error occurred during GKEController initialization: {str(e)}")
            raise RuntimeError(f"An error occurred during GKEController initialization: {str(e)}")
