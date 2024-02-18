from .utils import *
from .parameters import *
from paramiko_expect import SSHClientInteraction


@fire_and_forget
def cluster_install(
    hosts: list[str],
    config: dict,
    queue: Queue,
    name: str = "ezlab",
    disks: str = "/dev/sdz",
    dryrun: bool = True,
):
    hostnames = []

    response = {}
    if dryrun:
        response["task"] = (
            f"Create Data Fabric cluster {name} on {','.join(hosts)} using disk(s) {disks}"
        )
        response["settings"] = config

    # lazy way to catch exceptions
    try:
        username = config.get("username")
        # used for connecting to nodes from this app
        keyfile = config.get("privatekeyfile")
        # used for connection between cluster nodes
        password = config.get("password")

        # get fqdn for each host
        if dryrun:

            def getsshcmd(host):
                return f"ssh {config.get('username')}@{host} 'hostname -f'"

            response["commands"] = [getsshcmd(host) for host in hosts]

        else:
            for host in hosts:
                print(f"Getting fqdn for {host}")
                for result in ssh_run_command(
                    host=host.strip(),
                    username=username,
                    keyfile=keyfile,
                    command="hostname -f",
                ):
                    hostnames.append(result)

        # addhosts = ([h for h in hosts if h["name"] != host["name"]],)
        # # to add to /etc/hosts
        # otherhosts = [
        #     f"{h['ip']} {h['name']}.{domain} {h['name']}" for h in addhosts
        # ].join("\n")

        commands: list[str] = INSTALL_COMMANDS[DF]

        if config.get("maprrepoislocal", False):
            # using local repository for mapr packages
            ezrepo: str = config.get("maprlocalrepo", "").rstrip("/")
            repouser = config["maprlocalrepousername"]
            repopass = config["maprlocalrepopassword"]

            wgetauthstring = (
                f"--user={repouser} --password={repopass}"
                if config.get("maprlocalrepoauth", False)
                else ""
            )

            proto, path, *_ = ezrepo.split("://")
            repourl = (
                f"{proto}://{repouser}:{repopass}@{path}"
                if config.get("maprlocalrepoauth", False)
                else ezrepo
            )

            commands.insert(
                0,
                f"[ -f /tmp/mapr-setup.sh ] || wget -q {wgetauthstring} {ezrepo}/installer/redhat/mapr-setup.sh -P /tmp; chmod +x /tmp/mapr-setup.sh",
            )

            commands.insert(
                1,
                f"curl -s -k https://127.0.0.1:9443/ > /dev/null || sudo /tmp/mapr-setup.sh -y -r {repourl}/",
            )

        else:
            # using HPE repository
            ezrepo = f"https://package.ezmeral.hpe.com/releases"
            repouser = config["maprrepouser"]
            repotoken = config["maprrepotoken"]

            commands.insert(
                0,
                f"[ -f /tmp/mapr-setup.sh ] || wget -q --user={repouser} --password= {repotoken} {ezrepo}/installer/redhat/mapr-setup.sh -P /tmp; chmod +x /tmp/mapr-setup.sh",
            )

            commands.insert(
                1,
                f"curl -s -k https://127.0.0.1:9443/ > /dev/null || sudo /tmp/mapr-setup.sh -y --repo-user {repouser} --repo-token {repotoken}",
            )

        first_host = hosts[0].strip()

        # Create and upload stanza file
        stanza = get_mapr_stanza(
            hosts=hostnames,
            username=username,
            password=password,
            disks=disks.split(","),
            cluster_name=name,
        )

        if dryrun:
            response["files"] = {"/tmp/mapr.stanza": stanza}

        else:
            print(f"{first_host} Writing /tmp/mapr.stanza")
            for result in ssh_content_into_file(
                host=first_host,
                username=username,
                keyfile=keyfile,
                content=stanza,
                filepath="/tmp/mapr.stanza",
            ):
                queue.put(f"{first_host}: {result}")

            queue.put(f"stanza copied to {first_host}")

            queue.put(f"starting installer on {first_host}")

        if dryrun:
            response["commands"].extend(commands)

        else:
            for command in commands:
                print(f"{first_host} Running: {command}")
                for result in ssh_run_command(
                    host=first_host,
                    username=username,
                    keyfile=keyfile,
                    command=command,
                ):
                    queue.put(f"{first_host} SSH: {result}")

            queue.put(
                f"echo Check installation process and results. Installer is available at https://{first_host}:9443/"
            )


    except Exception as error:
        print("Cluster creation exception", error)
        queue.put(TASK_FINISHED)
        if dryrun:
            return response
        else:
            return False

    queue.put(TASK_FINISHED)
    if dryrun:
        return response
    else:
        return True


