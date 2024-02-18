import click
from loguru import logger

import komodo_cli.printing as printing
from komodo_cli.backends.backend import Backend
from komodo_cli.backends.backend_factory import BackendFactory
from komodo_cli.backends.local_backend import (JobNotFoundException,
                                               JobNotInDesiredStateException)
from komodo_cli.utils import APIClient, handle_errors


@click.command("terminate")
@click.argument(
    "name",
    type=str,
)
@click.option(
    "--force",
    "-f",
    type=bool,
    is_flag=True,
    help="Delete the machine even if it cannot be reached. This can result in a machine continuing to run on your infrastructure, but no longer being tracked by Komodo. Use with caution.",
)
@click.pass_context
@handle_errors
def cmd_terminate(ctx: click.Context, name: str, force: bool):
    logger.info(f"Machine Name: {name}")

    api_client: APIClient = ctx.obj["api_client"]

    machine = api_client.get_machine(name)
    backend_schema = api_client.get_backend(machine.backend_name)
    backend: Backend = BackendFactory.get_backend(
        backend_schema,
        api_client,
    )

    printing.warning(f"Terminating machine {name}", bold=True)
    api_client.delete_machine(machine.name, force)
    # only the local backend actually does anything here
    try:
        backend.cancel(machine.backend_job_id)
    except JobNotFoundException as e:
        if not force:
            raise e
