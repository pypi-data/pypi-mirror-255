import time

import click

import komodo_cli.printing as printing
from komodo_cli.backends.backend_factory import BackendFactory
from komodo_cli.types import BackendStatus
from komodo_cli.utils import APIClient, handle_errors


@click.command("add-resource")
@click.option(
    "--backend",
    "-b",
    type=str,
    required=True,
    help="Name of the backend to create the resource under",
)
@click.option(
    "--name",
    "-n",
    type=str,
    required=True,
    help="Name of the resource to create",
)
@click.pass_context
@handle_errors
def cmd_add_resource(
    ctx: click.Context,
    backend: str,
    name: str,
):
    api_client: APIClient = ctx.obj["api_client"]

    backend_name = backend
    backend = api_client.get_backend(backend_name)
    backend_cls = BackendFactory.backend_types[backend.type]

    resource_config_params = backend_cls.resource_config_params
    resource_config = {}
    for param in resource_config_params:
        prompt = f"{param.name} ({param.description})"
        value = click.prompt(prompt, default=param.default, type=param.dtype)
        if value == "":
            value = None
        resource_config[param.name] = value

    api_client.create_backend_resource(
        backend_name,
        name,
        resource_config,
    )

    printing.info(
        "Waiting for backend to finish updating. This could take several minutes."
    )
    while True:
        backend = api_client.get_backend(backend_name)
        if backend.status == BackendStatus.VALID:
            break

        if backend.status == BackendStatus.ERROR:
            printing.error(
                f"Backend '{backend_name}' failed to update with the following error:\n{backend.status_message}"
            )
            exit(1)

        time.sleep(5)

    printing.success(
        f"Resource '{name}' succesfully created for backend '{backend_name}'"
    )
