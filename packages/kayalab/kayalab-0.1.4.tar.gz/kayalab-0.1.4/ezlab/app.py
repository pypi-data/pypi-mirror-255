#!/usr/bin/env python3

# Dependent packages
import asyncio
import logging
import os
import random
import string
import time
from nicegui import app, ui, run
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from queue import Empty, Queue


# Module packages
from .parameters import *
from .utils import *
from .ezdf import *
# from .ezua import *
# from . import kvm
from . import pve
# from . import vmw


class ConnectionContext:
    connection = None

    def __init__(self) -> None:
        pass

# Module Globals
logger = logging.getLogger("ezlab")
logger.setLevel(level=logging.DEBUG)
ez = ConnectionContext()

# Utility
class LogElementHandler(logging.Handler):
    """A logging handler that emits messages to a log element."""

    def __init__(self, element: ui.log, level: int = logging.NOTSET) -> None:
        self.element = element
        super().__init__(level)

    def emit(self, record: logging.LogRecord) -> None:
        try:
            msg = self.format(record)
            self.element.push(msg)
            with open("ezrun.log", "a") as f:
                print(msg, file=f)
        except Exception:
            self.handleError(record)


@ui.refreshable
def ssh_keys_ui():
    if is_file(SSHKEYNAME):
        ui.label(f"Existing Key: {os.path.abspath(SSHKEYNAME)}")
    with ui.row():
        ui.upload(
            label="Import",
            on_upload=lambda e: save_sshkey(e.content.read().decode("utf-8")),
            on_rejected=lambda x: ui.notify("No file selected"),
            max_file_size=1_000_000,
            max_files=1,
            auto_upload=True,
        ).props("accept=*")

        ui.button("Create New", on_click=create_sshkey)


async def confirm_overwrite(file):
    with ui.dialog() as dialog, ui.card():
        ui.label(f"{file} will be overwritten, are you sure?")
        with ui.row():
            ui.button("Yes", on_click=lambda: dialog.submit("Yes"))
            ui.button("No", on_click=lambda: dialog.submit("No"))
    return await dialog


async def save_sshkey(key: str):
    # verify format and get private key
    private_key = get_privatekey_from_string(key)
    if private_key is None:
        ui.notify("Not a known key format", type="negative")
        return None

    if is_file(SSHKEYNAME):
        if await confirm_overwrite(SSHKEYNAME) != "Yes":
            ui.notify("Cancelled", type="warning")
            return None

    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.OpenSSH,
        encryption_algorithm=serialization.NoEncryption(),
    )
    with open(SSHKEYNAME, "wb") as private_keyfile:
        private_keyfile.write(private_pem)

    public_pem = (
        private_key.public_key()
        .public_bytes(
            encoding=serialization.Encoding.OpenSSH,
            format=serialization.PublicFormat.OpenSSH,
        )
        .decode("utf-8")
    )

    with open(f"{SSHKEYNAME}.pub", "w") as public_keyfile:
        public_keyfile.write(public_pem)

    app.storage.general["config"]["privatekey"] = key
    app.storage.general["config"]["privatekeyfile"] = os.path.abspath(SSHKEYNAME)

    ui.notify(f"Key saved as {os.path.abspath(SSHKEYNAME)}", type="positive")
    ssh_keys_ui.refresh()
    return True


async def create_sshkey():
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.OpenSSH,
        encryption_algorithm=serialization.NoEncryption(),
    ).decode("utf-8")
    await save_sshkey(private_pem)


# Top-level UI menus
@ui.refreshable
def infra_menu():
    with (
        ui.expansion("VMs", icon="computer", caption="create and configure")
        .classes("w-full")
        .classes("text-bold") as virtualmachines
    ):
        with ui.row().classes("w-full items-center justify-between"):
            # target connection
            connect_ui()
            # new vm button
            ui.label().bind_text_from(
                app.storage.general["target"],
                "hve",
                backward=lambda x: f"{x} connected",
            ).bind_visibility_from(app.storage.general["target"], "connected")
            ui.button(
                "New VM", on_click=new_vm
            ).bind_visibility_from(app.storage.general["target"], "connected").bind_enabled_from(app.storage.user, "busy", backward=lambda x: not x)

    virtualmachines.bind_value(app.storage.general["ezui"], "virtualmachines")


