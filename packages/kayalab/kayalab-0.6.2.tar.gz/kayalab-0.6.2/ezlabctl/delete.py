from typing import Annotated
import typer
from .connect import connect_to_target

from .common import fail, target_classes, target_names

from . import pve
from . import vmw

app = typer.Typer(add_completion=True, no_args_is_help=True)


@app.command()
def vm(
    target: Annotated[target_names, typer.Option("--target", "-t", prompt=True)],
    host: Annotated[
        str, typer.Option("--host", "-h", envvar="EZLAB_HOST", prompt=True)
    ],
    username: Annotated[
        str, typer.Option("--username", "-u", envvar="EZLAB_USER", prompt=True)
    ],
    password: Annotated[
        str,
        typer.Option(
            "--password", "-p", prompt=True, hide_input=True, envvar="EZLAB_PASSWORD"
        ),
    ],
):
    connection = connect_to_target(target, host, username, password)

    vms = []
    connection_type = connection.__class__.__name__
    if connection_type == target_classes.pve.value:
        vms = pve.delete_vms(connection)  # type: ignore
    elif connection_type == target_classes.vmw.value:
        vms = vmw.delete_vms(connection)  # type: ignore
    else:
        fail("Unknown connection type")

    if vms:
        for vm in vms:
            print(f"{vm} is deleted.")


@app.command()
def template(
    target: Annotated[target_names, typer.Option("--target", "-t", prompt=True)],
    host: Annotated[
        str, typer.Option("--host", "-h", envvar="EZLAB_HOST", prompt=True)
    ],
    username: Annotated[
        str, typer.Option("--username", "-u", envvar="EZLAB_USER", prompt=True)
    ],
    password: Annotated[
        str,
        typer.Option(
            "--password", "-p", prompt=True, hide_input=True, envvar="EZLAB_PASSWORD"
        ),
    ],
):
    connection = connect_to_target(target, host, username, password)

    vms = []
    connection_type = connection.__class__.__name__
    if connection_type == target_classes.pve.value:
        vms = pve.delete_templates(connection)  # type: ignore
    elif connection_type == target_classes.vmw.value:
        vms = vmw.delete_templates(connection)  # type: ignore
    else:
        fail("Unknown connection type")

    for vm in vms:
        print(f"{vm} is deleted.")
