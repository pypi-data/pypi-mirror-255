import os
import time
from typing import Optional

import click
from loguru import logger
from vyper import Vyper

import komodo_cli.printing as printing
from komodo_cli.backends.backend import Backend
from komodo_cli.backends.backend_factory import BackendFactory
from komodo_cli.types import JobStatus
from komodo_cli.utils import (APIClient, config_args_to_dict, handle_errors,
                              update_context_project_config_with_overrides,
                              update_context_with_project_config)


@click.command("create")
@click.argument(
    "name",
    type=str,
)
@click.option(
    "--backend",
    "-b",
    type=str,
    default=None,
    help="Name of the backend to use.",
)
@click.option(
    "--resource",
    "-r",
    type=str,
    default=None,
    help="Resource type to use for the job as defined in the config file. Ignored for local jobs.",
)
@click.option(
    "--config",
    "-c",
    type=str,
    default="",
    help=(
        "Override any parameters in the section of your project config corresponding to the specified backend."
        "Values must be provided as a comma-separated list of key=value pairs."
    ),
)
@click.option("--detach", "-d", is_flag=True)
@click.pass_context
@handle_errors
def cmd_create(
    ctx: click.Context,
    name: str,
    backend: Optional[str],
    resource: Optional[str],
    config: str,
    detach: bool,
):
    api_client: APIClient = ctx.obj["api_client"]
    backend_schema = api_client.get_backend(backend)
    backend_name = backend_schema.name

    update_context_with_project_config(ctx, backend_name)
    backend_config_override = config_args_to_dict(config)
    update_context_project_config_with_overrides(ctx, backend_config_override)
    project_config: dict = ctx.obj["project_config"]

    backend: Backend = BackendFactory.get_backend(
        backend_schema,
        api_client,
    )
    backend.assert_ready_for_use()

    if resource is None:
        if backend_schema.type != "local":
            printing.error("No resource was specified", bold=True)
            exit(1)

    logger.info(f"Using backend {backend_name}")
    logger.info(f"Resource: {resource}")

    if not backend.supports_shell():
        printing.error(
            f"Backend {backend_name} does not support machines",
            bold=True,
        )
        return

    workspace = project_config["workspace"]
    workdir = project_config["workdir"]
    image = backend.prepare_image(
        project_config["image"], ctx.obj["project_dir"], workspace, workdir
    )
    project_config["image"] = image

    printing.header("Starting a machine", bold=True)
    machine = backend.create_machine(
        name,
        resource,
        project_config["image"],
        project_config["env"],
        project_config["mounts"],
        project_config["workdir"],
    )

    printing.success(
        f"Created a machine on backend {machine.backend_name} with name {machine.name}",
        bold=True,
    )

    if detach:
        return

    printing.success("Waiting for machine to start...", bold=True)

    while True:
        machine = api_client.get_machine(name)
        status = machine.status
        if status != JobStatus.PENDING:
            break
        time.sleep(1)

    backend.shell(machine.backend_job_id, 0)