@ui.refreshable
def ezmeral_menu():
    with (
        ui.expansion(
            "Ezmeral",
            icon="analytics",
            caption="install, configure and use",
        )
        .classes("w-full")
        .classes("text-bold") as ezmeral
    ):
        ui.label("Data Fabric").classes("text-bold")

        with ui.stepper().props("vertical").classes("w-full") as stepper:
            with ui.step("Configure", icon=""):
                df_prepare_ui()
                with ui.stepper_navigation():
                    ui.button(
                        "Setup",
                        icon="navigate_next",
                        on_click=lambda: dfprepare(stepper),
                    ).bind_enabled_from(
                        app.storage.user, "busy", backward=lambda x: not x
                    )
                    ui.button(
                        "Skip",
                        icon="skip_next",
                        on_click=stepper.next,
                    ).props("color=secondary")

            with ui.step("Install"):
                ui.input("Cluster Name", placeholder="ezlab").bind_value(
                    app.storage.general[DF], "cluster_name"
                ).classes("w-full")

                install_on_hosts = ui.input(
                    "Hosts",
                    placeholder="One or more comma-separated IPs, i.e., 10.1.1.x,10.1.1.y",
                    value=",".join([h["ip"] for h in app.storage.general[DF]["hosts"]]),
                ).classes("w-full")

                ui.input(
                    "Disks",
                    placeholder="One or more comma-separated raw disk path, i.e., /dev/sdb,/dev/vdb",
                ).bind_value(app.storage.general[DF], "maprdisks").classes("w-full")

                with ui.stepper_navigation():
                    ui.button(
                        "Install",
                        icon="navigate_next",
                        on_click=lambda: dfinstall(install_on_hosts.value, stepper),
                    ).bind_enabled_from(
                        app.storage.user, "busy", backward=lambda x: not x
                    )
                    ui.button(
                        "Skip",
                        icon="skip_next",
                        on_click=stepper.next,
                    ).props("color=secondary")
                    ui.button("Back", on_click=stepper.previous).props("flat")

            with ui.step("Cross-Cluster"):
                ui.label("Configure two clusters to join global namespace")
                ui.input(
                    "Local Cluster CLDB node", placeholder="core.ez.lab"
                ).bind_value(app.storage.general[DF], "crosslocalcldb").classes(
                    "w-full"
                )
                ui.input(
                    "Remote Cluster CLDB node", placeholder="edge.ez.lab"
                ).bind_value(app.storage.general[DF], "crossremotecldb").classes(
                    "w-full"
                )
                ui.input("Cluster Admin User", placeholder="mapr").bind_value(
                    app.storage.general[DF], "crossadminuser"
                ).classes("w-full")
                ui.input(
                    "Cluster Admin Password",
                    placeholder="mapr",
                    password=True,
                    password_toggle_button=True,
                ).bind_value(app.storage.general[DF], "crossadminpassword").classes(
                    "w-full"
                )

                with ui.stepper_navigation():
                    ui.button(
                        "Setup",
                        icon="navigate_next",
                        on_click=lambda: dfcrosscluster(stepper),
                    ).bind_enabled_from(
                        app.storage.user, "busy", backward=lambda x: not x
                    )
                    ui.button(
                        "Skip",
                        icon="skip_next",
                        on_click=stepper.next,
                    ).props("color=secondary")
                    ui.button("Back", on_click=stepper.previous).props("flat")

            with ui.step("Client"):
                ui.label("Client setup for DF")
                with ui.stepper_navigation():
                    ui.button(
                        "Connect",
                        icon="navigate_next",
                        on_click=lambda: dfclient(stepper),
                    ).bind_enabled_from(
                        app.storage.user, "busy", backward=lambda x: not x
                    )
                    ui.button("Back", on_click=stepper.previous).props("flat")

    ezmeral.bind_value(app.storage.general["ezui"], "ezmeral")


