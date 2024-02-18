import base64
from enum import Enum
from io import BytesIO
from ipaddress import IPv4Address, ip_address, ip_network
from socket import gethostbyaddr
import socket
from uuid import uuid4

from urllib import parse
import os
import shlex
import subprocess
from threading import Thread
from time import sleep
from paramiko import (
    AuthenticationException,
    AutoAddPolicy,
    BadHostKeyException,
    SSHException,
    client as pclient,
)
from questionary import Choice, checkbox, prompt, select
from rich import print

from .parameters import ez_nodes, ez_files, ez_commands
from . import config

defaults = config.get()
if len(defaults.keys()) == 0:
    config.set()
    defaults = config.get()
vm_network = defaults["NETWORK"]["vm_cidr"]
no_proxy = vm_network
# no_proxy = ",".join([str(h) for h in ip_network(vm_network).hosts()])
vm_proxy = defaults["NETWORK"]["proxy"] if "proxy" in defaults["NETWORK"] else ""
if "yum_proxy" in defaults["NETWORK"]:
    no_proxy += f",{parse.urlsplit(defaults['NETWORK']['yum_proxy']).hostname}"
vm_domain = defaults["NETWORK"]["vm_domain"]


class target_names(str, Enum):
    """
    Supported target platforms
    """

    pve = "pve"
    vmw = "vmw"


class target_classes(str, Enum):
    """
    API classes for target platforms
    """

    pve = "ProxmoxAPI"
    vmw = "vim.ServiceInstance"


def fail(message):
    """
    Print the message and gracefully exit
    Params:
        <message>: parameter to print
    """
    print("Operation failed!")
    print(message)
    exit(1)


def select_from_list(
    title: str, list: list, name_generator=lambda n: n, value_generator=lambda v: v
):
    """
    Select an item from a list of objects.
    Params:
        <title>           : Title to show for selection
        <list>            : List of objects (or a simple list(str))
        <name_generator>  : Optional function to get display name for the selection, defaults to the object (if object has __str__ or __name__ method it is returned by default)
        <value_generator> : Optional function to get value for the selection, defaults to the object

    Returns: selected object | <value>
    """
    if not list or len(list) == 0:
        print(f"No {title} found")
        return None
    # generate choices from list with provided name/value field transformers
    choices = [make_choice(name_generator(x), value_generator(x)) for x in list]
    choice = select(title, choices=choices).ask()
    if not choice:
        fail(f"Nothing selected for {title}")
        return None
    # find and return the object from list matching the choice
    return [x for x in list if choice == value_generator(x)][0]


def multiselect_from_list(
    title: str, list: list, name_generator=lambda n: n, value_generator=lambda v: v
):
    """
    Select multiple items from a list of objects.
        Params:
        <title>           : Title to show for selection
        <list>            : List of objects (or a simple list(str))
        <name_generator>  : Optional function to get display name for the selection, defaults to the object (if object has __str__ or __name__ method it is returned by default)
        <value_generator> : Optional function to get value for the selection, defaults to the object

    Returns: list of selected object | <value>

    """
    if not list or len(list) == 0:
        print(f"No {title} found")
        return []
    choices = [make_choice(name_generator(x), value_generator(x)) for x in list]
    choice = checkbox(title, choices=choices).ask()
    if not choice:
        fail(f"Nothing selected for {title}")
    return [x for x in list if value_generator(x) in choice]


def make_choice(name, value=None) -> Choice:
    if not value:
        value = name
    return Choice.build({"name": name, "value": value})


def ask_customisations(**kwargs):
    """
    Ask user for customised values
    Returns <dict>: with selection
    """
    # selecting 3rd available ip as the first vm ip
    recommended_first_ip = str(
        list(ip_network(defaults["NETWORK"]["vm_cidr"]).hosts())[3]
    )
    customisation = [
        {
            "type": "text",
            "name": "vmname",
            "message": "First VM name",
            "default": "ezvm",
        },
        {
            "type": "text",
            "name": "first_vm_ip",
            "message": "First VM IP or 'dhcp'",
            "default": recommended_first_ip,
        },
    ]
    return prompt(customisation, **kwargs)


def get_ssh_key_file():
    return os.path.abspath(os.path.expanduser(defaults["CLOUDINIT"]["ssh_keyfile"]))


