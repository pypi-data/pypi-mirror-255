import click

import komodo_cli.printing as printing
from komodo_cli.utils import APIClient, handle_errors


@click.command("delete-resource")
@click.option(
    "--backend",
    "-b",
    type=str,
    default=None,
    help="Name of the backend containing the resource to delete",
)
@click.option(
    "--resource",
    "-r",
    type=str,
    default=None,
    help="Name of the resource to delete",
)
@click.pass_context
@handle_errors
def cmd_delete_resource(
    ctx: click.Context,
    backend: str,
    resource: str,
):
    api_client: APIClient = ctx.obj["api_client"]

    printing.warning(
        "Deleting a resource will delete all jobs and machines associated with this resource. Are you sure you want to continue?",
        nl=False,
    )
    confirmed = click.confirm("")
    if not confirmed:
        return

    api_client.delete_backend_resource(
        backend,
        resource,
    )

    printing.success(f"Resource '{resource}' is being deleted from backend '{backend}'")