@ui.refreshable
def settings_menu():
    with (
        ui.expansion(
            "Settings",
            icon="settings",
            caption="for your environment",
        )
        .classes("w-full")
        .classes("text-bold") as settings
    ):
        ui.checkbox("Dry Run", value=False).bind_value(
            app.storage.general["config"], "dryrun"
        )
        ui.label("Network Settings").classes("text-bold")
        with ui.row():
            ui.input("VM Network", placeholder="10.1.1.0/24").bind_value(
                app.storage.general["config"], "cidr"
            )
            ui.input("Gateway", placeholder="10.1.1.1").bind_value(
                app.storage.general["config"], "gateway"
            )
            ui.input("Name Server", placeholder="10.1.1.1").bind_value(
                app.storage.general["config"], "nameserver"
            )
            ui.input("Domain", placeholder="ez.lab").bind_value(
                app.storage.general["config"], "domain"
            )
            ui.input("HTTP Proxy", placeholder="").bind_value(
                app.storage.general["config"], "proxy"
            )

        ui.label("Repositories").classes("text-bold")
        with ui.row().classes("w-full"):
            # YUM Repo
            ui.input("YUM Repo", placeholder="").bind_value(
                app.storage.general["config"], "yumrepo"
            )

            ui.input("EPEL Repo", placeholder="").bind_value(
                app.storage.general["config"], "epelrepo"
            )

        # MapR Repository Configuration
        with ui.row().classes("w-full"):
            ui.label("MapR Repo").classes("self-center")
            switch = (
                ui.switch("Use local", value=False)
                .props("left-label")
                .bind_value(app.storage.general["config"], "maprrepoislocal")
            )

            # Using default HPE repository
            with (
                ui.row()
                .bind_visibility_from(switch, "value", lambda x: not x)
                .classes("w-full items-justify")
            ):
                ui.input("HPE Passport e-mail").bind_value(
                    app.storage.general["config"], "maprrepouser"
                )
                ui.input(
                    "HPE Passport token", password=True, password_toggle_button=True
                ).bind_value(app.storage.general["config"], "maprrepotoken")

            # Using local repository
            with ui.row().bind_visibility_from(switch, "value"):
                ui.input(
                    "MapR Repo",
                    placeholder="https://repo.ez.lab/mapr/",
                ).bind_value(app.storage.general["config"], "maprlocalrepo")
                authlocal = ui.switch("Authenticate", value=True).bind_value(
                    app.storage.general["config"], "maprlocalrepoauth"
                )
                with ui.row():
                    ui.input("Username", password=True).bind_value(
                        app.storage.general["config"], "maprlocalrepousername"
                    ).bind_visibility(authlocal, "value")
                    ui.input("Password", password=True).bind_value(
                        app.storage.general["config"], "maprlocalrepopassword"
                    ).bind_visibility(authlocal, "value")

        ui.label("Cloudinit Settings").classes("text-bold")
        with ui.row():
            ui.input("username", placeholder="ezmeral").bind_value(
                app.storage.general["config"], "username"
            )
            ui.input("password", password=True, password_toggle_button=True).bind_value(
                app.storage.general["config"], "password"
            )

        ui.label("SSH Key").classes("text-bold")
        ssh_keys_ui()

    settings.bind_value(app.storage.general["ezui"], "settings")


# Business logic
async def connect(params: set):
    target, host, username, password = params
    try:
        if target == PVE:
            return await asyncio.to_thread(pve.connect, host, username, password)
        # elif target == KVM:
        #     return await asyncio.to_thread(kvm.connect, host, username, password)
        # elif target == VMWARE:
        #     return await asyncio.to_thread(vmw.connect, host, username, password)

    except Exception as error:
        ui.notify(error, type="negative")


