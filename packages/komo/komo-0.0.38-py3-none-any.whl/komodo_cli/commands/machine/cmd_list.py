import sys

import click
from tabulate import tabulate

import komodo_cli.printing as printing
from komodo_cli.utils import APIClient, handle_errors


@click.command("list")
@click.pass_context
@handle_errors
def cmd_list(ctx: click.Context):
    api_client: APIClient = ctx.obj["api_client"]

    machines = api_client.list_machines()

    machines_to_print = [
        [
            machine.name,
            machine.status.value,
            machine.backend_name,
            machine.resource_name,
            machine.backend_job_id,
        ]
        for machine in machines
    ]

    printing.header(f"Found {len(machines)} Komodo machines\n", bold=True)
    printing.info(
        tabulate(
            machines_to_print,
            headers=["Name", "Status", "Backend", "Resource", "Backend Job ID"],
            tablefmt="simple_grid",
        ),
    )
