import click

import komodo_cli.printing as printing
from komodo_cli.backends.backend_factory import Backend, BackendFactory
from komodo_cli.types import JobStatus
from komodo_cli.utils import APIClient, handle_errors


@click.command("delete")
@click.option(
    "--backend",
    "-b",
    type=str,
    default=None,
    help="Name of the backend to delete",
)
@click.option(
    "--force",
    "-f",
    type=bool,
    is_flag=True,
    help="Delete the backend even if there are jobs/machines that are still running or unreacheable (those will be deleted, but not cancelled)",
)
@click.pass_context
@handle_errors
def cmd_delete(
    ctx: click.Context,
    backend: str,
    force: bool,
):
    backend_name = backend
    api_client: APIClient = ctx.obj["api_client"]

    printing.warning(
        "Deleting a backend will delete all jobs and machines associated with this backend. Are you sure you want to continue?",
        nl=False,
    )
    confirmed = click.confirm("")
    if not confirmed:
        return

    backend_schema = api_client.get_backend(backend_name)

    jobs = api_client.list_jobs()
    jobs = [j for j in jobs if j.backend_name == backend_name]
    machines = api_client.list_machines()
    machines = [m for m in machines if m.backend_name == backend_name]

    api_client.delete_backend(backend_name, force)

    # if we've gotten to this point, then all the jobs/machines associated with
    # this backend have been deleted
    # now let's cancel the running ones (only applies for local jobs, since server handles the rest)
    backend: Backend = BackendFactory.get_backend(backend_schema, api_client)
    for job in jobs:
        if job.status in [JobStatus.RUNNING, JobStatus.PENDING]:
            backend.cancel(job.backend_job_id)
    for machine in machines:
        if machine.status in [JobStatus.RUNNING, JobStatus.PENDING]:
            backend.cancel(machine.backend_job_id)

    printing.success(f"Backend '{backend_name}' deleting")
