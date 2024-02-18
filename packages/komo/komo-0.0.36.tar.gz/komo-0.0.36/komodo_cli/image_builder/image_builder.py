import os
import uuid
from typing import Optional

import docker
from loguru import logger

import komodo_cli.printing as printing
from komodo_cli.types import ImageBuildException, ImagePushException

KOMODO_DOCKERFILE_NAME = "komodo.Dockerfile"


class ImageBuilder:
    def __init__(
        self, base_image: str, project_dir: str, install_requirements: bool = False
    ):
        self.dockerfile = f"FROM {base_image}"
        if install_requirements:
            requirements_file = os.path.join(project_dir, "requirements.txt")
            if os.path.isfile(requirements_file):
                self.dockerfile += "\nCOPY requirements.txt /tmp/requirements.txt"
                self.dockerfile += (
                    "\nRUN pip install --no-cache-dir -r /tmp/requirements.txt"
                )

        self.project_dir = project_dir
        self.client = docker.from_env()

    def add_overlay(self, overlay_dir, dest_dir):
        self.dockerfile += f"\nCOPY {overlay_dir} {dest_dir}"

    def set_workdir(self, workdir):
        self.dockerfile += f"\nWORKDIR {workdir}"

    def build_image(self, overlay_images_repository: Optional[str] = None):
        printing.info("Building image...")
        dockerfile_path = os.path.join(self.project_dir, KOMODO_DOCKERFILE_NAME)

        with open(dockerfile_path, "w") as f:
            f.write(self.dockerfile)

        uid = str(uuid.uuid4())
        if overlay_images_repository:
            tag = f"{overlay_images_repository}:{uid}"
        else:
            tag = f"komodo-overlay:{uid}"

        try:
            image, build_logs = self.client.images.build(
                path=os.path.dirname(dockerfile_path),
                tag=tag,
                quiet=False,
                rm=True,
                pull=True,
                forcerm=True,
                dockerfile=dockerfile_path,
                platform="linux/amd64",  # TODO
            )
            return image
        except (
            docker.errors.BuildError,
            docker.errors.APIError,
            TypeError,
        ) as e:
            raise ImageBuildException(str(e))
        except Exception as e:
            raise e
        finally:
            os.remove(dockerfile_path)

    def push_image(self, image, overlay_images_repository):
        printing.info("Pushing image...")
        try:
            resp = self.client.images.push(
                overlay_images_repository,
                image.tags[0].split(":")[-1],
                stream=True,
                decode=True,
            )

            for line in resp:
                if "error" in line:
                    raise ImagePushException(line["error"])
        except ImagePushException as e:
            raise e
        except Exception as e:
            raise ImagePushException(str(e))
