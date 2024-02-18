import time

import click

import komodo_cli.printing as printing
from komodo_cli.types import BackendStatus
from komodo_cli.utils import APIClient, handle_errors


@click.command("update")
@click.option(
    "--backend",
    "-b",
    type=str,
    required=True,
    help="Name of the backend to update",
)
@click.pass_context
@handle_errors
def cmd_update(
    ctx: click.Context,
    backend: str,
):
    api_client: APIClient = ctx.obj["api_client"]
    backend_name = backend

    api_client.update_backend(backend_name)

    printing.info("Waiting for backend to finish updating...")
    while True:
        backend = api_client.get_backend(backend_name)
        if backend.status == BackendStatus.VALID:
            break

        if backend.status == BackendStatus.ERROR:
            printing.error(
                f"Backend '{backend_name}' failed to update with the following error:\n{backend.status_message}"
            )
            exit(1)

        time.sleep(5)

    printing.success(f"Backend '{backend_name}' succesfully updated")
