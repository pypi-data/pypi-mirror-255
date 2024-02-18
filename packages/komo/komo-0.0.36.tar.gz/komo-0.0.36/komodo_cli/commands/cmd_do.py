import os

import click
import yaml

import komodo_cli.printing as printing
from komodo_cli.commands.cmd_run import _run_helper
from komodo_cli.utils import handle_errors


@click.command("do")
@click.option("--file", "-f", type=str, required=True)
@click.option("--detach", "-d", is_flag=True)
@click.pass_context
@handle_errors
def cmd_do(ctx: click.Context, file: str, detach: bool):
    if not os.path.isfile(file):
        printing.error(
            f"{file} does not exist",
            bold=True,
        )

    with open(file, "r") as f:
        task = yaml.load(f, yaml.FullLoader)

    kind = task["kind"]

    if kind == "job":
        # TODO: use vyper for defaults
        backend = task.get("backend", None)
        resource = task.get("resource", None)
        num_nodes = task.get("num_nodes", 1)
        backend_config_override = task.get("config", {})
        command = task["command"]
        _run_helper(
            ctx,
            backend,
            resource,
            num_nodes,
            backend_config_override,
            detach,
            command,
        )
    # TODO: add support for machine tasks
    else:
        printing.error(f"Task of type {kind} is not supported", bold=True)
        exit(1)
