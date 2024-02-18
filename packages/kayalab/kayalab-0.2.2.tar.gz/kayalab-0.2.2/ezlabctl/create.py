from ipaddress import ip_address, ip_network
from typing import Annotated
from .connect import (
    connect_to_target,
)
from .common import (
    get_customisations,
    select_nodes,
    target_names,
    fail,
    target_classes,
)
from . import config

import typer

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

    # app settings
    defaults = config.get()
    # What to deploy
    nodes = select_nodes()

    requested_node_count = sum([int(x["count"]) for x in nodes])
    if len(nodes) < 1:
        fail("No nodes selected")
    else:
        print(f"{requested_node_count} VMs will be created")

    # Check resource availability
    # [TODO] Target specific controls required here, such as if there is enough capacity on selected volume, or enough cores in selected cluster etc.

    # Customisation
    customisations = get_customisations()
    if customisations["first_vm_ip"] != "dhcp":
        if (
            ip_address(customisations["first_vm_ip"]) + requested_node_count
            not in ip_network(defaults["NETWORK"]["vm_cidr"]).hosts()
        ):  # type: ignore
            fail(
                f"Not enough IP available in selected network.\n Available IPs: {ip_network(defaults['NETWORK']['vm_cidr']).hosts()}"
            )

    new_vms = []
    if connection is not None:
        connection_type = connection.__class__.__name__
        if connection_type == target_classes.pve.value:
            new_vms = pve.clone_vms(
                proxmox=connection,  # type: ignore
                customisations=customisations,
                nodes=nodes,
            )
        elif connection_type == target_classes.vmw.value:
            fail("Vmware cloudinit customisation is not working at this release, check if there is a newer release!")
            new_vms = vmw.clone_vms(
                connection=connection,  # type: ignore
                customisations=customisations,
                nodes=nodes,
            )
        else:
            fail("Unknown connection type")
    try:
        for vm, product in new_vms:
            print(f"{vm} is ready for {product}")
    except TypeError:
        fail("Cannot complete vm creation")


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
    if connection is not None:
        connection_type = connection.__class__.__name__
        if connection_type == target_classes.pve.value:
            if "root" not in username:
                fail("You must connect with root to create template.")
            vms = pve.create_template(connection)  # type: ignore
        elif connection_type == target_classes.vmw.value:
            vms = vmw.create_template(connection)  # type: ignore
        else:
            fail("Unknown connection type")

    else:
        fail(f"Cannot open connection to {target}")

    for vm in vms:
        print(f"{vm} is ready")
