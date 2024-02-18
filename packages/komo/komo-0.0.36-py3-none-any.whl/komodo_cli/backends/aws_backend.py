import json
import os
import stat
import subprocess
import tempfile
from copy import deepcopy
from typing import Dict, Optional, Tuple

import boto3
import botocore
from loguru import logger

from komodo_cli import printing
from komodo_cli.backends.backend import Backend, ConfigParam
from komodo_cli.image_builder.image_builder import ImageBuilder
from komodo_cli.types import ClientException, Job, Machine
from komodo_cli.utils import APIClient


class AWSBackend(Backend):
    config_params = (ConfigParam("region", str, "eg. us-east-1", True),)
    resource_config_params = (
        ConfigParam("instance_type", str, "eg. g4dn.xlarge", True),
        ConfigParam(
            "volume_size", int, "size, in GB, of the root EBS volume", True, default=100
        ),
    )

    def __init__(self, name: str, api_client: APIClient, config: Dict, resources: Dict):
        super().__init__(name, api_client, config, resources)

        session = boto3.Session(
            region_name=config["region"],
        )
        self._batch_client = session.client("batch", region_name=config["region"])
        self._ec2_client = session.client("ec2", region_name=config["region"])
        self._logs_client = session.client("logs", region_name=config["region"])
        self._ecs_client = session.client("ecs", region_name=config["region"])

    def run(
        self,
        command: Tuple[str],
        num_nodes: int,
        resource_name: str,
        image: str,
        env: Dict[str, str],
        mounts: list,
        workdir: str,
    ) -> Job:
        job = self.api_client.create_job(
            self.name,
            command,
            num_nodes,
            image,
            env,
            mounts,
            workdir,
            resource_name,
        )

        return job

    def create_machine(
        self,
        machine_name: str,
        resource_name: str,
        image: str,
        env: Dict[str, str],
        mounts: list,
        workdir: str,
    ) -> Machine:
        machine = self.api_client.create_machine(
            machine_name,
            self.name,
            image,
            env,
            mounts,
            workdir,
            resource_name,
        )
        return machine

    def _get_job(self, job_id: str, node_index: int) -> dict:
        job_id = f"{job_id}#{node_index}"
        try:
            jobs = self._batch_client.describe_jobs(jobs=[job_id])["jobs"]
            if len(jobs) == 0:
                raise ClientException(f"AWS Batch job {job_id} not found")

            assert len(jobs) == 1
            job = jobs[0]

            return job
        except botocore.exceptions.ClientError as err:
            logger.error(str(err))
            raise err

    def logs(self, job_id: str, node_index: int, watch: bool):
        job = self._get_job(job_id, node_index)

        if job.get("status", None) == "RUNNING":
            log_stream_name = job["container"]["logStreamName"]
        else:
            attempts = job["attempts"]
            if len(attempts) == 0:
                return

            attempt = attempts[-1]
            container = attempt["container"]
            log_stream_name = container["logStreamName"]

        next_token = None

        while True:
            args = {}
            if next_token is not None:
                args["nextToken"] = next_token

            try:
                response = self._logs_client.get_log_events(
                    logGroupName="/aws/batch/job",
                    logStreamName=log_stream_name,
                    limit=10000,
                    startFromHead=True,
                    **args,
                )
            except self._logs_client.exceptions.ResourceNotFoundException:
                return
            if response["nextForwardToken"] == next_token:
                # we've reached the end of the available logs

                # if watch is False, then we end here
                if not watch:
                    break

                # if the job is running, we wait for more logs
                job = self._get_job(job_id, node_index)
                if job["status"] == "RUNNING":
                    continue

                # if the job is not running, then we end here
                break

            next_token = response["nextForwardToken"]

            for event in response["events"]:
                yield event["message"] + "\n"

    def shell(self, job_id: str, node_index: int):
        job = self._get_job(job_id, node_index)
        status = job["status"]
        if status != "RUNNING":
            raise ClientException("Job is not running, cannot shell into it")

        task_arn = job["container"]["taskArn"]
        job_queue_arn = job["jobQueue"]
        job_queue = self._batch_client.describe_job_queues(jobQueues=[job_queue_arn])[
            "jobQueues"
        ][0]

        # these are all the possible compute environments that the job could've been scheduled on
        possible_compute_environment_arns = [
            e["computeEnvironment"] for e in job_queue["computeEnvironmentOrder"]
        ]
        possible_compute_environments = (
            self._batch_client.describe_compute_environments(
                computeEnvironments=possible_compute_environment_arns,
            )["computeEnvironments"]
        )

        # these are all the possible ECS clusters (corresponding to AWS Batch compute environments) that
        # the job could be running in
        possible_ecs_cluster_arns = [
            e["ecsClusterArn"] for e in possible_compute_environments
        ]

        job_cluster_arn = None
        task = None
        for cluster_arn in possible_ecs_cluster_arns:
            tasks = self._ecs_client.describe_tasks(
                cluster=cluster_arn,
                tasks=[task_arn],
            )["tasks"]

            if len(tasks) == 0:
                continue

            job_cluster_arn = cluster_arn
            task = tasks[0]
            break

        if job_cluster_arn is None:
            raise ClientException(
                "Could not find the corresponding ECS cluster for the job"
            )

        container_arn = task["containerInstanceArn"]
        container_instance = self._ecs_client.describe_container_instances(
            containerInstances=[container_arn],
            cluster=job_cluster_arn,
        )["containerInstances"][0]

        ec2_instance_id = container_instance["ec2InstanceId"]

        instance = self._ec2_client.describe_instances(
            InstanceIds=[ec2_instance_id],
        )[
            "Reservations"
        ][0]["Instances"][0]

        private_ip = instance.get("PrivateDnsName", None)
        if private_ip is None:
            raise ClientException("Cannot find IP address for instance")

        key = tempfile.mktemp()
        with open(key, "w") as f:
            f.write(self.config["ssh-key"])
        os.chmod(key, stat.S_IRUSR)

        p = subprocess.Popen(
            [
                "ssh",
                "-vvv",
                "-i",
                key,
                "-o",
                "StrictHostKeyChecking=no",
                "-o",
                "IdentitiesOnly=yes",
                f"ec2-user@{private_ip}",
                "-o",
                f"proxycommand ssh -W %h:%p -i {key} -o IdentitiesOnly=yes ec2-user@{self.config['bastion-ip-address']}",
                "docker",
                "ps",
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        stdout, stderr = p.communicate()
        rc = p.returncode

        if rc != 0:
            raise ClientException(f"Got error: \n{stderr.decode('utf-8')}")

        stdout = stdout.decode("utf-8")
        lines = stdout.splitlines()
        if lines[0].split()[0] != "CONTAINER":
            raise ClientException("Cannot find docker container")

        num_amazon_containers = 0
        non_amazon_containers = []
        for line in lines[1:]:
            if not line:
                continue
            parts = line.split(" ")
            parts = [p for p in parts if p]

            container_id = parts[0]
            image = parts[1]
            if image.startswith("amazon"):
                num_amazon_containers += 1
            else:
                non_amazon_containers.append(container_id)

        if num_amazon_containers == 0 or len(non_amazon_containers) != 1:
            raise ClientException("Cannot find docker container")

        container_id = non_amazon_containers[0]

        subprocess.call(
            [
                "ssh",
                "-t",
                "-i",
                key,
                "-o",
                "StrictHostKeyChecking=no",
                "-o",
                "IdentitiesOnly=yes",
                "-o",
                f"proxycommand ssh -W %h:%p -i {key} -o IdentitiesOnly=yes ec2-user@{self.config['bastion-ip-address']}",
                f"ec2-user@{private_ip}",
                f"docker exec -it {container_id} /bin/bash",
            ]
        )

        os.remove(key)

    def cancel(self, job_id: str):
        pass

    def delete(self, job_id: str):
        pass

    @staticmethod
    def supports_shell() -> bool:
        return True

    def prepare_image(
        self,
        base_image: Optional[str],
        project_dir: str,
        workspace: Optional[str],
        workdir: Optional[str],
    ) -> str:
        if base_image is None:
            base_image = "komodoai/aws:latest"
            install_requirements = True
        else:
            install_requirements = False
        builder = ImageBuilder(base_image, project_dir, install_requirements)

        if workspace:
            if not workdir:
                raise ClientException(
                    "Workspace was provided but no workdir was provided"
                )
            builder.add_overlay(workspace, workdir)

        if workdir:
            builder.set_workdir(workdir)

        docker_repo = self.config["docker-repo"]
        image = builder.build_image(docker_repo)
        # log in to ECR
        if "dkr.ecr" in docker_repo:
            exit_status = os.system(
                f"aws ecr get-login-password --region {self.config['region']} | docker login --username AWS --password-stdin {docker_repo}"
            )
            if exit_status != 0:
                raise ClientException("Failed to log in with ECR")

        builder.push_image(image, docker_repo)
        return image.tags[0]

    @staticmethod
    def assert_ready_for_use():
        sts_client = boto3.client("sts")
        try:
            sts_client.get_caller_identity()
        except botocore.exceptions.ClientError:
            raise ClientException(
                "You are not logged in with the AWS CLI. Please login and try again."
            )

    @staticmethod
    def setup(config: dict, api_client: APIClient) -> dict:
        config = deepcopy(config)

        session = boto3.Session(region_name=config["region"])
        iam_client = session.client("iam")
        sts_client = session.client("sts")
        ec2_client = session.client("ec2")

        try:
            aws_account_id = sts_client.get_caller_identity()["Account"]
            user_id = api_client.get_user_id()

            # first check if the default security group has an SSH rule that isn't created by Komodo,
            # and if it does, delete it
            # we do this because the server will create this rule, and if it already exists, it will
            # throw an error
            sg_response = ec2_client.describe_security_groups(GroupNames=["default"])
            sgs = sg_response["SecurityGroups"]

            if len(sgs) == 0:
                raise ClientException(
                    "To create an AWS backend, you must have a default VPC set up with a default security group"
                )
            if len(sgs) > 1:
                raise ClientException("Found more than one default security group")
            sg = sgs[0]
            ssh_rule_exists = False
            group_id = sg["GroupId"]
            for perm in sg["IpPermissions"]:
                if (
                    perm.get("IpProtocol", "") == "tcp"
                    and perm.get("FromPort", -1) == 22
                    and perm.get("ToPort", -1) == 22
                ):
                    ip_ranges = perm.get("IpRanges", [])
                    if len(ip_ranges) == 1:
                        ipr = ip_ranges[0]
                        if (
                            ipr.get("Description", "") != "Created by Komodo"
                            and ipr.get("CidrIp", "") == "0.0.0.0/0"
                        ):
                            ssh_rule_exists = True

            if ssh_rule_exists:
                printing.info(
                    "Found existing inbound SSH security rule. Deleting temporarily so that the Komodo platform can re-create it and manage it."
                )
                ec2_client.revoke_security_group_ingress(
                    CidrIp="0.0.0.0/0",
                    FromPort=22,
                    ToPort=22,
                    GroupId=group_id,
                    GroupName="default",
                    IpProtocol="tcp",
                )

            iam_role_name = f"komodo-role-{user_id}"
            policy_name = f"komodo-policy-{user_id}"
            policy_arn = f"arn:aws:iam::{aws_account_id}:policy/{policy_name}"

            try:
                role_response = iam_client.get_role(RoleName=iam_role_name)
            except iam_client.exceptions.NoSuchEntityException:
                printing.info(
                    "Creating IAM Role to allow the Komodo server access to your account"
                )

                try:
                    policy_response = iam_client.get_policy(PolicyArn=policy_arn)
                except iam_client.exceptions.NoSuchEntityException:
                    policy_response = iam_client.create_policy(
                        PolicyName=policy_name,
                        PolicyDocument=json.dumps(
                            {
                                "Version": "2012-10-17",
                                "Statement": [
                                    {
                                        "Effect": "Allow",
                                        "Action": [
                                            "batch:*",
                                            "ecs:*",
                                            "ec2:*",
                                            "logs:*",
                                            "ecr:*",
                                            "cloudwatch:*",
                                            "iam:*",
                                        ],
                                        "Resource": "*",
                                    },
                                    {
                                        "Effect": "Allow",
                                        "Action": ["iam:CreateServiceLinkedRole"],
                                        "Resource": "*",
                                        "Condition": {
                                            "StringEquals": {
                                                "iam:AWSServiceName": "batch.amazonaws.com"
                                            }
                                        },
                                    },
                                ],
                            }
                        ),
                        Description="These are the permissions that the Komodo server will have to be able to manage your infrastructure",
                    )

                role_response = iam_client.create_role(
                    RoleName=iam_role_name,
                    AssumeRolePolicyDocument=json.dumps(
                        {
                            "Version": "2012-10-17",
                            "Statement": [
                                {
                                    "Sid": "Statement1",
                                    "Effect": "Allow",
                                    "Principal": {"AWS": "211125406737"},
                                    "Condition": {
                                        "StringEquals": {
                                            "sts:ExternalId": user_id,
                                        }
                                    },
                                    "Action": "sts:AssumeRole",
                                }
                            ],
                        }
                    ),
                )

                attach_response = iam_client.attach_role_policy(
                    RoleName=iam_role_name,
                    PolicyArn=policy_arn,
                )
        except botocore.exceptions.BotoCoreError as e:
            raise ClientException(str(e))

        role_arn = role_response["Role"]["Arn"]
        config["komodo_role_arn"] = role_arn

        return config
