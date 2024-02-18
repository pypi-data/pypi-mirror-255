from typing import Annotated, List
from urllib.parse import quote
from paramiko import AutoAddPolicy, SSHClient
from paramiko_expect import SSHClientInteraction

import typer

from . import config

from .common import (
    fail,
    sftp_write_into_file,
    ssh_run_command,
)

app = typer.Typer(add_completion=True, no_args_is_help=True)

defaults = config.get()


@app.command(
    help="Create Data Fabric cluster with provided hosts",
    short_help="Create DF cluster",
    no_args_is_help=True,
)
def cluster(
    hosts: List[str],
    name: Annotated[str, typer.Option("--name", "-n", help="cluster name")] = "ezlab",
    repouser: Annotated[str, typer.Option("--username", "-u", help="repo user")] = "",
    repotoken: Annotated[
        str,
        typer.Option(
            "--token",
            "-t",
            hide_input=True,
            help="password or token to authenticate for the repo",
        ),
    ] = "",
):
    hostnames = []
    for host in hosts:
        for result in ssh_run_command(
            host=f"{host}.{defaults['NETWORK']['vm_domain']}", command="hostname -f"
        ):
            hostnames.append(result)

    first_host = hosts[0]

    print(first_host)

    ez_repo = (
        defaults["NETWORK"]["mapr_repo"]
        if "mapr_repo" in defaults["NETWORK"]
        else f"https://{repouser}:{repotoken}@package.ezmeral.hpe.com/releases"
    )

    sftp_write_into_file(
        host=first_host,
        username=defaults["CLOUDINIT"]["vm_username"],
        filename="/tmp/mapr.stanza",
        content=get_mapr_stanza(
            hosts=hostnames,
            username=defaults["CLOUDINIT"]["vm_username"],
            password=defaults["CLOUDINIT"]["vm_password"],
            disks=["/dev/sdb"],
            cluster_name=name,
        ),
    )
    print(f"stanza copied to {first_host}")

    # for wget string
    user_str = quote(f"--user={repouser}" if repouser else "")
    token_str = f"--password={repotoken}" if repotoken else ""

    commands = [
        f"[ -f /tmp/mapr-setup.sh ] || wget -q {user_str} {token_str} {ez_repo}/installer/redhat/mapr-setup.sh -P /tmp",
        "chmod +x /tmp/mapr-setup.sh",
        f"curl -s -k https://127.0.0.1:9443/ > /dev/null || sudo /tmp/mapr-setup.sh -y -r {ez_repo}",
        "[ -f /opt/mapr/installer/bin/mapr-installer-cli ] && echo Starting installation, this may take ~30 minutes... && sleep 30",
        "echo Installer at: https://$(hostname -f):9443/",
        "echo -n 'Starting at: '; date",
        # "[ -f /opt/mapr/installer/bin/mapr-installer-cli ] && echo Monitor progres on Installer web, do not use navigation links!",
        "echo y | sudo /opt/mapr/installer/bin/mapr-installer-cli install -nvp -t /tmp/mapr.stanza -u mapr:mapr@127.0.0.1:9443",
        "echo -n 'Finished at: '; date",
    ]

    print(f"starting installer on {first_host}")
    for command in commands:
        for result in ssh_run_command(host=first_host, command=command):
            print(result)

    print(
        f"echo Installation complete. Install license file and configure cluster on https://{first_host}:8443/"
    )


@app.command(
    help="Configure DF client for specified cluster (CLDB)",
    short_help="Create a DF client",
    no_args_is_help=True,
)
def dfclient(
    server: Annotated[str, typer.Option("--server", "-s")],
    client: Annotated[str, typer.Option("--client", "-c")],
    user: Annotated[str, typer.Option("--username", "-u", help="repo user")] = "",
    token: Annotated[
        str,
        typer.Option(
            "--token",
            "-t",
            hide_input=True,
        ),
    ] = "",
):
    ez_repo = (
        defaults["NETWORK"]["mapr_repo"]
        if "mapr_repo" in defaults["NETWORK"]
        else f"https://{user}:{token}@package.ezmeral.hpe.com/releases"
    )

    repo_content = """
[ezmeral]
name = Ezmeral Packages
enabled = 1
gpgcheck = 0
baseurl = {ez_repo}/v7.5.0/redhat
priority=1
proxy=

[ezmeral-eep]
name = Ezmeral EEP Packages
enabled = 1
gpgcheck = 0
baseurl = {ez_repo}/MEP/MEP-9.2.0/redhat
priority=1
proxy=

""".format(
        ez_repo=ez_repo
    )

    sftp_write_into_file(
        host=client,
        username=defaults["CLOUDINIT"]["vm_username"],
        filename="/etc/yum.repos.d/mapr.repo",
        content=repo_content,
    )

    commands = [
        "sudo dnf update -y -q",
        "sudo useradd -md /home/mapr -u 5000 -U -s /bin/bash mapr",
        "echo mapr:mapr | sudo chpasswd",
        "sudo dnf install -y -q mapr-client java-11-openjdk",
    ]
    files = [
        "/opt/mapr/conf/ssl_truststore",
        "/opt/mapr/conf/ssl_truststore.p12",
        "/opt/mapr/conf/ssl_truststore.pem",
        "/opt/mapr/conf/maprtrustcreds.conf",
        "/opt/mapr/conf/maprtrustcreds.jceks",
        "/opt/mapr/conf/ssl_keystore-signed.pem",
    ]
    for file in files:
        commands.append(
            f"sudo curl -s --insecure --user mapr:mapr sftp://{server}{file} --output {file}"
        )

    # Run these last
    commands.append(
        f"sudo /opt/mapr/server/configure.sh -c -C {server} -N ezdf -secure"
    )
    commands.append("echo mapr | sudo -u mapr maprlogin password")

    for command in commands:
        print(f"Runnning {command}")
        for result in ssh_run_command(host=client, command=command):
            print(result)