async def new_vm():

    if app.storage.general["target"]["hve"] == PVE:
        try:
            app.storage.user["busy"] = True

            templates = [
                x
                for x in pve.vms(ez.connection)
                if x["template"] and x["type"] == "qemu"
            ]
            networks = pve.networks(ez.connection)
            storage = pve.storage(ez.connection)

            app.storage.user["busy"] = False

            if "template" not in app.storage.user.keys():
                app.storage.user["template"] = templates[0]

            def set_template(name):
                app.storage.user["template"] = [
                    t for t in templates if t["name"] == name
                ].pop()

            # select dialog
            with ui.dialog() as dialog, ui.card():
                t = (
                    ui.select(
                        options=[x["name"] for x in templates],
                        label="Template",
                        on_change=lambda e: set_template(e.value),
                    )
                    .classes("w-full")
                    .props("inline")
                    .bind_value(app.storage.general[PVE], "template")
                )
                s = (
                    ui.select(
                        options=[
                            x["storage"]
                            for x in storage
                            if x["node"] == app.storage.user["template"]["node"]
                        ],
                        label="Storage",
                    )
                    .classes("w-full")
                    .props("inline")
                    .bind_value(app.storage.general[PVE], "storage")
                )
                n = (
                    ui.select(
                        options=[
                            x["sdn"]
                            for x in networks
                            if x["node"] == app.storage.user["template"]["node"]
                        ],
                        label="Network",
                    )
                    .classes("w-full")
                    .props("inline")
                    .bind_value(app.storage.general[PVE], "network")
                )

                b = (
                    ui.select(
                        options=[
                            x["iface"]
                            for x in pve.bridges(
                                ez.connection, app.storage.user["template"]["name"]
                            )
                        ],
                        label="Bridge",
                    )
                    .classes("w-full")
                    .props("inline")
                    .bind_value(app.storage.general[PVE], "bridge")
                )

                e = (
                    ui.select(
                        options=[x["name"] for x in EZNODES],
                        label="Node Type",
                    )
                    .classes("w-full")
                    .props("inline")
                    .bind_value(app.storage.general[PVE], "eznode")
                )

                h = (
                    ui.input(label="VM Name", placeholder="ezvm")
                    .classes("w-full")
                    .props("inline")
                    .bind_value(app.storage.general[PVE], "hostname")
                )

                f = (
                    ui.input(
                        label="First IP",
                        placeholder=app.storage.general["config"]["gateway"],
                    )
                    .classes("w-full")
                    .props("inline")
                    .bind_value(app.storage.general[PVE], "firstip")
                )

                ui.button(
                    "Create",
                    on_click=lambda: dialog.submit(
                        (
                            next(
                                (
                                    # {"template": i}
                                    i
                                    for i in templates
                                    if i["name"] == t.value
                                ),
                                None,
                            ),
                            next(
                                (
                                    # {"storage": i}
                                    i
                                    for i in storage
                                    if i["storage"] == s.value
                                ),
                                None,
                            ),
                            # next(
                            #     (i for i in networks if i["sdn"] == n.value),
                            #     None,
                            # ),
                            b.value,  # Bridge
                            next(
                                (i for i in EZNODES if i["name"] == e.value),
                                None,
                            ),
                            h.value,  # hostname
                            f.value,  # firstip
                        )
                    ),
                )

            resources = await dialog
            if resources and all(resources):
                try:
                    vmcount = resources[3]["count"]

                    logger.info(f"Cloning {vmcount} VMs...")

                    queue = Queue(1000)
                    for count in range(vmcount):
                        # await run.io_bound(watch_clone_status, resources, n)
                        # run.io_bound(
                        pve.clone_vm(
                            proxmox=ez.connection,
                            resources=resources,
                            settings=dict(app.storage.general["config"]),
                            vm_number=0 if vmcount == 1 else count + 1,  # start from 1 not 0, use 0 for single vm
                            queue=queue,
                            dryrun=app.storage.general["config"].get("dryrun", True)
                        )
                    # reset counter to monitor completed tasks
                    app.storage.general["ezui"]["finished_tasks"] = 0

                    app.storage.user["busy"] = True
                    res = await run.io_bound(process_queue_messages, queue, vmcount)
                    if res:
                        ui.notify(f"Clone for {vmcount} VM(s) completed successfully", type="positive")

                    app.storage.user["busy"] = False
                    return True

                except Exception as error:
                    logger.error(error, exc_info=True)
                    app.storage.user["busy"] = False
                    return False

            else:
                ui.notify(f"Missing resources")

        except Exception as error:
            print("Query PVE error", error)
            ui.notify(f"PVE Error: {error}", type="negative")
            app.storage.user["busy"] = False

    else:
        ui.notify("not implemented")

    app.storage.user["busy"] = False
    return False


def process_queue_messages(queue: Queue, number_of_tasks: int = 1):
    while True:
        try:
            message = queue.get_nowait()
            if message is not None and TASK_FINISHED in message:
                app.storage.general["ezui"]["finished_tasks"] += 1
                logger.info(
                    f"Completed jobs: {app.storage.general['ezui']['finished_tasks']}"
                )
                if app.storage.general["ezui"]["finished_tasks"] == number_of_tasks:
                    logger.info("All tasks completed")
                    app.storage.general["ezui"]["finished_tasks"] = 0
                    queue.task_done()
                    return True
            else:
                if "error" in message or "failed" in message:
                    logger.error(message)
                    # ui.notify(message=message, type='warning', position='bottom-right')
                else:
                    logger.info(message)
            queue.task_done()
        except Empty:
            pass
        except Exception as error:
            queue.put(TASK_FINISHED)
            queue.task_done()
            print(error)


