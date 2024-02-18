import textwrap

import click
import yaml
from tabulate import tabulate

import komodo_cli.printing as printing
from komodo_cli.utils import APIClient, handle_errors


@click.command("list")
@click.option(
    "--configs", "-c", is_flag=True, help="Display the config for each backend"
)
@click.pass_context
@handle_errors
def cmd_list(
    ctx: click.Context,
    configs: bool,
):
    api_client: APIClient = ctx.obj["api_client"]

    backends = api_client.list_backends()

    backends_to_print = []
    for backend in backends:
        if len(backend.config) == 0:
            config_str = ""
        else:
            config_strs = []
            for key, value in backend.config.items():
                config_strs.append(f"{key}: {value}")

            config_str = "\n".join(config_strs)
            config_str = "\n".join(
                textwrap.wrap(
                    config_str,
                    80,
                    break_on_hyphens=False,
                    replace_whitespace=False,
                    drop_whitespace=False,
                )
            )

        if len(backend.resources) == 0:
            resources = ""
        else:
            resources = "\n".join(
                [yaml.dump({r.name: r.config}) for r in backend.resources]
            )
        print_info = [
            backend.name,
            backend.type,
            config_str,
            resources,
            backend.status.name,
            backend.status_message,
        ]
        backends_to_print.append(print_info)

    if configs:
        headers = ["Name", "Type", "Config", "Resources", "Status", "Status Message"]
        maxcolwidths = [None, None, None, None, None, None]
    else:
        headers = ["Name", "Type", "Resources", "Status", "Status Message"]
        maxcolwidths = [None, None, None, None, None]
        backends_to_print = [row[0:2] + row[3:] for row in backends_to_print]

    if len(backends_to_print) == 0:
        maxcolwidths = None  # weird tabulate bug

    printing.header("Backends:")
    # TODO: use a better library than tabulate to make this pretty
    printing.info(
        tabulate(
            backends_to_print,
            headers=headers,
            maxcolwidths=maxcolwidths,
            tablefmt="simple_grid",
        ),
    )
