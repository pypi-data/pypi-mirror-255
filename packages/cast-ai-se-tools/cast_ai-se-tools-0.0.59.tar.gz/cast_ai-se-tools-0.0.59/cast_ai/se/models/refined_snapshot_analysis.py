from cast_ai.se.constants import WORKLOAD_MAP, K8S_WORKLOADS


class RefinedSnapshotAnalysis:
    def __init__(self):
        self.counters = {
            "nodeSelector": {},
            "topologySpreadConstraints": {},
            "affinity": {},
            "runtimeClassName": {},
            "no_requests": {},
            "tolerations": {},
            "total": 0
        }
        for reason in self.counters.keys():
            if reason != "total":
                self.counters[reason] = {WORKLOAD_MAP[workload]: {"total": 0} for workload in K8S_WORKLOADS}
                self.counters[reason]["total"] = 0

    def __getitem__(self, key):
        return self.counters[key]
