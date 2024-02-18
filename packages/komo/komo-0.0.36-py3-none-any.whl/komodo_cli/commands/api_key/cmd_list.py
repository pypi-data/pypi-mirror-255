import click

import komodo_cli.printing as printing
from komodo_cli.utils import (APIClient, handle_errors,
                              update_context_with_api_client)


@click.command("list")
@click.pass_context
@handle_errors
def cmd_list(ctx: click.Context):
    update_context_with_api_client(ctx)
    api_client: APIClient = ctx.obj["api_client"]

    tokens = api_client.get_all_tokens()

    printing.header(
        f"All of your API keys are below:\n",
    )
    printing.info("\n".join(tokens))
