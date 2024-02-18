from typing import Dict, Any


class RefinedSnapshot:
    def __init__(self):
        self.pdbs = []
        self.workloads = WorkloadObject()


class WorkloadObject:
    def __init__(self):
        self.deployments = []
        self.replica_sets = []
        self.daemon_sets = []
        self.stateful_sets = []
        self.jobs = []

    def add_item(self, item_type: str, item_data: Dict[str, Any]) -> None:
        match item_type:
            case 'deployments':
                self.deployments.append(item_data)
            case 'replica_sets':
                self.replica_sets.append(item_data)
            case 'daemon_sets':
                self.daemon_sets.append(item_data)
            case 'stateful_sets':
                self.stateful_sets.append(item_data)
            case 'jobs':
                self.jobs.append(item_data)
            case _:
                raise ValueError(f"Invalid item type: {item_type}")