def connect_ui():
    # Login dialog
    with ui.dialog() as dialog, ui.card():
        t = (
            ui.radio(options=SUPPORTED_HVES)
            .classes("w-full")
            .props("inline")
            .bind_value(app.storage.general["target"], "hve")
        )

        h = (
            ui.input("Host", validation={"Required": nonzero})
            .classes("w-full")
            .bind_value(app.storage.general["target"], "host")
        )

        u = (
            ui.input("Username", validation={"Required": nonzero})
            .classes("w-full")
            .bind_value(app.storage.general["target"], "username")
        )

        p = (
            ui.input(
                "Password",
                password=True,
                password_toggle_button=True,
                validation={"Required": nonzero},
            )
            .classes("w-full")
            .bind_value(app.storage.general["target"], "password")
        )

        ui.button(
            "Login",
            on_click=lambda: dialog.submit((t.value, h.value, u.value, p.value)),
        )

    async def process_login():
        if app.storage.general["target"]["connected"]:
            # TODO: disconnect process/cleanup
            app.storage.general["target"]["connected"] = False
        else:
            result = await dialog
            if result:
                app.storage.user["busy"] = True
                connection = await connect(result)
                if connection:
                    app.storage.general["target"]["connected"] = True
                    ez.connection = connection
                else:
                    app.storage.general["target"]["connected"] = False
                    ui.notify(f"Get {connection} instead of a valid response")
                app.storage.user["busy"] = False

    with ui.row() as connection_status:
        ui.button(icon="cloud_done", on_click=process_login).bind_visibility_from(
            app.storage.general["target"],
            "connected",
        )
        ui.button(icon="cloud_off", on_click=process_login).bind_visibility_from(
            app.storage.general["target"],
            "connected",
            lambda x: not x,
        )
        # .bind_text_from(
        #     app.storage.general["target"],
        #     "connected",
        #     lambda x: "Disconnect" if x else "Connect",
        # )

    return connection_status


# Product specific UIs
async def dfprepare(pager: ui.stepper):
    hosts = app.storage.general[DF]["hosts"]
    # deep check list[dict] for missing values (if any host's name or IP is missing)
    if not (
        len(hosts) > 0
        and all(
            [values for values in [all(host) for host in [h.values() for h in hosts]]]
        )
    ):
        ui.notify("Missing values", type="warning")
        return False

    queue = Queue(1000)
    queue.put("Starting configuration for DF")
    for host in hosts:
        result = prepare_vm(
            hostname=host["name"],
            hostip=host["ip"],
            config=dict(app.storage.general["config"]),
            addhosts=[h for h in hosts if h["name"] != host["name"]],
            prepare_for=DF,
            queue=queue,
            dryrun=app.storage.general["config"]["dryrun"],
        )
        if app.storage.general["config"]["dryrun"]:
            get_doc(await result)
        elif result:
            pass
        else:
            ui.notify(f"{host} preparation failed!", type="warning")

    app.storage.user["busy"] = True
    res = await run.io_bound(process_queue_messages, queue, len(hosts))
    app.storage.user["busy"] = False

    if res:
        ui.notify(f"Finished with {len(hosts)} host(s)", type="positive")
        pager.next()
        return True
    else:
        return False


def df_prepare_ui():
    if not "hosts" in app.storage.general[DF].keys():
        app.storage.general[DF]["hosts"] = [{"name": "", "ip": ""}]
    with ui.row().classes("w-full items-center items-stretch") as prep_view:
        ui.label("Hosts")
        ui.space()
        with ui.row():

            def add_host():
                try:
                    app.storage.general[DF]["hosts"].append({"name": "", "ip": ""})
                except (KeyError, AttributeError):
                    app.storage.general[DF]["hosts"] = [{"name": "", "ip": ""}]
                finally:
                    add_remove_host.refresh(app.storage.general[DF]["hosts"])

            def remove_host():
                if len(app.storage.general[DF]["hosts"]) > 0:
                    app.storage.general[DF]["hosts"].pop()
                    add_remove_host.refresh()

            ui.button(icon="add_box", color=None, on_click=add_host).props("flat")
            ui.button(icon="delete", color=None, on_click=remove_host).props("flat")

    # Hosts
    add_remove_host(app.storage.general[DF]["hosts"])


