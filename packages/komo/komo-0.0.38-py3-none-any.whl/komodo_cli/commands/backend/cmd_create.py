import os
import time

import click

import komodo_cli.printing as printing
from komodo_cli.backends.backend_factory import BackendFactory
from komodo_cli.types import BackendStatus
from komodo_cli.utils import APIClient, handle_errors


@click.command("create")
@click.option(
    "--name",
    "-n",
    type=str,
    default=None,
    help="Name of the backend to create",
)
@click.option(
    "--backend-type",
    "-t",
    type=click.Choice(list(BackendFactory.backend_types.keys())),
    help="Type of backend to create.",
    required=True,
)
@click.pass_context
@handle_errors
def cmd_create(
    ctx: click.Context,
    name: str,
    backend_type: str,
):
    api_client: APIClient = ctx.obj["api_client"]

    backend_cls = BackendFactory.backend_types[backend_type]
    backend_cls.assert_ready_for_use()

    config_params = backend_cls.config_params
    config = {}
    for param in config_params:
        while True:
            prompt = f"{param.name} ({param.description})"
            value = click.prompt(prompt, default=param.default, type=param.dtype)

            if param.read_from_file:
                value = os.path.expanduser(value)
                if not os.path.isfile(value):
                    printing.error(f"{value} is not a valid file")
                    continue

                with open(value, "r") as f:
                    value = f.read()

            break

        config[param.name] = value

    resource_config_params = backend_cls.resource_config_params
    # also prompt user to set up resources
    if len(resource_config_params) > 0:
        printing.header("Now let's set up your first resource!")

    resource_configs = {}
    while True:
        if len(resource_config_params) == 0:
            break

        resource_config = {}

        for param in resource_config_params:
            while True:
                prompt = f"{param.name} ({param.description})"
                value = click.prompt(prompt, default=param.default, type=param.dtype)

                if param.read_from_file:
                    value = os.path.expanduser(value)
                    if not os.path.isfile(value):
                        printing.error(f"{value} is not a valid file")
                        continue

                    with open(value, "r") as f:
                        value = f.read()

                break

            resource_config[param.name] = value

        printing.header(
            "Now pick a name for this resource. For example, if you selected an instance type with 8 V100 GPUs, you could name it v100x8"
        )
        while True:
            resource_name = click.prompt("name", type=str)
            if resource_name in resource_configs:
                printing.error(
                    "You have already used this name, please pick another name"
                )
                continue

            break

        resource_configs[resource_name] = resource_config

        printing.header(
            "Would you like to set up another resource? If not, you can always add more later with the 'komo backend add-resource' command"
        )
        add_another = click.prompt("y/n", type=bool)

        if not add_another:
            break

    config = backend_cls.setup(config, api_client)

    api_client.create_backend(
        name,
        backend_type,
        config,
        resource_configs,
    )

    printing.info(
        "Waiting for backend to finish initializing. This could take several minutes."
    )
    while True:
        backend = api_client.get_backend(name)
        if backend.status == BackendStatus.VALID:
            break

        if backend.status == BackendStatus.ERROR:
            printing.error(
                f"Backend '{name}' failed to initialize with the following error:\n{backend.status_message}"
            )
            exit(1)

        time.sleep(5)

    printing.success(f"Backend '{name}' succesfully created")
