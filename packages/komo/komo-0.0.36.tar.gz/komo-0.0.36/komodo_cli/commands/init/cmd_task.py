import os

import click
import git
import jinja2

import komodo_cli.printing as printing
from komodo_cli.utils import APIClient, get_komodo_project_dir

TASK_TEMPLATE_DIR = os.path.join(
    os.path.dirname(os.path.realpath(__file__)), "../..", "templates"
)


@click.command("task")
@click.option(
    "--name",
    "-n",
    type=str,
    help="Name of task to create.",
)
@click.pass_context
def cmd_task(ctx: click.Context, name: str):
    project_dir = get_komodo_project_dir()

    task_config_filepath = os.path.join(project_dir, f"{name}.yaml")
    if os.path.isfile(task_config_filepath):
        printing.error(
            f"Project config already exists in this repository",
            bold=True,
        )
        exit(1)
    printing.info(
        f"Initializing Komo task config in {task_config_filepath}",
        bold=True,
    )

    api_client: APIClient = ctx.obj["api_client"]
    backend_schemas = api_client.list_backends()

    template_loader = jinja2.FileSystemLoader(
        searchpath=os.path.join(TASK_TEMPLATE_DIR)
    )
    template_env = jinja2.Environment(loader=template_loader)
    project_template = template_env.get_template("task.jinja")

    backends_str = " | ".join([b.name for b in backend_schemas])

    task_config_output = project_template.render(backends=backends_str)
    os.makedirs(os.path.dirname(task_config_filepath), exist_ok=True)
    with open(task_config_filepath, "w") as f:
        f.write(task_config_output)