async def dfinstall(hosts_string: str, pager: ui.stepper):
    queue = Queue(1000)
    queue.put("Starting DF cluster installation")

    result = cluster_install(
        hosts=hosts_string.split(","),
        config=dict(app.storage.general["config"]),
        queue=queue,
        name=app.storage.general[DF]["cluster_name"],
        disks=app.storage.general[DF]["maprdisks"],
        dryrun=app.storage.general["config"]["dryrun"],
    )

    if app.storage.general["config"]["dryrun"]:
        get_doc(await result)

    elif not result:
        ui.notify(f"Cluster creation failed!", type="negative")

    app.storage.user["busy"] = True
    res = await run.io_bound(process_queue_messages, queue, 1)
    app.storage.user["busy"] = False
    if res:
        ui.notify(f"Finished cluster creation", type="positive")
        pager.next()
        return True
    else:
        return False


async def dfcrosscluster(pager: ui.stepper):
    queue = Queue(1000)
    queue.put("Starting DF cross-cluster setup")

    if not crosscluster(
        config=dict(app.storage.general["config"]),
        settings=dict(app.storage.general[DF]),
        queue=queue,
    ):
        ui.notify(f"Cluster creation failed!", type="negative")

    app.storage.user["busy"] = True
    res = await run.io_bound(process_queue_messages, queue, 1)
    app.storage.user["busy"] = False
    if res:
        ui.notify(f"Finished cross-cluster setup", type="positive")
        pager.next()
        return True
    else:
        return False


async def dfclient(pager: ui.stepper):
    ui.notify("Not implemented", type='warning')
    return False

@ui.refreshable
def add_remove_host(hosts: list):
    if hosts is None:
        hosts = []
    for host in hosts:
        with ui.row().classes("w-full items-center no-wrap"):
            ui.input(
                "Hostname",
                placeholder="Host shortnames, ie, ezvm1,ezvm2...",
            ).bind_value(host, "name")
            ui.input(
                "IP Address",
                placeholder="10.1.1.x",
            ).bind_value(host, "ip")


def ua_ui(args):
    ui.notify(args)


#  async def vmware_ui(connection):
#     si = connection
#     vmtable = ui.table(
#         title="VMs",
#         columns=vmw.VM_COLUMNS,
#         rows=[],
#         selection="single",
#         on_select=lambda x: print(x),
#     ).classes("w-full max-h-200")

#     logger.info("waiting vms")

#     try:
#         for vm in await asyncio.to_thread(vmw.vms, si):
#             vmtable.add_rows([vm])

#     except Exception as e:
#         ui.notify(e, type="negative")

#     finally:
#         print("Done with vm")


def get_doc(content: dict):
    
    random_eof = "".join(random.choices(string.ascii_uppercase + string.digits, k=10))

    def indent(strings:str, spaces: int):
        return strings.strip().replace("\n", f"\n{' '*spaces}")

    settings = ""

    for key,value in content["settings"].items():
        settings += f"""
    #   {key}: {value if len(str(value)) < 80 else value[:77] + '...'}"""

    files = ""
    for filepath, filecontent in content["files"].items():
        files += f"""
    sudo cat <<{random_eof}>{filepath}
    {indent(filecontent,4)}
    {random_eof}
    """

    commands = ""
    for command in content["commands"]:
        commands += f"""
    {indent(command,4)}
    """

    doc = f"""
    #!/usr/bin/env bash

    # Ezlab Run {time.strftime('%Y%m%d%H%M%z')}
    
    # {content["task"]}

    # Settings
        {settings}

    # Write Files
        {files}
    
    # Run Commands
        {commands}

    # End of {content['task']}

"""

    with ui.dialog().props("full-width") as dialog, ui.card().classes("w-full"):
        ui.code(doc, language="bash").classes(
            "w-full text-wrap"
        )
        with ui.row():
            ui.button(
                "Save (useless on app mode)",
                icon="save",
                on_click=lambda: ui.download(doc.encode(), "ezlab-runbook.sh"),
            )
            ui.button(
                "Close",
                icon="cancel",
                on_click=dialog.close,
            )
    dialog.open()
