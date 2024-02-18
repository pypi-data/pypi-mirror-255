import click
from loguru import logger
from tabulate import tabulate

import komodo_cli.printing as printing
from komodo_cli.utils import (APIClient, handle_errors,
                              update_context_with_api_client)


@click.command("apply-promo-code")
@click.argument(
    "code",
    type=str,
)
@click.pass_context
@handle_errors
def cmd_apply_promo_code(ctx: click.Context, code: str):
    """List Komodo jobs."""
    logger.info("Listing jobs")

    update_context_with_api_client(ctx)
    api_client: APIClient = ctx.obj["api_client"]

    api_client.apply_promo_code(code)
    printing.success(f"Promo code {code} successfully applied")
