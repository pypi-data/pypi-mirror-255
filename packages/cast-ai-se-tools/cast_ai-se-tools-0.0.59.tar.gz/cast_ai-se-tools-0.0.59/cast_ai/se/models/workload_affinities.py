import hashlib
import json
import logging
from typing import Dict, Any, List


class WorkloadAffinities:
    def __init__(self, name: str, workload_type: str):
        self._logger = logging.getLogger(__name__)
        self._name = name
        self._workload_type = workload_type
        self._node_placement_spec = {
            "affinities": {"affinities_or": [], "hash": ""},
            "node_selector": {"labels_values": {}, "hash": ""},
            "tolerations": {"toelrations_values": [], "hash": ""},
            "hash": ""
        }

    @property
    def name(self):
        return self._name

    @property
    def workload_type(self):
        return self._workload_type

    @property
    def node_placement_spec_hash(self):
        return self._node_placement_spec["hash"]

    @property
    def node_placement_spec(self):
        return self._node_placement_spec

    def digestify(self):
        ordered_keys = [self._node_placement_spec["affinities"]["hash"],
                        self._node_placement_spec["node_selector"]["hash"],
                        self._node_placement_spec["tolerations"]["hash"]]
        combined_hashes = ".".join(val for val in ordered_keys)
        self._node_placement_spec["hash"] = hashlib.sha256(combined_hashes.encode('utf-8')).hexdigest().upper()
        print("")

    def populate_nodeselector(self, selectors: Dict[str, Any]):
        try:
            hash_value = hashlib.sha256(json.dumps(selectors, sort_keys=True).encode('utf-8')).hexdigest().upper()
            self._node_placement_spec["node_selector"]["labels_values"] = selectors
            self._node_placement_spec["node_selector"]["hash"] = hash_value
        except Exception as e:
            self._logger.critical(f"An error occurred during populating node_selector details: {str(e)}")
            raise RuntimeError(f"An error occurred during populating node_selector detailes: {str(e)}")

    def populate_tolerations(self, tolerations: List[Dict[str, Any]]):
        try:
            hashable_tolerations_list = [
                {
                    "key": toleration["key"],
                    "operator": toleration["operator"],
                    "value": toleration.get("value", ""),
                    "effect": toleration.get("effect", "")
                }
                for toleration in tolerations
            ]
            sorted_hashable_tolerations_list = sorted(hashable_tolerations_list,
                                                      key=lambda x: (x["key"], x["operator"], x["value"], x["effect"]))
            hash_value = hashlib.sha256(json.dumps(sorted_hashable_tolerations_list, sort_keys=True).encode('utf-8'))
            self._node_placement_spec["tolerations"]["toelrations_values"] = sorted_hashable_tolerations_list
            self._node_placement_spec["tolerations"]["hash"] = hash_value.hexdigest().upper()
        except Exception as e:
            self._logger.critical(f"An error occurred during populating node_selector details: {str(e)}")
            raise RuntimeError(f"An error occurred during populating node_selector details: {str(e)}")

    def populate_affinities(self, selector_terms: List[Dict[str, Any]]):
        try:
            affinities_or_hash_list = []
            for term in selector_terms:
                affinities_or_list = []
                for match_exp in term["matchExpressions"]:
                    if "values" in match_exp.keys():
                        match_exp["values"].sort()
                    affinities_or_list.append(match_exp)
                sorted_affinities_or_list = sorted(affinities_or_list,
                                                   key=lambda x: (x["key"], x["operator"], sorted(x.get("values", []))))

                hash_value = hashlib.sha256(json.dumps(sorted_affinities_or_list, sort_keys=True).encode('utf-8'))
                hash_value_digested = hash_value.hexdigest().upper()
                affinities_or_dict = {"affinities_or": sorted_affinities_or_list, "hash": hash_value_digested}
                self._node_placement_spec["affinities"]["affinities_or"].append(affinities_or_dict)
            hash_value = hashlib.sha256(json.dumps(affinities_or_hash_list, sort_keys=True).encode('utf-8'))
            self._node_placement_spec["affinities"]["hash"] = hash_value.hexdigest().upper()
        except Exception as e:
            self._logger.critical(f"An error occurred during populating affinities: {str(e)}")
            raise RuntimeError(f"An error occurred during populating affinities: {str(e)}")
