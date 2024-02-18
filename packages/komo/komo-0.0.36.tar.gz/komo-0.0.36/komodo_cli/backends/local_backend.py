import os
import subprocess
from typing import Dict, Optional, Tuple
from uuid import getnode

import docker
from loguru import logger

from komodo_cli.backends.backend import Backend
from komodo_cli.image_builder.image_builder import ImageBuilder
from komodo_cli.types import (LOCAL_STATUS_MAPPING, ClientException, Job,
                              JobNotFoundException,
                              JobNotInDesiredStateException, JobStatus,
                              Machine, TooManyNodes)
from komodo_cli.utils import APIClient


class LocalBackend(Backend):
    config_params = ()
    resource_config_params = ()

    def __init__(self, name: str, api_client: APIClient, config: Dict, resources: Dict):
        super().__init__(name, api_client, config, resources)
        self.client = docker.from_env()

    def _docker_run(
        self,
        image,
        command,
        env,
        mounts,
        workdir,
        auto_remove=False,
    ):
        env["NODE_INDEX"] = 0
        env["NNODES"] = 1
        env["NODE_0_IP_ADDRESS"] = "localhost"
        container = self.client.containers.run(
            image=image,
            command=[
                "sh",
                "-c",
                " ".join(
                    f'"{a}"' if a not in ["&", "&&", "|", "||"] else a for a in command
                ),
            ],
            auto_remove=auto_remove,
            # cap_add=
            # cpu_count=
            # cpu_percent=
            detach=True,
            # devices=[],
            # https://stackoverflow.com/questions/71429711/how-to-run-a-docker-container-with-specific-gpus-using-docker-sdk-for-python
            # device_requests=[docker.types.DeviceRequest(device_ids=["0,2"], capabilities=[['gpu']])],
            environment=env,
            # mem_limit= #100000b, 1000k, 128m, 1g
            mounts=[
                docker.types.Mount(
                    target=m["target"],
                    source=m["source"] if m["source"] != "." else os.getcwd(),
                    type=m["type"],
                    read_only=False,
                )
                for m in mounts
            ],
            privileged=False,  # Does this need to be True to access devices?
            # runtime="nvidia",
            working_dir=workdir,
        )

        return container

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
        if num_nodes > 1:
            raise TooManyNodes(1)

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

        komodo_job_id = job.id

        try:
            container = self._docker_run(
                image,
                command,
                env,
                mounts,
                workdir,
            )
            backend_job_id = f"{getnode()}:{container.id[:12]}"
        except Exception as e:
            logger.error(f"Error starting container: {str(e)}")
            self.api_client.update_job(
                komodo_job_id,
                LOCAL_STATUS_MAPPING["dead"],  # TODO: need a failed job status?
            )
            raise e

        self.api_client.update_job(
            komodo_job_id,
            LOCAL_STATUS_MAPPING[container.status],
            backend_job_id,
        )

        return job

    def create_machine(
        self,
        machine_name: str,
        resource_name: dict,
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

        try:
            container = self._docker_run(
                image,
                ["tail", "-f", "/dev/null"],
                env,
                mounts,
                workdir,
                True,
            )
            backend_job_id = f"{getnode()}:{container.id[:12]}"
        except Exception as e:
            logger.error(f"Error starting container: {str(e)}")
            self.api_client.update_machine(
                machine_name,
                LOCAL_STATUS_MAPPING["dead"],  # TODO: need failed job status?
            )
            raise e

        self.api_client.update_machine(
            machine_name,
            LOCAL_STATUS_MAPPING[container.status],
            backend_job_id,
        )

        return machine

    def logs(self, job_id: str, node_index: int, watch: bool):
        try:
            if ":" in job_id:
                mac_address, container_id = job_id.split(":")
            else:
                mac_address = None
                container_id = job_id

            if mac_address and mac_address != str(getnode()):
                raise ClientException(
                    f"Cannot get logs for job because it was not started on this machine"
                )
            container = self.client.containers.get(container_id)
        except docker.errors.NotFound:
            raise JobNotFoundException
        return container.logs(follow=watch, stream=True)

    def shell(self, job_id: str, node_index: int):
        if ":" in job_id:
            mac_address, container_id = job_id.split(":")
        else:
            mac_address = None
            container_id = job_id

        if mac_address and mac_address != str(getnode()):
            raise ClientException(
                f"Cannot shell into job because it was not started on this computer"
            )

        # /bin/sh links to the installed shell, whatever it is
        subprocess.call(["docker", "exec", "-it", container_id, "/bin/sh"])

    def vscode(self, job_id: str, node_index: int):
        if ":" in job_id:
            mac_address, container_id = job_id.split(":")
        else:
            mac_address = None
            container_id = job_id

        if mac_address and mac_address != str(getnode()):
            raise ClientException(
                f"Cannot shell into job because it was not started on this computer"
            )

        container = self.client.containers.get(container_id)
        container_info = container.attrs
        workdir = container_info["Config"]["WorkingDir"]
        subprocess.call(
            [
                "bash",
                "-c",
                f'code --folder-uri vscode-remote://attached-container+$(printf "{container_id}" | xxd -p){workdir}',
            ]
        )

    def cancel(self, job_id: str):
        try:
            if ":" in job_id:
                mac_address, container_id = job_id.split(":")
            else:
                mac_address = None
                container_id = job_id

            if mac_address and mac_address != str(getnode()):
                raise ClientException(
                    f"Cannot cancel job because it was not started on this machine"
                )
            container = self.client.containers.get(container_id)
        except docker.errors.NotFound:
            raise JobNotFoundException
        except docker.errors.NullResource:
            raise JobNotFoundException
        container.kill()

    def delete(self, job_id: str):
        try:
            if ":" in job_id:
                mac_address, container_id = job_id.split(":")
            else:
                mac_address = None
                container_id = job_id

            if mac_address and mac_address != str(getnode()):
                raise ClientException(
                    f"Cannot cancel job because it was not started on this machine"
                )
            container = self.client.containers.get(container_id)
        except docker.errors.NotFound:
            raise JobNotFoundException
        except docker.errors.NullResource:
            raise JobNotFoundException
        container.remove(force=True)

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

        image = builder.build_image()
        return image.tags[0]
