import asyncio
import base64
import io
from ipaddress import IPv4Address, ip_address
import os
from queue import Queue
import random
import re
import shlex
import socket
import string
import subprocess
import cryptography
from cryptography.hazmat.primitives import serialization


# from threading import Thread
from time import sleep
from paramiko import (
    AuthenticationException,
    AutoAddPolicy,
    BadHostKeyException,
    RSAKey,
    SSHException,
    SSHClient,
)

from .parameters import *


def nonzero(val):
    return len(val) != 0


def fire_and_forget(f):
    def wrapped(*args, **kwargs):
        return asyncio.get_event_loop().run_in_executor(
            None, f, *args, *[v for v in kwargs.values()]
        )

    return wrapped


def wait_for_ssh(host, username, privatekey):
    client = SSHClient()
    client.set_missing_host_key_policy(AutoAddPolicy)
    try:
        while True:
            client.connect(
                host,
                username=username,
                pkey=RSAKey.from_private_key(io.StringIO(privatekey)),
            )
            break
    except (
        BadHostKeyException,
        AuthenticationException,
        ConnectionResetError,
        SSHException,
        socket.error,
    ):
        print(f"{host} still waiting ssh...")
        sleep(5)
    finally:
        print(f"{host} connected")
        client.close()

    return True


def ssh_run_command(
    host: str,
    username: str,
    keyfile: str,
    command: str,
):
    """
    Run commands over ssh using default credentials
    Params:
        <host>              : hostname/IP to SSH
        <username>          : username to authenticate
        <keyfile>           : private key for <username>
        <command>           : command to run
    Returns:
        Generator with stdout. Calling function should process output with a for loop.
        Prints out stderr directly into terminal.

    """
    client = SSHClient()
    client.set_missing_host_key_policy(AutoAddPolicy)
    command_output = None
    # print(f"Try connection to {host}")
    try:
        client.connect(
            host,
            username=username,
            key_filename=keyfile,
            timeout=60,
        )

        if "hostname -f" not in command:
            yield f"{host} running: {command}"

        _stdin, _stdout, _stderr = client.exec_command(command, get_pty=True)
        command_errors = _stderr.read().decode().strip()
        command_output = _stdout.read().decode().strip()

        if command_errors and command_errors != "":
            yield f"[CMDERR]: {command_errors}"
        if command_output and command_output != "":
            # should return only the command output
            yield command_output

    except Exception as error:
        print("SSH run exception: ", error)

    finally:
        client.close()

    # return command_output


def ssh_content_into_file(
    host: str, username: str, keyfile: str, content: str, filepath: str
):
    random_eof = "".join(random.choices(string.ascii_uppercase + string.digits, k=10))
    command = f"""cat << {random_eof} | sudo tee {filepath}
{content}
{random_eof}
"""
    return ssh_run_command(
        host=host,
        username=username,
        keyfile=keyfile,
        command=command,
    )


def find_app(name: str):
    """Return executable path for `name` on PATH or in CWD."""
    from shutil import which

    return which(cmd=name, path=f"{os.environ.get('PATH')}:{os.getcwd()}")


def execute(cmd: str):
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


def toB64(string: str):
    return base64.b64encode(string.encode("ascii")).decode("utf-8")


def validate_ip(ip_string: str) -> bool:
    try:
        return isinstance(ip_address(ip_string), IPv4Address)
    except:
        return False


def get_fqdn(ip_string: str) -> str:
    fqdn, _, _ = socket.gethostbyaddr(ip_string)
    return fqdn


