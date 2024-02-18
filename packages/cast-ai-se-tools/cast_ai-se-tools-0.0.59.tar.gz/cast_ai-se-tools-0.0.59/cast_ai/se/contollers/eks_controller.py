import logging
import time
import boto3

from cast_ai.se.models.cloud_confs import EksConfig
from cast_ai.se.models.execution_status import ExecutionStatus
from cast_ai.se.contollers.cloud_controller import CloudController


class EKSController(CloudController):
    def __init__(self, aws_conf: EksConfig):
        try:
            self.conf = aws_conf
            self._logger = logging.getLogger(__name__)
            self._client = boto3.client(
                'autoscaling',
                region_name=self.conf.region,
                aws_access_key_id=self.conf.access_key,
                aws_secret_access_key=self.conf.access_secret_key
            )
        except Exception as e:
            self._logger.critical(f"An error occurred during EKSController initialization: {str(e)}")
            raise RuntimeError(f"An error occurred during EKSController initialization: {str(e)}")

    def disable_autoscaler(self) -> ExecutionStatus:
        self.scale(0)
        return ExecutionStatus()

    def get_node_count(self) -> int:
        ec2_client = boto3.client('ec2', region_name=self.conf.region,
                                  aws_access_key_id=self.conf.access_key,
                                  aws_secret_access_key=self.conf.access_secret_key)

        try:
            response = ec2_client.describe_instances(Filters=[
                {
                    'Name': 'tag:aws:autoscaling:groupName',
                    'Values': [f"{self.conf.asg}"]
                },
                {
                    'Name': f'tag:kubernetes.io/cluster/{self.conf.cluster_name}/nodegroup',
                    'Values': [f"{self.conf.ng}"]
                },
                {
                    'Name': 'instance-state-name',
                    'Values': ['running']
                }
            ])

            # Extract the count of running instances
            running_node_count = sum([len(reservations['Instances']) for reservations in response['Reservations']])
            return running_node_count
        except Exception as e:
            self._logger.exception(f"Error trying to get Nodes count: {str(e)}")
            raise RuntimeError(f"Error trying to get Nodes count: {str(e)}")

    def scale(self, node_count: int) -> ExecutionStatus:
        self._logger.info(f"{'-' * 70}[ Scaling EKS Auto Scaling Group to {node_count} ]")

        try:
            for _ in range(5):
                response = self._client.update_auto_scaling_group(
                    AutoScalingGroupName=self.conf.asg,
                    MinSize=node_count,
                    MaxSize=node_count + 1,  # You can adjust the max size as needed
                    DesiredCapacity=node_count,
                )
                if response["ResponseMetadata"]["HTTPStatusCode"] == 200:
                    if not self._is_asg_scaled(node_count):
                        self._logger.warning(f"Default asg=({self.conf.asg}) has still not changed going to retry")
                        time.sleep(1)
                        continue
                    else:
                        self._logger.debug(f"Successfully updated EKS Auto Scaling Group"
                                           f" [{self.conf.asg}] : [{str(response)}]")
                        self._logger.info('Successfully updated EKS Auto Scaling Group')
                        return ExecutionStatus()
                else:
                    self._logger.error(f"Scaling default ng result = [{response}]")
                    return ExecutionStatus(f'HTTP {response["ResponseMetadata"]["HTTPStatusCode"]}')
        except Exception as e:
            self._logger.exception(f"Error trying to set Demo Nodes capacity: {str(e)}")
            raise RuntimeError(f"Error trying to set Demo Nodes capacity: {str(e)}")

    def _is_asg_scaled(self, node_count: int) -> bool:
        validate_asg_response = self._client.describe_auto_scaling_groups(AutoScalingGroupNames=[self.conf.asg])
        self._logger.debug(f"Validating ASG={validate_asg_response['AutoScalingGroups'][0]}")
        return (validate_asg_response["AutoScalingGroups"][0]["DesiredCapacity"] == node_count and
                validate_asg_response["AutoScalingGroups"][0]["MinSize"] == node_count)