def get_customisations():
    """
    Ask user for customisations and verify if they are valid

    """

    vm_ip = ""
    customisations = ask_customisations()
    try:
        vm_ip: str = customisations["first_vm_ip"] or ""

    except KeyError:
        fail("missing information")

    if vm_ip != "dhcp":
        try:
            # check if ip settings are fitting
            if ip_address(vm_ip) not in ip_network(vm_network):
                fail(f"{vm_ip} is not in configured network {vm_network}")
            # confirm enough IP addresses are available in the chosen block for selected node counts
        except ValueError as error:
            print(error)
            fail(f"Invalid IP address or network: {vm_ip} in {vm_network}")

    return customisations


def select_nodes():
    selected = checkbox("Select nodes to deploy", choices=ez_nodes).ask() or []
    nodes = []
    for node in selected:
        nodes.extend([n for n in ez_nodes if n["name"] == node])
    return nodes


def prepare_vm(vm_name: str, vm_ip: str, product_code: str = ""):
    """
    Configure VMs for selected product, taking care of pre-requisites
    Params:
        <vm_name>      : VM name to use in hosts and various system files
        <vm_ip>        : VM IP address to use in hosts and various system files
        <product_code> : Prepare for ezdf | ezua | generic installations

    Returns <bool>     : True in succesful completion, else False
    """

    # files to write
    add_files: dict = ez_files[product_code]

    # update /etc/hosts
    add_files.update(
        {
            "/etc/hosts": f"127.0.0.1 localhost.localdomain localhost\n{vm_ip} {vm_name}.{vm_domain} {vm_name}\n"
        }
    )

    if vm_proxy != "":
        add_files = update_proxy_files(add_files)

    # TODO: Not tested
    if (
        "airgap_registry" in defaults["NETWORK"]
        and defaults["NETWORK"]["airgap_registry"].split("://")[0] == "http"
    ):
        add_files.update({"/etc/docker/daemon.json": get_insecure_registry()})

    if "yum_proxy" in defaults["NETWORK"]:
        repo_content = get_repo_content()
        add_files.update({"/etc/yum.repos.d/nexus.repo": repo_content})

    for file, content in add_files.items():
        # print(f"Writing: {file}")
        if not sftp_write_into_file(
            host=vm_ip,
            username=defaults["CLOUDINIT"]["vm_username"],
            filename=file,
            content=content,
        ):
            return False

    # commands to execute
    commands = list(ez_commands[product_code])

    if "yum_proxy" in defaults["NETWORK"]:
        commands.insert(
            2, "sudo dnf config-manager --set-disabled baseos appstream extras"
        )

    elif vm_proxy != "":
        commands.insert(
            1,
            f"echo proxy={vm_proxy} | sudo tee -a /etc/dnf/dnf.conf > /dev/null",
        )

    for command in commands:
        # print(f"Running: {command}")
        for output in ssh_run_command(vm_ip, command=command):
            print(output)

    return True


def technitium_add_record(hostname: str, ip: str):
    """
    Add DNS records for hostname in Technitium DNS
    Params:
        <hostname>       : hostname to add in DNS
        <ip>             : IP Address to add in DNS
        # <admin_user>     : Technitium admin user
        # <admin_password> : Technitium admin password, defaults to vm_password provided during install/config

    Returns result from API call and prints the error if any
    """
    from tdnss.connection import Connection

    c = Connection(defaults["NETWORK"]["dns_api"])
    res = c.login(
        username=defaults["CLOUDINIT"]["vm_username"],
        password=defaults["CLOUDINIT"]["vm_password"],
    )
    result = None
    if res.status == 1:
        print(f"Cannot add DNS record! Add {ip}: {hostname} to your DNS!")
        print(res.message)
    else:
        result = c._get(
            "zones/records/add",
            {
                "domain": f"{hostname}.{vm_domain}",
                "zone": vm_domain,
                "type": "A",
                "overwrite": "true",
                "ipAddress": ip,
                "ptr": "true",
            },
        )
    c.logout()
    return result


# def get_dns_admin_password():
#     admin_password = os.getenv("EZLAB_DNSPASS")
#     if admin_password is None:
#         admin_password = password("DNS Admin password").ask()

#     return admin_password


