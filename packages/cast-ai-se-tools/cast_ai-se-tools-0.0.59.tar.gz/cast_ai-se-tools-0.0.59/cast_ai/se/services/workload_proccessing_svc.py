from typing import Optional, List, Dict, Any

from cast_ai.se.models.workload_affinities import WorkloadAffinities


def which_affinities_exist(workload):
    affinity = workload["spec"]["template"]["spec"].get("affinity", {})
    node_selector = workload["spec"]["template"]["spec"].get("nodeSelector", {})
    tolerations = workload["spec"]["template"]["spec"].get("tolerations", {})
    node_affinity = affinity.get("nodeAffinity", {})
    required_affinity = node_affinity.get("requiredDuringSchedulingIgnoredDuringExecution", {})
    return node_selector, required_affinity, tolerations


def process_tolerations(workload_affinities: WorkloadAffinities, required_aff: Optional[dict] = None,
                        node_selector: Optional[dict] = None, tolerations: List[Dict[str, Any]] = None) -> bool:
    affinities_exist = False
    if required_aff:
        workload_affinities.populate_affinities(required_aff["nodeSelectorTerms"])
        affinities_exist = True
    if node_selector:
        workload_affinities.populate_nodeselector(node_selector)
        affinities_exist = True
    if tolerations:
        workload_affinities.populate_tolerations(tolerations)
        affinities_exist = True
    return affinities_exist
