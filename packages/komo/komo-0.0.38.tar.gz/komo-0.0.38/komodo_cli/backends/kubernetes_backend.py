import os
import subprocess
from typing import Dict, Optional, Tuple

from kubernetes import client
from kubernetes import watch as k8swatch
from kubernetes.client.rest import ApiException
from loguru import logger

import komodo_cli.printing as printing
from komodo_cli.backends.backend import Backend, ClientException, ConfigParam
from komodo_cli.image_builder.image_builder import ImageBuilder
from komodo_cli.types import Job, Machine
from komodo_cli.utils import APIClient


class KubernetesBackend(Backend):
    config_params = (
        ConfigParam("host", str, "URL of the cluster", True),
        ConfigParam("bearer_token", str, "token to access the cluster", True),
        ConfigParam(
            "docker_repo",
            str,
            "The Docker registry used to store job images",
            True,
        ),
    )
    resource_config_params = (
        ConfigParam("gpus", int, "number of gpus", True),
        ConfigParam("cpus", float, "number of cpus", True),
        ConfigParam("memMB", int, "amount of RAM, in MB", True),
        ConfigParam("instance_type", str, "instance type", False, default=""),
    )

    def __init__(self, name: str, api_client: APIClient, config: Dict, resources: Dict):
        super().__init__(name, api_client, config, resources)

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

    def logs(self, job_id: str, node_index: int, watch: bool):
        replica_id = f"{job_id}-sh-{node_index}-0"
        configuration = client.Configuration()
        configuration.host = self.config["host"]
        configuration.api_key["authorization"] = self.config["bearer_token"]
        configuration.api_key_prefix["authorization"] = "Bearer"
        configuration.verify_ssl = False
        configuration.assert_hostname = False
        client.Configuration.set_default(configuration)
        core_v1 = client.CoreV1Api()

        if watch:
            w = k8swatch.Watch()
            for e in w.stream(
                core_v1.read_namespaced_pod_log,
                name=replica_id,
                namespace="default",
            ):
                yield e
        else:
            api_response = core_v1.read_namespaced_pod_log(
                name=replica_id, namespace="default", follow=watch
            )
            yield api_response

    def shell(self, job_id: str, node_index: int):
        replica_id = f"{job_id}-sh-{node_index}-0"
        subprocess.call(
            [
                "kubectl",
                "--kubeconfig",
                "/dev/null",
                "--insecure-skip-tls-verify=true",
                "--server",
                self.config["host"],
                "--token",
                self.config["bearer_token"],
                "exec",
                "--stdin",
                "--tty",
                replica_id,
                "--",
                "/bin/sh",
            ]
        )

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
            base_image = "komodoai/base:latest"
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

        image = builder.build_image(self.config["docker_repo"])
        builder.push_image(image, self.config["docker_repo"])
        return image.tags[0]