def technitium_delete_record(hostname: str, ip: str):
    """
    Delete DNS records for hostname in Technitium DNS
    Params:
        <hostname>       : hostname to delete in DNS
        <ip>             : IP Address to delete in DNS
        # <admin_user>     : Technitium admin user
        # <admin_password> : Technitium admin password, defaults to vm_password provided during install/config

    Returns result from API call and prints the error if any
    """

    from tdnss.connection import Connection

    c = Connection(defaults["NETWORK"]["dns_api"])
    res = c.login(
        username=defaults["CLOUDINIT"]["vm_username"],
        password=defaults["CLOUDINIT"]["vm_password"],
    )
    if res.status == 1:
        print(f"Cannot delete DNS record! Remove {ip}: {hostname} on your DNS!!!")
        print(res.message)
    else:
        res = c._get(
            "zones/records/delete",
            {
                "domain": f"{hostname}.{vm_domain}",
                "zone": vm_domain,
                "type": "A",
                "ipAddress": ip,
                "overwrite": "true",
                "ptr": "true",
            },
        )
    c.logout()
    return res


def ssh_run_command(
    host: str, command: str, username: str = defaults["CLOUDINIT"]["vm_username"], password: str = ""
):
    """
    Run commands over ssh using default credentials
    Params:
        <host>              : hostname/IP to SSH
        <command>           : command to run
        <username>          : (optional) username to authenticate
        <password>          : (optional) password for <username>
    Returns:
        Generator with output. Calling function should process output with a for loop.
        Prints out stderr directly into terminal.

    """
    client = pclient.SSHClient()
    client.set_missing_host_key_policy(AutoAddPolicy)
    command_output = None
    try:
        if password == "":
            client.connect(
                host,
                username=username,
                key_filename=get_ssh_key_file(),
                timeout=60,
            )
        else:
            client.connect(
                host,
                username=username,
                password=password,
                timeout=60,
            )

        _stdin, _stdout, _stderr = client.exec_command(command, get_pty=True)
        command_errors = _stderr.read().decode().strip()
        command_output = _stdout.read().decode().strip()
        if command_errors and command_errors != "":
            print(f"STDERR: {command_errors}")
        if command_output and command_output != "":
            yield command_output
    except Exception as error:
        fail(error)
    finally:
        client.close()

    # return command_output


def wait_for_ssh(host):
    client = pclient.SSHClient()
    client.set_missing_host_key_policy(AutoAddPolicy)
    try:
        while True:
            client.connect(
                host,
                username=defaults["CLOUDINIT"]["vm_username"],
                key_filename=get_ssh_key_file(),
            )
            break
    except (
        BadHostKeyException,
        AuthenticationException,
        SSHException,
        socket.error,
    ):
        print(f"{host} wait for ssh...")
        sleep(5)
    finally:
        client.close()

    return True


def sftp_write_into_file(host, username, filename, content):
    """
    Create files over SFTP using default credentials, putting the content into the file.
    Note:
        The file will be created in temp location as the configured user, but then will be moved to location with sudo
    Params:
        <host>       : hostname/IP to SSH
        <username>   : connect as username
        <filename>   : full path to file in remote system
        <content>    : file content

    """

    client = pclient.SSHClient()
    # client.set_missing_host_key_policy(WarningPolicy)
    client.set_missing_host_key_policy(AutoAddPolicy)
    ftp = None
    try:
        client.connect(host, username=username, key_filename=get_ssh_key_file())
        ftp = client.open_sftp()

        seq = str(uuid4().hex)

        ftp.putfo(BytesIO(content.encode()), f"/tmp/{seq}")
        client.exec_command(
            f"sudo mkdir -p $(dirname {filename}) && sudo mv /tmp/{seq} {filename} && chown root:root {filename} && chmod 644 {filename}"
        )
    except (
        BadHostKeyException,
        AuthenticationException,
        SSHException,
        socket.error,
    ) as e:
        print(e)
        sleep(5)
    finally:
        if ftp:
            ftp.close()
        client.close()

    return True


class ReturningThread(Thread):
    """Create a Thread which returns a value

    Args:
        Thread (Thread): Thread to run and return the result/return value
    """

    def __init__(self, group=None, target=None, name=None, args=(), kwargs={}):
        Thread.__init__(self, group, target, name, args, kwargs)
        self._return = None

    def run(self):
        if self._target is not None:  # type: ignore
            self._return = self._target(*self._args, **self._kwargs)  # type: ignore

    def join(self, *args):
        Thread.join(self, *args)
        return self._return


def start_tasks_delayed(threads: list, delay: int = 0):
    """Start a thread for each task with an optional delay

    Args:
        threads (list<thread>): list of threads to start
        delay (int): delay in seconds
    """
    for t in threads:
        t.start()
        sleep(delay)  # wait few sec to give api time against race condition


