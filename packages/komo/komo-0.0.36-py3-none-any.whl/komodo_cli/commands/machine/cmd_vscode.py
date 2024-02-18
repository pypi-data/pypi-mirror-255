import sys

import click
from loguru import logger

import komodo_cli.printing as printing
from komodo_cli.backends.backend import Backend
from komodo_cli.backends.backend_factory import BackendFactory
from komodo_cli.types import JobStatus
from komodo_cli.utils import APIClient, handle_errors


@click.command("vscode")
@click.argument(
    "name",
    type=str,
)
@click.pass_context
@handle_errors
def cmd_vscode(ctx: click.Context, name: str):
    logger.info(f"Machine: {name}")

    api_client: APIClient = ctx.obj["api_client"]

    machine = api_client.get_machine(name)

    if machine.status != JobStatus.RUNNING:
        printing.error(f"Machine {name} is not running", bold=True)
        exit(1)

    backend_schema = api_client.get_backend(machine.backend_name)
    backend: Backend = BackendFactory.get_backend(
        backend_schema,
        api_client,
    )

    printing.header(f"Opening a VSCode session into machine {name}", bold=True)
    backend.vscode(machine.backend_job_id, 0)
