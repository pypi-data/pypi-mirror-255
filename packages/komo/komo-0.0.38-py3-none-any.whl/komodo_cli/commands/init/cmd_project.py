import os
import sys

import click
import git
import jinja2

import komodo_cli.printing as printing
from komodo_cli.utils import APIClient, get_komodo_project_file

BACKEND_CONFIG_TEMPLATE_DIR = os.path.join(
    os.path.dirname(os.path.realpath(__file__)), "../..", "templates"
)


@click.command("project")
@click.pass_context  # TODO: do we need ctx?
# what happens if the cli.py fails to read these configs?
def cmd_project(ctx: click.Context):
    """Initialize a Komodo project in the current directory."""
    project_config_filepath = get_komodo_project_file()

    if os.path.isfile(project_config_filepath):
        printing.error(f"Project config {project_config_filepath} already exists")
        exit(1)

    printing.header(
        f"Initializing Komo project config in {project_config_filepath}",
        bold=True,
    )

    api_client: APIClient = ctx.obj["api_client"]
    backend_schemas = api_client.list_backends()

    template_loader = jinja2.FileSystemLoader(
        searchpath=os.path.join(BACKEND_CONFIG_TEMPLATE_DIR)
    )
    template_env = jinja2.Environment(loader=template_loader)
    project_template = template_env.get_template("project.jinja")

    backend_templates = {}
    for backend_schema in backend_schemas:
        backend_template = template_env.get_template(
            f"{backend_schema.type}.jinja",
        )
        backend_templates[backend_schema.name] = backend_template.render()

    project_config_output = project_template.render(
        backends=backend_templates,
        first_backend=backend_schemas[0].name,
    )

    with open(project_config_filepath, "w") as f:
        f.write(project_config_output)

    printing.success(
        f"Komodo project successfully initialized at project root.\nUpdate the .komo/project.yaml file to your needs.",
        bold=True,
    )
