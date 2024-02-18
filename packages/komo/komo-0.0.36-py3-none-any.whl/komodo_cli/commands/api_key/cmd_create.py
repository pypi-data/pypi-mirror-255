import os

import click

import komodo_cli.printing as printing
from komodo_cli.utils import APIClient, handle_errors


@click.command("create")
@click.pass_context
@handle_errors
def cmd_create(ctx: click.Context):
    """Log into Komodo and create an API key."""
    api_key_file = os.path.join(os.path.expanduser("~"), ".komo", "api-key")
    os.makedirs(os.path.dirname(api_key_file), exist_ok=True)
    if os.path.exists(api_key_file):
        # Prompt the user for action
        if not click.confirm(
            f"The file {api_key_file} already exists. Do you want to replace it?",
            default=False,
        ):
            printing.warning("Operation cancelled.")
            return

    printing.warning(
        f"Enter your Komodo credentials to get the API key",
    )
    email = None
    while email is None:
        email = click.prompt("email", default=None, type=str)

    password = None
    while password is None:
        password = click.prompt(
            "password",
            default=None,
            type=str,
            hide_input=True,
        )

    printing.info(
        f"Fetching Komodo API key...",
    )
    client = APIClient(username=email, password=password)

    api_key_file = os.path.join(os.path.expanduser("~"), ".komo", "api-key")
    os.makedirs(os.path.dirname(api_key_file), exist_ok=True)
    with open(api_key_file, "w") as f:
        f.write(client.access_token)

    printing.header(
        f"Your API key is below. It has also been written to ~/.komo/api-key",
    )
    printing.info(client.access_token)
