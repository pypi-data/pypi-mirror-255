import json
import logging
import subprocess
import time
from datetime import datetime
from typing import Optional

from cast_ai.se.constants import CAST_NS
from cast_ai.se.misc_utils import get_get_deployments_command, validate_kctl_required_tools_exist
from cast_ai.se.models.execution_status import ExecutionStatus


class KubectlController:
    def __init__(self, context: str):
        self._logger = logging.getLogger(__name__)
        validate_kctl_required_tools_exist()
        self._cmd_prefix = f"kubectl --context {context}"
        self._context = context

    def trigger_cronjob(self, cronjob_name: str) -> ExecutionStatus:
        self._logger.info(f"{'-' * 70} Triggering {cronjob_name} cronjob")
        try:
            exec_timeout = 300
            exec_msg = "Cronjob still active..."
            job_name = self._create_cronjob_job(cronjob_name)
            for _ in range(exec_timeout):
                if self._has_job_completed(job_name):
                    exec_msg = ""
                    break
                else:
                    time.sleep(1)
            return ExecutionStatus(exec_msg)
        except Exception as e:
            self._logger.exception(f"An error occurred: {str(e)}")
            raise RuntimeError(f"An error occurred: {str(e)}")

    def _create_cronjob_job(self, cronjob_name) -> str:
        self._logger.info(f"Creating a job from {cronjob_name} in namespace {CAST_NS}")
        stamp = datetime.now().strftime("%d%m%H%M%S")
        job_name = f"{cronjob_name}-{stamp}"
        kubectl_cmd = ["kubectl", "--context", self._context, "create", "job", "-n", CAST_NS,
                       f"--from=cronjob/{cronjob_name}", job_name]
        result = subprocess.check_output(kubectl_cmd, text=True, shell=True)
        self._logger.debug(f"Command=[{' '.join(kubectl_cmd)} | Output=[{result.rstrip()}]")
        return job_name

    def scale_deployments(self, replica_count: int) -> ExecutionStatus:
        self._logger.info(f"{'-' * 70}[ Scaling Deployments to {replica_count} ]")
        try:
            # Get the list of deployments across all namespaces with namespace and name
            get_deployments_command = f"{self._cmd_prefix} {get_get_deployments_command(bool(not replica_count))}"
            result = subprocess.check_output(get_deployments_command, text=True, shell=True)
            deployments = result.split()
            self._logger.debug(f'Command=[{str(get_deployments_command)}] | Output=[{" ".join(deployments)}]')

            # Iterate over pairs of namespace and deployment name
            for i in range(0, len(deployments), 1):
                deployment_name = deployments[i]

                kubectl_cmd = (f"{self._cmd_prefix} scale --replicas={replica_count} deployment/{deployment_name} "
                               f"--namespace=default")
                result = subprocess.check_output(kubectl_cmd, text=True, shell=True)
                self._logger.debug(f'Command=[{" ".join(kubectl_cmd)}] | Output=[{result.rstrip()}]')
                self._logger.info(f"Deployment {deployment_name}[default] scaled to {replica_count} replicas.")
            return ExecutionStatus()
        except subprocess.CalledProcessError as e:
            self._logger.exception(f"Error executing kubectl command related to deployments scaling: {str(e)}")
            raise RuntimeError(f"Error executing kubectl command related to deployments scaling: {str(e)}")

    def _has_job_completed(self, job_name) -> Optional[bool]:
        try:
            command = f'{self._cmd_prefix} get job -n {CAST_NS} {job_name} -o json'
            result = subprocess.check_output(command, shell=True, text=True)
            job_info = json.loads(result)
            total_completions = job_info.get("spec", {}).get("completions", 1)
            succeeded = job_info["status"].get("succeeded", 0)
            failed = job_info["status"].get("failed", 0)
            if "succeeded" in job_info["status"] and succeeded + failed == total_completions:
                if job_info["status"].get("failed", 0) > 0:
                    self._logger.debug(f"The job '{job_name}' has completed with errors.")
                else:
                    self._logger.debug(f"The job '{job_name}' has completed successfully.")
                return True
            else:
                self._logger.debug(f"The job '{job_name}' is still running.")
                return False
        except subprocess.CalledProcessError as e:
            print(f"Error checking job status: {e}")
            return False

    def get_context_cloud_type(self) -> str:
        command = f"{self._cmd_prefix} cluster-info"
        try:
            result = subprocess.check_output(command, shell=True, text=True)
            if "eks.amazonaws.com" in result:
                self._logger.info("k8s cluster reflects it`s an EKS cluster")
                return "eks"
            elif "azmk8s.io" in result:
                self._logger.info("k8s cluster reflects it`s an AKS cluster")
                return "aks"
            self._logger.debug(f"k8s cluster reflects an unknown cluster type {result}")
            return ""
        except subprocess.CalledProcessError as e:
            self._logger.exception(f"Error executing/parsing kubectl command:{command} -=> {str(e)}")
            return ""