def wait_tasks(threads):
    """wait for finish and return result from threads as they come"""
    for t in threads:
        yield t.join()


def toB64(string: str):
    return base64.b64encode(string.encode("ascii")).decode("utf-8")


def execute(cmd: str):
    # sub_env = os.environ.copy()
    # for line in get_proxy_environment().splitlines():
    #     if line.strip() != "":
    #         key, value = line.split("=")
    #         sub_env[key] = value
    proc = subprocess.Popen(
        args=shlex.split(cmd),
        stdout=subprocess.PIPE,
        universal_newlines=True,
        # env=sub_env,
    )

    while proc.stdout:
        output = proc.stdout.readline().strip()
        if output == "" and proc.poll() is not None:
            break
        if output:
            yield f">>> {output}"
    rc = proc.poll()

    # if return_code:
    #     print(f"Error running command: {cmd}")
    #     return "Error"
    # raise subprocess.CalledProcessError(return_code, cmd)


def find_app(name: str):
    """Return executable path for `name` on PATH or in CWD."""
    from shutil import which

    return which(cmd=name, path=f"{os.environ.get('PATH')}:{os.getcwd()}")


def get_proxy_environment():
    # TODO: refactor to return dict and get_proxy_profile() and /etc/environment files can be generated with that
    return f"""
HTTP_PROXY={vm_proxy}
http_proxy={vm_proxy}
HTTPS_PROXY={vm_proxy}
https_proxy={vm_proxy}
NO_PROXY=10.96.0.0/12,10.224.0.0/16,10.43.0.0/16,.external.hpe.local,localhost,.cluster.local,.svc,.default.svc,127.0.0.1,169.254.169.254,.{vm_domain},{no_proxy}
no_proxy=10.96.0.0/12,10.224.0.0/16,10.43.0.0/16,.external.hpe.local,localhost,.cluster.local,.svc,.default.svc,127.0.0.1,169.254.169.254,.{vm_domain},{no_proxy}

"""


def get_proxy_profile():
    return f"""
export HTTP_PROXY={vm_proxy}
export http_proxy={vm_proxy}
export HTTPS_PROXY={vm_proxy}
export https_proxy={vm_proxy}
export NO_PROXY=10.96.0.0/12,10.224.0.0/16,10.43.0.0/16,.external.hpe.local,localhost,.cluster.local,.svc,.default.svc,127.0.0.1,169.254.169.254,.{vm_domain},{no_proxy}
export no_proxy=10.96.0.0/12,10.224.0.0/16,10.43.0.0/16,.external.hpe.local,localhost,.cluster.local,.svc,.default.svc,127.0.0.1,169.254.169.254,.{vm_domain},{no_proxy}

"""


def get_repo_content():
    repo_content = ""
    for repo in ["BaseOS", "AppStream", "PowerTools", "extras"]:
        repo_content += f"""
[nexus-{repo.lower()}]
name = Nexus {repo}
enabled = 1
gpgcheck = 0
baseurl = {defaults["NETWORK"]["yum_proxy"]}/$releasever/{repo}/$basearch/os
ui_repoid_vars = releasever basearch
priority=1
proxy=

"""
    return repo_content


def update_proxy_files(file_content_object: dict):
    file_content_object.update({"/etc/environment": get_proxy_environment()})
    file_content_object.update({"/etc/profile.d/proxy.sh": get_proxy_profile()})
    # file_content_object.update(
    #     {f"/home/{defaults['CLOUDINIT']['vm_username']}/.bashrc": get_proxy_profile()}
    # )
    containerd_proxy = f"""
[Service]
EnvironmentFile=/etc/environment
"""
    # [Service]
    # Environment="HTTP_PROXY={vm_proxy}"
    # Environment="HTTPS_PROXY={vm_proxy}"
    # Environment="NO_PROXY=localhost,127.0.0.1,.{vm_domain},{no_proxy}"
    file_content_object.update(
        {"/etc/systemd/system/containerd.service.d/http-proxy.conf": containerd_proxy}
    )

    return file_content_object


def get_insecure_registry():
    return f"""
{
  "log-driver": "journald",
  "insecure-registries" : [ {defaults['NETWORK']['airgap_registry']} ]
}
"""


def validate_ip(ip_string: str) -> bool:
    try:
        return isinstance(ip_address(ip_string), IPv4Address)
    except:
        return False


def get_fqdn(ip_string: str) -> str:
    fqdn, _, _ = gethostbyaddr(ip_string)
    return fqdn
