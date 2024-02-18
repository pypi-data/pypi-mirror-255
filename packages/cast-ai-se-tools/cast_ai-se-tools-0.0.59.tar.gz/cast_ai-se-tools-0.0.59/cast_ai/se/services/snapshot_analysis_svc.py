import logging
from typing import Dict, Any, List

from cast_ai.se.constants import NON_RELEVANT_NAMESPACES, POD_SPEC_KEYWORDS, CLOUD_TAINTS, K8S_WORKLOADS, WORKLOAD_MAP
from cast_ai.se.services.workload_proccessing_svc import which_affinities_exist, process_tolerations
from cast_ai.se.models.refined_snapshot import RefinedSnapshot
from cast_ai.se.models.refined_snapshot_analysis import RefinedSnapshotAnalysis
from cast_ai.se.models.workload_affinities import WorkloadAffinities
from cast_ai.se.models.workload_affinities_fingerprints import WorkloadAffinitiesFingerprints


class SnapshotAnalyzer:
    def __init__(self):
        self._logger = logging.getLogger(__name__)
        self._refined_snapshot = RefinedSnapshot()
        self._rs_metadata = RefinedSnapshotAnalysis()
        self._node_affinities: List[WorkloadAffinities] = []
        self._workload_affinities_db = WorkloadAffinitiesFingerprints()

    def refine_snapshot(self, snapshot_data: Dict[str, Any]):
        self._refined_snapshot = RefinedSnapshot()
        self.refine_snapshot_workloads(snapshot_data)
        self._refine_snapshot_pdbs(snapshot_data)
        self._summarize_rs_object_types()
        # self._refine_snapshot_nodes(rf, snapshot_data)

    def _summarize_rs_object_types(self) -> None:

        for workload_type, workload_list in self._refined_snapshot.workloads.__dict__.items():
            for workload in workload_list:
                for reason in workload["refined_reason"]:
                    if workload["namespace"] not in self._rs_metadata[reason][workload_type]:
                        self._rs_metadata[reason][workload_type][workload["namespace"]] = set()
                    self._rs_metadata[reason][workload_type][workload["namespace"]].add(workload["name"])
                    self._rs_metadata[reason][workload_type]["total"] += 1
                    self._rs_metadata[reason]["total"] += 1
                    self._rs_metadata.counters["total"] += 1

    def _get_taints_or_tolerations(self, item: Dict[str, Any], keyword: str):
        taints_or_tolerations_list = []
        for taint_or_toleration in item["spec"][keyword]:
            if "key" not in taint_or_toleration.keys() or taint_or_toleration["key"] not in CLOUD_TAINTS:
                print()
                taints_or_tolerations_list.append(taint_or_toleration)
            else:
                if "key" not in item.keys():
                    self._logger.info(f'Ignored {keyword} as no key found')
                else:
                    self._logger.info(f'Ignored {keyword} as no key part of known cloud taints')
        return taints_or_tolerations_list

    def _refine_snapshot_pdbs(self, snapshot_data: Dict[str, Any]) -> None:
        if snapshot_data["podDisruptionBudgetList"]["items"]:
            for pdb in snapshot_data["podDisruptionBudgetList"]["items"]:
                if pdb["metadata"]["namespace"] in NON_RELEVANT_NAMESPACES:
                    self._logger.info(f'Ignored pdb {pdb["metadata"]["name"]} (it`s in {pdb["metadata"]["namespace"]})')
                    continue
                new_refined_pdb = {"name": pdb["metadata"]["name"],
                                   "namespace": pdb["metadata"]["namespace"],
                                   "spec": pdb["spec"]}
                self._logger.info(f'Found pdb {pdb["metadata"]["name"]} in {pdb["metadata"]["namespace"]}')
                self._refined_snapshot.pdbs.append(new_refined_pdb)

    def refine_snapshot_workloads(self, snapshot_data: Dict[str, Any]) -> None:
        self._analyze_snapshot_workloads(snapshot_data, mode="refine")

    def analyze_snapshot_affinities(self, snapshot_data: Dict[str, Any]) -> None:
        self._analyze_snapshot_workloads(snapshot_data, mode="gen_workload_affinities")

    def _analyze_snapshot_workloads(self, snapshot_data: Dict[str, Any], mode: str = "refine") -> None:
        for workload_key in K8S_WORKLOADS:
            if snapshot_data[workload_key]["items"]:
                self._logger.info(f"Starting to analyze workloads ({workload_key})...")
                for workload in snapshot_data[workload_key]["items"]:
                    if workload["metadata"]["namespace"] in NON_RELEVANT_NAMESPACES:
                        continue
                    if workload_key == "replicaSetList" and "ownerReferences" in workload["metadata"].keys():
                        continue
                    match mode:
                        case "refine":
                            self._refine_workload(workload, workload_key)
                        case "gen_workload_affinities":
                            node_selector, required_affinity, tolerations = which_affinities_exist(workload)
                            if required_affinity or node_selector or tolerations:
                                if workload["metadata"]["name"] == "job-with-toleration":
                                    print("")
                                self._process_workload_affinities(node_selector, required_affinity, tolerations,
                                                                  workload, workload_key)

                        case _:
                            self._logger.error(f"Invalid mode: {mode}. Skipping...")
        brief = self._workload_affinities_db.generate_report()
        detailed = self._workload_affinities_db.generate_report(detailed=True)
        print("")

    def _process_workload_affinities(self, node_selector, required_affinity, tolerations, workload, workload_key):
        w_a = WorkloadAffinities(workload["metadata"]["name"], WORKLOAD_MAP[workload_key][:-1])
        process_tolerations(w_a, required_affinity, node_selector, tolerations)
        w_a.digestify()
        self._node_affinities.append(w_a)
        self._workload_affinities_db.add_workload(w_a)

    def _refine_workload(self, workload: Dict[str, Any], workload_key: str):
        new_refined_workload = {"name": workload["metadata"]["name"],
                                "namespace": workload["metadata"]["namespace"],
                                "refined_reason": []}
        self._refine_podspec(new_refined_workload, workload)
        self._refine_tolerations(new_refined_workload, workload)
        if "requests" not in workload["spec"]["template"]["spec"].keys():
            new_refined_workload["refined_reason"].append("no_requests")
        if len(new_refined_workload) > 2:
            self._refined_snapshot.workloads.add_item(WORKLOAD_MAP[workload_key], new_refined_workload)

    def _get_workload_affinity(self, workload: Dict[str, Any], workload_key: str):
        new_refined_workload = {"name": workload["metadata"]["name"],
                                "namespace": workload["metadata"]["namespace"],
                                "refined_reason": []}
        self._refine_podspec(new_refined_workload, workload)
        self._refine_tolerations(new_refined_workload, workload)
        if "requests" not in workload["spec"]["template"]["spec"].keys():
            new_refined_workload["refined_reason"].append("no_requests")
        if len(new_refined_workload) > 2:
            self._refined_snapshot.workloads.add_item(WORKLOAD_MAP[workload_key], new_refined_workload)

    def _refine_tolerations(self, new_refined_workload: Dict[str, Any], workload: Dict[str, Any]) -> None:
        if "tolerations" in workload["spec"]["template"]["spec"].keys():
            toleration_list = self._get_taints_or_tolerations(workload["spec"]["template"], "tolerations")
            if toleration_list:
                new_refined_workload["tolerations"] = toleration_list
                self._logger.debug(f"Added toleration's data ({toleration_list}) to {new_refined_workload['name']}")
                new_refined_workload["refined_reason"].append("tolerations")

    def _refine_podspec(self, new_refined_workload: Dict[str, Any], workload: Dict[str, Any]) -> None:
        for spec_keyword in POD_SPEC_KEYWORDS:
            if spec_keyword in workload["spec"]["template"]["spec"].keys():
                new_refined_workload[spec_keyword] = workload["spec"]["template"]["spec"][spec_keyword]
                self._logger.debug(f"Added {spec_keyword} to {new_refined_workload['name']}")
                new_refined_workload["refined_reason"].append(spec_keyword)

    def generate_refined_workloads_report(self, detailed: bool = False) -> str:
        report = (f"{self._rs_metadata.counters['total']} "
                  f"Workloads with scheduling-challenging settings:\n")
        for reason in [key for key in self._rs_metadata.counters.keys() if key != "total"]:
            if self._rs_metadata.counters[reason]['total']:
                report += f"\t- {self._rs_metadata.counters[reason]['total']} workloads with {reason} field\n"
                report = self._add_workloads_to_report(detailed, reason, report)
        return report

    def generate_workloads_affinities_report(self, detailed: bool = False) -> str:
        pass

    def _add_workloads_to_report(self, detailed: bool, reason: str, report: str):
        for workload_type in [key for key in self._rs_metadata.counters[reason].keys() if key != "total"]:
            if self._rs_metadata.counters[reason][workload_type]['total']:
                report += (f"\t\t- {self._rs_metadata.counters[reason][workload_type]['total']} {workload_type}"
                           f"\n")
                if detailed:
                    report = self._add_detailed_workloads_to_report(reason, report, workload_type)
        return report

    def _add_detailed_workloads_to_report(self, reason: str, report: str, workload_type: str) -> str:
        for namespace in self._rs_metadata.counters[reason][workload_type].keys():
            if namespace != "total":
                report += f"\t\t\t- {namespace}\n"
                for workload_name in (
                        list(self._rs_metadata.counters[reason][workload_type][namespace])):
                    report += f"\t\t\t\t- {workload_name}\n"
        return report
