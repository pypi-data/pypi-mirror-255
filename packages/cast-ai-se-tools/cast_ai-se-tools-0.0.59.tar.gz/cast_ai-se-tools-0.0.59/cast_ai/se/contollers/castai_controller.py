import logging
from typing import Dict, Any

from cast_ai.se.constants import API_SERVER, EXTERNAL_CLUSTER_PREFIX, NODES_POSTFIX, CLUSTERS_PREFIX, POLICIES_POSTFIX, \
    AUDIT_PREFIX, CLUSTER_Q, RECONCILE_POSTFIX
from cast_ai.se.models.execution_status import ExecutionStatus
from cast_ai.se.services.api_requests_svc import cast_api_get, cast_api_put, cast_api_delete, cast_api_post


class CastController:
    def __init__(self, cast_api_key: str, default_cluster_id: str):
        self._logger = logging.getLogger(__name__)
        self._api_key = cast_api_key

        self._cluster_id = default_cluster_id
        self.cluster = None
        self._get_cluster_info()

    def _get_cluster_info(self):
        get_cluster_info_url = f"{API_SERVER}{EXTERNAL_CLUSTER_PREFIX}{self._cluster_id}"
        self.cluster = cast_api_get(get_cluster_info_url, self._api_key)

    def get_nodes(self) -> Dict[str, Any]:
        get_nodes_url = f"{API_SERVER}{EXTERNAL_CLUSTER_PREFIX}{self._cluster_id}{NODES_POSTFIX}"
        return cast_api_get(get_nodes_url, self._api_key)

    def delete_nodes(self, nodes) -> ExecutionStatus:
        self._logger.info(f"{'-' * 70}[ Deleting Nodes via CAST API ]")
        # TODO: add failure logic (return)
        for node in nodes["items"]:
            delete_node_url = f"{API_SERVER}{EXTERNAL_CLUSTER_PREFIX}{self._cluster_id}{NODES_POSTFIX}/{node['id']}"
            cast_api_delete(delete_node_url, self._api_key)
        return ExecutionStatus()

    def enable_existing_policies(self) -> ExecutionStatus:
        self._logger.info(f"{'-' * 70}[ Enabling CAST policies ]")
        current_policies = self.get_policies()
        if current_policies['enabled']:
            self._logger.warning("Current policies were already enabled")
            return ExecutionStatus()
        current_policies['enabled'] = True
        return self._set_policies(current_policies)

    def _set_policies(self, policies: Dict[str, Any]) -> ExecutionStatus:
        set_policies_url = f"{API_SERVER}{CLUSTERS_PREFIX}{self._cluster_id}{POLICIES_POSTFIX}"
        result = cast_api_put(set_policies_url, self._api_key, policies)
        # TODO: Add logic for failed execution
        return ExecutionStatus()

    def get_policies(self) -> Dict[str, Any]:
        get_policies_url = f"{API_SERVER}{CLUSTERS_PREFIX}{self._cluster_id}{POLICIES_POSTFIX}"
        return cast_api_get(get_policies_url, self._api_key)

    def are_policies_disabled(self) -> bool:
        try:
            return not self.get_policies()["enabled"]
        except Exception as e:
            raise Exception(e)

    def is_downscaler_disabled(self) -> bool:
        try:
            return not self.get_policies()["nodeDownscaler"]["enabled"]
        except Exception as e:
            raise Exception(e)

    def is_upscaler_disabled(self) -> bool:
        try:
            return not self.get_policies()["unschedulablePods"]["enabled"]
        except Exception as e:
            raise Exception(e)

    def disable_downscaler_policy(self) -> ExecutionStatus:
        self._logger.info(f"{'-' * 70}[ Disabling Node deletion policy ]")
        current_policies = self.get_policies()
        if not current_policies['nodeDownscaler']["enabled"]:
            self._logger.warning("Node deletion policy already disabled")
            return ExecutionStatus()
        else:
            current_policies['nodeDownscaler']["enabled"] = False
            return self._set_policies(current_policies)

    def disable_unscheduled_pods_policy(self) -> ExecutionStatus:
        self._logger.info(f"{'-' * 70}[ Disabling Unscheduled pods policy ]")
        current_policies = self.get_policies()
        if not current_policies['unschedulablePods']["enabled"]:
            self._logger.warning("Unscheduled pod policy already disabled")
            return ExecutionStatus()
        else:
            current_policies['unschedulablePods']["enabled"] = False
            return self._set_policies(current_policies)

    def get_audit(self) -> Dict[str, Any]:
        get_cluster_info_url = f"{API_SERVER}{AUDIT_PREFIX}{CLUSTER_Q}{self._cluster_id}&page.limit=750"
        return cast_api_get(get_cluster_info_url, self._api_key)

    def reconcile(self) -> ExecutionStatus:
        reconcile_url = f"{API_SERVER}{EXTERNAL_CLUSTER_PREFIX}{self._cluster_id}{RECONCILE_POSTFIX}"
        cast_api_post(reconcile_url, self._api_key, {})
        return ExecutionStatus()
