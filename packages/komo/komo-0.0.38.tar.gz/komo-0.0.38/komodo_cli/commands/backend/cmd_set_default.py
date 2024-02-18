import time

import click

import komodo_cli.printing as printing
from komodo_cli.types import BackendStatus
from komodo_cli.utils import APIClient, handle_errors


@click.command("set-default")
@click.option(
    "--backend",
    "-b",
    type=str,
    required=True,
    help="Name of the backend to set as default",
)
@click.pass_context
@handle_errors
def cmd_set_default(
    ctx: click.Context,
    backend: str,
):
    api_client: APIClient = ctx.obj["api_client"]
    backend_name = backend

    api_client.set_default_backend(backend_name)

    printing.success(f"Backend '{backend_name}' succesfully set as default")
