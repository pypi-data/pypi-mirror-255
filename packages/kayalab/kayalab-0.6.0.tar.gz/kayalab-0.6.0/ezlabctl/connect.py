from .common import fail, target_classes, target_names
from . import pve
from . import vmw


def connect_to_target(target, host, username, password):
    """Create connection to target API

    Args:
        target (enum): pve or vmw
        host (string): API host/IP to connect
        username (str): API user, required permissions ...
        password (str): API user password

    Returns:
        class: API connection class
    """
    connection = None
    if target == target_names.pve:
        connection = pve.get_connection(host, username, password)

    elif target == target_names.vmw:
        connection = vmw.get_connection(host, username, password)

    else:
        fail("Unknown target")

    return connection


def select_vms(connection):
    """Returns all VMs from connection

    Args:
        connection (class<API>): connection class returned by the API connection

    Returns:
        list<class>: List of all VMs returned by API call
    """
    connection_type = connection.__class__.__name__
    if connection_type == target_classes.pve.value:
        return pve.select_vms(connection)
    elif connection_type == target_classes.vmw.value:
        return vmw.get_all_vms(connection)
    else:
        fail("Unknown connection type")
    return None


# def get_vm_ip(connection, vm):
#     connection_type = connection.__class__.__name__
#     if connection_type == target_classes.pve.value:
#         return pve.get_vm_ip(connection, vm)
#     elif connection_type == target_classes.vmw.value:
#         fail("Vmware not implemented yet")
#     else:
#         fail("Unknown connection type")
#     return None
