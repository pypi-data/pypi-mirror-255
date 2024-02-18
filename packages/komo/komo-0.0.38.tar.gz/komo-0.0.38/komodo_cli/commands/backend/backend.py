import click

from komodo_cli.commands.backend.cmd_add_resource import cmd_add_resource
from komodo_cli.commands.backend.cmd_create import cmd_create
from komodo_cli.commands.backend.cmd_delete import cmd_delete
from komodo_cli.commands.backend.cmd_delete_resource import cmd_delete_resource
from komodo_cli.commands.backend.cmd_list import cmd_list
from komodo_cli.commands.backend.cmd_set_default import cmd_set_default
from komodo_cli.commands.backend.cmd_update import cmd_update
from komodo_cli.utils import update_context_with_api_client


@click.group()
@click.pass_context
def backend(ctx: click.Context):
    update_context_with_api_client(ctx)


backend.add_command(cmd_create)
backend.add_command(cmd_update)
backend.add_command(cmd_list)
backend.add_command(cmd_delete)
backend.add_command(cmd_add_resource)
backend.add_command(cmd_delete_resource)
backend.add_command(cmd_set_default)
