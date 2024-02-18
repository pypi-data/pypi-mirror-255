import click

import komodo_cli.printing as printing
from komodo_cli.utils import (APIClient, handle_errors,
                              update_context_with_api_client)


@click.command("delete")
@click.argument(
    "api-key",
    type=str,
)
@click.pass_context
@handle_errors
def cmd_delete(ctx: click.Context, api_key: str):
    update_context_with_api_client(ctx)
    api_client: APIClient = ctx.obj["api_client"]

    api_client.delete_token(api_key)
    printing.success(f"API Key {api_key} has been successfully deleted")
