import click

from komodo_cli.commands.init.cmd_project import cmd_project
from komodo_cli.commands.init.cmd_task import cmd_task
from komodo_cli.utils import update_context_with_api_client


@click.group()
@click.pass_context
def init(ctx: click.Context):
    update_context_with_api_client(ctx)


init.add_command(cmd_project)
init.add_command(cmd_task)
