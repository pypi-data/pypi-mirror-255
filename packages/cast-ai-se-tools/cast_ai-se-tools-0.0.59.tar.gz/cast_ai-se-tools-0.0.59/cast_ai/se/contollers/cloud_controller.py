from abc import ABC, abstractmethod

from cast_ai.se.models.execution_status import ExecutionStatus


class CloudController(ABC):
    @abstractmethod
    def scale(self, node_count: int) -> ExecutionStatus:
        pass

    @abstractmethod
    def disable_autoscaler(self) -> ExecutionStatus:
        pass

    @abstractmethod
    def get_node_count(self) -> int:
        pass
