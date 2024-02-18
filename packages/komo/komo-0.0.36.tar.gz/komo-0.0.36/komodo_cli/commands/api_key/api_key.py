import click

from komodo_cli.commands.api_key.cmd_create import cmd_create
from komodo_cli.commands.api_key.cmd_delete import cmd_delete
from komodo_cli.commands.api_key.cmd_list import cmd_list


@click.group(name="api-key")
@click.pass_context
def api_key(ctx: click.Context):
    pass


api_key.add_command(cmd_create)
api_key.add_command(cmd_list)
api_key.add_command(cmd_delete)
