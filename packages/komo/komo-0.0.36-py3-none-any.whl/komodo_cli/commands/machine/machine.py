import click

from komodo_cli.commands.machine.cmd_create import cmd_create
from komodo_cli.commands.machine.cmd_list import cmd_list
from komodo_cli.commands.machine.cmd_shell import cmd_shell
from komodo_cli.commands.machine.cmd_terminate import cmd_terminate
from komodo_cli.commands.machine.cmd_vscode import cmd_vscode
from komodo_cli.utils import update_context_with_api_client


@click.group()
@click.pass_context
def machine(ctx: click.Context):
    update_context_with_api_client(ctx)


machine.add_command(cmd_create)
machine.add_command(cmd_list)
machine.add_command(cmd_terminate)
machine.add_command(cmd_shell)
machine.add_command(cmd_vscode)