@fire_and_forget
def client(
    server: str,
    client: str,
    username: str,
    password: str,
    repo: str,
    queue: Queue,
):
    repo_content = REPO_CONTENT.format(repo=repo)

    try:
        ssh_content_into_file(
            host=client,
            username=username,
            password=password,
            content=repo_content,
            filename="/etc/yum.repos.d/mapr.repo",
        )

        commands = INSTALL_COMMANDS[DFCLIENT]

        for file in DF_SECURE_FILES:
            commands.append(
                f"sudo curl -s --insecure --user mapr:mapr sftp://{server}{file} --output {file}"
            )

        # Run these last
        commands.append(
            f"sudo /opt/mapr/server/configure.sh -c -C {server} -N ezdf -secure"
        )
        commands.append("echo mapr | sudo -u mapr maprlogin password")

        for command in commands:
            # print(f"Runnning {command}")
            for result in ssh_run_command(
                host=client, username=username, password=password, command=command
            ):
                if result.strip() != "":
                    queue.put(f"{client} SSH: {result}")

    except Exception as error:
        print("Client configuration exception", error)
        queue.put(TASK_FINISHED)
        return False

    queue.put(TASK_FINISHED)
    return True


@fire_and_forget
def crosscluster(
    config: dict,
    settings: dict,
    queue: Queue,
    dryrun: bool = True,
):
    local = settings["crosslocalcldb"]
    remote = settings["crossremotecldb"]
    adminuser = settings["crossadminuser"]
    adminpassword = settings["crossadminpassword"]
    username = config["username"]
    keyfile = config["privatekeyfile"]

    queue.put(f"Create cross cluster connectivity between {local} and {remote}")

    response = {}
    if dryrun:
        response["task"] = f"Cross-cluster setup between {local} and {remote}"
        response["settings"] = {**config, **settings}

    else:  # get truststore passwords
        try:
            local_truststore_password = ""
            remote_truststore_password = ""

            for out in ssh_run_command(
                host=local,
                command="sudo grep ssl.server.truststore /opt/mapr/conf/store-passwords.txt | cut -d'=' -f2",
                username=username,
                keyfile=keyfile,
            ):
                local_truststore_password = out

            for out in ssh_run_command(
                host=remote,
                command="sudo grep ssl.server.truststore /opt/mapr/conf/store-passwords.txt | cut -d'=' -f2",
                username=username,
                keyfile=keyfile,
            ):
                remote_truststore_password = out

            if local_truststore_password and remote_truststore_password:
                queue.put(
                    f"using local truststore password: {local_truststore_password}"
                )
                queue.put(
                    f"using remote truststore password: {remote_truststore_password}"
                )
            else:
                queue.put(
                    f"ERROR: failed to get truststore passwords, local: {local_truststore_password}, remote: {remote_truststore_password}"
                )
                return False
        except Exception as error:
            print("Cross cluster setup exception", error)
            queue.put(TASK_FINISHED)
            return False

    cross_cluster_setup = f"sudo rm -rf /tmp/mapr-xcs; sudo -i -u {adminuser} /opt/mapr/server/configure-crosscluster.sh create all \
    -localcrossclusteruser {adminuser} -remotecrossclusteruser {adminuser} \
    -localtruststorepassword {local_truststore_password if local_truststore_password else 'LOCAL_TRUSTSTORE_PASSWORD'} \
    -remotetruststorepassword {remote_truststore_password if remote_truststore_password else 'REMOTE_TRUSTSTORE_PASSWORD'} \
    -remoteip {remote} -localuser {adminuser} -remoteuser {adminuser}"

    if dryrun:
        response["commands"] = (
            f"ssh {local} sudo grep ssl.server.truststore /opt/mapr/conf/store-passwords.txt | cut -d'=' -f2"
        )
        response["commands"] = (
            f"ssh {remote} sudo grep ssl.server.truststore /opt/mapr/conf/store-passwords.txt | cut -d'=' -f2"
        )
        response["commands"] = cross_cluster_setup
        queue.put(TASK_FINISHED)
        return response

    else:
        try:
            queue.put(
                "If fails run the configure-crosscluster.sh command on one of the cluster nodes:"
            )
            queue.put(cross_cluster_setup)

            client = SSHClient()
            client.set_missing_host_key_policy(AutoAddPolicy)

            client.connect(hostname=local, username=username, key_filename=keyfile)

            interact = SSHClientInteraction(client, timeout=300, display=True)
            prompt = f".*[{username}@{local} ~]$.*"
            interact.expect(prompt)
            # print(interact.current_output_clean)

            interact.send(cross_cluster_setup)

            interact.expect("Enter password for mapr user.*")
            interact.send(adminpassword)
            interact.expect("Enter password for mapr user.*")
            interact.send(adminpassword)

            interact.expect(prompt)
            interact.send("exit")
            interact.expect()
        except Exception as error:
            print("Cross cluster setup exception", error)
            queue.put(TASK_FINISHED)
            return False

        queue.put(TASK_FINISHED)
        return True


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
  mapr_core_version: 7.6.0
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
  mep_version: 9.2.1
  disks:
{disks_yaml}
  disk_format: true
  disk_stripe: 1
  cluster_name: {cluster_name}
  services:
    # template-05-converged:
    # template-30-maprdb:
    template-60-maprxd:
    mapr-keycloak:
      enabled: True
    mapr-hivemetastore:
      database:
        name: hive
        user: hive
        password: mapr123
    mapr-grafana:
      enabled: False
    mapr-opentsdb:
      enabled: False
    mapr-collectd:
      enabled: False
    mapr-fluentd:
      enabled: False
    mapr-kibana:
      enabled: False
    mapr-elasticsearch:
      enabled: False
    mapr-data-access-gateway:
    mapr-mastgateway:

"""