@app.command(
    help="Create cross-cluster connectivity between local and remote",
    short_help="Configure cross-cluster",
    no_args_is_help=True,
)
def cross(
    local: Annotated[str, typer.Option("--local", "-l")],
    remote: Annotated[str, typer.Option("--remote", "-r")],
    luser: Annotated[
        str, typer.Option("--luser", help="local cluster admin user")
    ] = "mapr",
    ruser: Annotated[
        str, typer.Option("--ruser", help="local cluster admin user")
    ] = "mapr",
    password: Annotated[
        str, typer.Option("--password", "-p", help="Admin user (mapr) password")
    ] = "mapr",
):
    print(f"Create cross cluster connectivity between {local} and {remote}")

    local_truststore_password = ""
    remote_truststore_password = ""
    for out in ssh_run_command(
        local,
        "grep ssl.server.truststore /opt/mapr/conf/store-passwords.txt | cut -d'=' -f2",
        username=luser,
        password=password,
    ):
        local_truststore_password = out

    for out in ssh_run_command(
        remote,
        "grep ssl.server.truststore /opt/mapr/conf/store-passwords.txt | cut -d'=' -f2",
        username=ruser,
        password=password,
    ):
        remote_truststore_password = out

    if local_truststore_password and remote_truststore_password:
        print(f"using local truststore password: {local_truststore_password}")
        print(f"using remote truststore password: {remote_truststore_password}")
    else:
        fail("failed to get truststore passwords")

    cross_cluster_setup = f"rm -rf /tmp/mapr-xcs; /opt/mapr/server/configure-crosscluster.sh create all \
    -localcrossclusteruser {luser} -remotecrossclusteruser {ruser} \
    -localtruststorepassword {local_truststore_password} -remotetruststorepassword {remote_truststore_password} \
    -remoteip {remote} -localuser {luser} -remoteuser {ruser} "

    # for out in ssh_run_command(host=local, command=cross_cluster_setup, username=luser, password=password):
    #     print(out)
    client = SSHClient()
    client.set_missing_host_key_policy(AutoAddPolicy)

    client.connect(hostname=local, username=luser, password=password)

    interact = SSHClientInteraction(client, timeout=300, display=True)
    prompt = f".*[{luser}@{local} ~]$.*"
    interact.expect(prompt)
    # print(interact.current_output_clean)

    interact.send(cross_cluster_setup)

    interact.expect("Enter password for mapr user.*")
    interact.send(password)
    interact.expect("Enter password for mapr user.*")
    interact.send(password)

    interact.expect(prompt)
    interact.send("exit")
    interact.expect()


def get_mapr_stanza(
    hosts: list, username: str, password: str, disks: list, cluster_name: str
):
    """
    Return stanza for Data Fabric installation
    """
    hosts_yaml = ""
    for host in hosts:
        hosts_yaml += f"  -   {host}\n"

    disks_yaml = ""
    for disk in disks:
        disks_yaml += f"  -   {disk}\n"

    return f"""
environment:
  mapr_core_version: 7.5.0
config:
  hosts:
{hosts_yaml}
  ssh_id: {username}
  ssh_password: {password}
  enable_nfs: False
  db_admin_user: root
  db_admin_password: mapr123
  log_admin_password: mapr123
  metrics_ui_admin_password: mapr123
  enable_encryption_at_rest: True
  license_type: M7
  mep_version: 9.2.0
  disks:
{disks_yaml}
  disk_format: true
  disk_stripe: 1
  cluster_name: {cluster_name}
  services:
    # template-05-converged:
    template-30-maprdb3:
    mapr-hivemetastore:
      database:
        name: hive
        user: hive
        password: mapr123
    mapr-grafana:
      enabled: True
    mapr-opentsdb:
      enabled: True
    mapr-collectd:
    mapr-fluentd:
    mapr-kibana:
      enabled: False
    mapr-elasticsearch:
      enabled: Flase
    mapr-data-access-gateway:
    mapr-mastgateway:

"""