@fire_and_forget
def prepare_vm(
    hostname: str,
    hostip: str,
    config: dict,
    addhosts: list,
    prepare_for: str,
    queue: Queue,
    dryrun: bool,
):
    """
    Configure VMs for selected product, taking care of pre-requisites
    Params:
        <hostname>      : VM hostname
        <hostip>        : VM IP address (should be reachable)
        <config>        : Dictinary of configuration from app settings
        <addhosts>      : Other hosts to add to /etc/hosts file
        <prepare_for>   : EZUA | EZDF | Generic (from parameters: UA|DF|GENERIC)
        <queue>         : Message queue
        <dryrun>        : Do not execute but report

    Returns <bool>     : True in succesful completion, False otherwise. If dryrun, returns dict of job run
    """

    response = {}
    if dryrun:
        response["task"] = (
            f"Prepare {hostname} ({hostip}) for {prepare_for} {'with hosts: ' + ','.join(addhosts) if len(addhosts) > 0 else 'as single node'}"
        )
        response["settings"] = config

    domain = config["domain"]
    cidr = config["cidr"]
    username = config["username"]
    # password = config["password"]
    keyfile = config["privatekeyfile"]
    # commands to execute, always prepend with generic/common commands, such as enable password auth, disable subscription mgr etc.
    commands = list(SETUP_COMMANDS[GENERIC]) + list(SETUP_COMMANDS[prepare_for])
    after_generic_commands = len(list(SETUP_COMMANDS[GENERIC]))

    # to add to /etc/hosts
    otherhosts = "\n".join(
        [f"{h['ip']} {h['name']}.{domain} {h['name']}" for h in addhosts]
    )

    files = {
        # "/etc/cloud/templates/hosts.redhat.tmpl": f"127.0.0.1 localhost.localdomain localhost\n{hostip} {hostname}.{domain} {hostname}\n"
        "/etc/hosts": f"127.0.0.1 localhost.localdomain localhost\n{hostip} {hostname}.{domain} {hostname}\n{otherhosts}"
    }

    noproxy = (
        f"{hostip},{re.split(':|/', config.get('maprlocalrepo').split('://')[1])[0]}"
        if config.get("maprrepoislocal", False)
        else hostip
    )

    # update env files for proxy
    if config.get("proxy", "").strip() != "":
        environment_file = ""
        proxy_file = ""
        for key, value in get_proxy_vars(config["proxy"]).items():
            val = value.format(vm_domain=domain, vm_network=cidr, no_proxy=noproxy)
            environment_file += f"{key}={val}\n"
            proxy_file += f"export {key}={val}\n"

        files.update({"/etc/environment": environment_file})
        files.update({"/etc/profile.d/proxy.sh": proxy_file})

    # TODO: Not tested
    if (
        config.get("airgap_registry", "").strip() != ""
        and config["airgap_registry"].split("://")[0] == "http"
    ):
        files.update(
            {
                "/etc/docker/daemon.json": get_insecure_registry(
                    config["airgap_registry"]
                )
            }
        )

    repo_content = ""
    if config.get("yumrepo", "").strip() != "":
        repo_content = get_repo_content(config["yumrepo"])
    else:
        print("Using system repositories")

    if config.get("epelrepo", "").strip() != "":
        repo_content += f"""
[local-epel]
name = Local EPEL
enabled = 1
gpgcheck = 0
baseurl = {config.get("epelrepo")}
priority=1
proxy=

"""
    else:
        epel_default = "subscription-manager repos --enable codeready-builder-for-rhel-8-x86_64-rpms; sudo dnf install -y https://dl.fedoraproject.org/pub/epel/epel-release-latest-8.noarch.rpm"
        commands.insert(after_generic_commands, epel_default)

    if repo_content != "": # yum or epel repo given
        files.update({"/etc/yum.repos.d/local.repo": repo_content})

    if dryrun:
        response["files"] = files
    else:
        try:
            for filepath, content in files.items():
                print(f"{hostip} Writing {filepath}")
                for result in ssh_content_into_file(
                    host=hostip,
                    username=username,
                    keyfile=keyfile,
                    content=content,
                    filepath=filepath,
                ):
                    queue.put(f"{hostip} COPY {filepath}, CONTENT:\n{result}")

        except Exception as error:
            print(error)
            return False

    if (
        config.get("yumrepo", "").strip() != ""
        or config.get("epelrepo", "").strip() != ""
    ):
        commands.insert(
            after_generic_commands, "sudo dnf config-manager --set-disabled baseos appstream extras"
        )

    if config.get("proxy", "").strip() != "":
        commands.insert(
            after_generic_commands + 1,
            # f"echo proxy={config['proxy']} | sudo tee -a /etc/dnf/dnf.conf > /dev/null",
            "sudo sed -i '/proxy=/d' /etc/dnf/dnf.conf > /dev/null; echo proxy={proxy_line} | sudo tee -a /etc/dnf/dnf.conf".format(
                proxy_line=(
                    config["proxy"]
                    if config["proxy"][-1] == "/"
                    else config["proxy"] + "/"
                )
            ),
        )

    # rename host
    commands.insert(after_generic_commands + 2, f"sudo hostnamectl set-hostname {hostname}.{domain}")

    if dryrun:
        response["commands"] = commands

    else:
        try:
            for command in commands:
                print(f"{hostip} Running: {command}")
                for output in ssh_run_command(
                    host=hostip, username=username, keyfile=keyfile, command=command
                ):
                    queue.put(f"{hostip} SSH: {output}")
        except Exception as error:
            print(error)
            return False

    queue.put(TASK_FINISHED)

    return response if dryrun else True


def get_proxy_vars(proxy):
    if proxy[-1] != "/":
        proxy += "/"
    return {
        "HTTP_PROXY": proxy,
        "http_proxy": proxy,
        "HTTPS_PROXY": proxy,
        "https_proxy": proxy,
        "NO_PROXY": NO_PROXY,
        "no_proxy": NO_PROXY,
    }


def get_insecure_registry(registry):
    return f"""
{
  "log-driver": "journald",
  "insecure-registries" : [ {registry} ]
}
"""


def get_repo_content(repo_url: str):
    repo_content = ""
    for repo in ["BaseOS", "AppStream", "PowerTools", "extras"]:
        repo_content += fr"""
[local-{repo.lower()}]
name = Local {repo}
enabled = 1
gpgcheck = 0
baseurl = {repo_url.rstrip('/')}/\$releasever/{repo}/\$basearch/os
ui_repoid_vars = releasever basearch
priority=1
proxy=
"""
    return repo_content


def is_file(file):
    return os.path.isfile(os.path.abspath(file))


def get_privatekey_from_string(key):
    try:
        # try OpenSSL format (RSA?)
        return serialization.load_pem_private_key(key.encode(), password=None)
    except ValueError:
        # try OpenSSH format
        try:
            return serialization.load_ssh_private_key(key.encode(), password=None)
        except (ValueError, TypeError, cryptography.exceptions.UnsupportedAlgorithm):
            return None
    except Exception as error:
        print(error)
        return None


def get_opensshpub(privatekey):
    try:
        return (
            privatekey.public_key()
            .public_bytes(
                encoding=serialization.Encoding.OpenSSH,
                format=serialization.PublicFormat.OpenSSH,
            )
            .decode()
        )
    except Exception as error:
        print(error)
        return None


def debug_queue_to_here(queue, message):
    print(message)
    queue.put(TASK_FINISHED)
    return True
