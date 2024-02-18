import logging
import textwrap
from yaml import dump
from collections import OrderedDict
from cast_ai.se.models.workload_affinities import WorkloadAffinities


class WorkloadAffinitiesFingerprints:
    def __init__(self):
        self._logger = logging.getLogger(__name__)
        self._hash_mappings = {}

    def add_workload(self, workload_af: WorkloadAffinities):
        hash_value = workload_af.node_placement_spec_hash
        if hash_value not in self._hash_mappings:
            self._hash_mappings[hash_value] = {"spec": workload_af.node_placement_spec}
        self._hash_mappings[hash_value].setdefault(workload_af.workload_type, []).append(workload_af.name)

    def generate_report(self, detailed: bool = False) -> str:
        report = ""
        for hash_id in self._hash_mappings:
            report += f"Hash : [{hash_id}]\n"
            if detailed:
                report += "\t - Workloads:\n"
                for workload_type in self._hash_mappings[hash_id].keys():
                    if workload_type != "spec":
                        report += f"\t\t - {workload_type}\n"
                        for workload in self._hash_mappings[hash_id][workload_type]:
                            report += f"\t\t\t - {workload}\n"
                report += "\t - Affinities details:\n"
                if self._hash_mappings[hash_id]["spec"]["affinities"]:
                    if self._hash_mappings[hash_id]["spec"]["affinities"]["affinities_or"]:
                        report = self._add_affinities_to_report(hash_id, report)
                    if self._hash_mappings[hash_id]["spec"]["node_selector"]["labels_values"]:
                        report = self._add_node_selector_to_report(hash_id, report)
                    if self._hash_mappings[hash_id]["spec"]["tolerations"]["toelrations_values"]:
                        report = self._add_tolerations_to_report(hash_id, report)
        return report

    def _add_tolerations_to_report(self, hash_id, report):
        report += "\t\t - Tolerations:\n"
        for toleration in self._hash_mappings[hash_id]["spec"]["tolerations"]["toelrations_values"]:
            report += f"{self._format_toleration(toleration)}"
        return report

    def _add_node_selector_to_report(self, hash_id, report):
        report += "\t\t - Node Selector:\n"
        for n_selec in (self._hash_mappings[hash_id]["spec"]["node_selector"]["labels_values"].items()):
            yaml_rep = dump({n_selec[0]: n_selec[1]}, default_flow_style=False, sort_keys=False)
            indented_yaml = textwrap.indent(yaml_rep, '\t' * 3 + " - ")
            report += f"{indented_yaml}"
        return report

    def _add_affinities_to_report(self, hash_id, report):
        report += "\t\t - !Affinities(must):\n"
        for affinity_or in self._hash_mappings[hash_id]["spec"]["affinities"]["affinities_or"]:
            report += "\t\t\t -  *Affinities(or):\n"
            for nested_or_affinity in affinity_or["affinities_or"]:
                report += f"{self._format_nested_or_affinity(nested_or_affinity)}"
        return report

    def _format_toleration(self, toleration):
        new_dict = {
            "  - key": toleration["key"],
            "    operator": toleration["operator"],
            "    value": toleration["value"],
            "    effect": toleration["effect"]
        }
        yaml_rep = dump(new_dict, default_flow_style=False, sort_keys=False)
        indented_yaml = textwrap.indent(yaml_rep.replace("'", ""), '\t' * 3)
        return indented_yaml

    def _format_nested_or_affinity(self, nested_or_affinity):
        new_dict = OrderedDict({"  - key": nested_or_affinity.get("key", "")})
        if "operator" in nested_or_affinity:
            new_dict["    operator"] = nested_or_affinity["operator"]
        if "values" in nested_or_affinity:
            new_dict["    values"] = nested_or_affinity["values"]
        yaml_rep = dump(dict(new_dict), default_flow_style=False, sort_keys=False)
        indented_yaml = textwrap.indent(yaml_rep.replace("'", ""), '\t' * 4)
        yaml_lines = indented_yaml.split('\n')
        values_line_index = next((i for i, line in enumerate(yaml_lines) if "values:" in line),
                                 None)
        if values_line_index:
            for i in range(values_line_index + 1, len(yaml_lines)):
                yaml_lines[i] = "\t" + yaml_lines[i]
        yaml_lines.pop()
        yaml_lines[len(yaml_lines) - 1] = yaml_lines[len(yaml_lines) - 1] + "\n"
        formatted_yaml = '\n'.join(yaml_lines)
        return formatted_yaml
