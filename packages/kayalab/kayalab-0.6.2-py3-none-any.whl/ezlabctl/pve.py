from ipaddress import ip_address
import os
import subprocess
from time import sleep
from urllib.parse import quote
import humanize
from questionary import confirm
from requests import Response
from proxmoxer import ProxmoxAPI

from . import connect
from . import config

from .common import (
    ReturningThread,
    fail,
    get_ssh_key_file,
    multiselect_from_list,
    prepare_vm,
    select_from_list,
    start_tasks_delayed,
    technitium_add_record,
    technitium_delete_record,
    wait_for_ssh,
    wait_tasks,
)


def pve_nextid(proxmox):
    return proxmox.cluster.nextid.get()


def get_connection(host, username, password):
    try:
        return ProxmoxAPI(
            host,
            user=username,
            password=password,
            verify_ssl=False,
        )

    except Exception as error:
        print(error)
        connect.fail("Connection error: " + str(type(error)))


def task_status(proxmox, node, task_id):
    return proxmox.nodes(node).tasks(task_id).status.get()


def template_name(t):
    return (" | ").join([t["name"], t["node"], t["type"]])


def vm_name(vm):
    return (" | ").join([vm["name"], vm["id"], vm["status"]])


def network_name(n):
    return (" | ").join([n["sdn"], n["node"], n["status"]])


def volume_name(v):
    return " | ".join(
        [
            v["storage"],
            v["node"],
            v["plugintype"],
            "/".join(
                [
                    humanize.naturalsize(v["disk"], binary=True),
                    humanize.naturalsize(v["maxdisk"], binary=True),
                ]
            ),
        ]
    )


def vms(proxmox):
    return proxmox.cluster.resources.get(type="vm")


def storage(proxmox):
    return proxmox.cluster.resources.get(type="storage")


def networks(proxmox):
    return proxmox.cluster.resources.get(type="sdn")


def vm_id(vm):
    return vm["id"]


def volume_id(volume):
    return volume["id"]


def network_id(network):
    return network["id"]


def vm_filter(fields):
    return fields["type"] == "qemu" and fields["template"] == 0


def template_filter(fields):
    return fields["type"] == "qemu" and fields["template"] == 1


def volume_filter(fields):
    return "images" in fields["content"].split(",")


def network_filter(fields):
    return True


def select_template(proxmox):
    return select_from_list(
        title="Template",
        list=[x for x in vms(proxmox) if template_filter(x)],
        name_generator=template_name,
        value_generator=vm_id,
    )


def select_storage(proxmox, host=None):
    return select_from_list(
        title="Data Storage",
        list=sorted(
            [x for x in storage(proxmox) if volume_filter(x) and x["node"] == host],
            key=lambda x: x["storage"],
        ),
        name_generator=volume_name,
        value_generator=volume_id,
    )


def select_network(proxmox, host=None):
    return select_from_list(
        title="Network",
        list=[x for x in networks(proxmox) if network_filter(x) and x["node"] == host],
        name_generator=network_name,
        value_generator=network_id,
    )


def select_network_bridge(proxmox, host):
    return select_from_list(
        title="Network Bridge",
        list=proxmox.nodes(host).network.get(type="any_bridge"),
        name_generator=lambda x: (" | ").join([x["iface"], x["cidr"]]),
        value_generator=lambda x: x["iface"],
    )


def select_vms(proxmox):
    return multiselect_from_list(
        title="Virtual Machines",
        list=[x for x in vms(proxmox) if vm_filter(x)],
        name_generator=vm_name,
        value_generator=vm_id,
    )


def select_templates(proxmox):
    return multiselect_from_list(
        title="Templates",
        list=[x for x in vms(proxmox) if template_filter(x)],
        name_generator=vm_name,
        value_generator=vm_id,
    )


def get_resources(proxmox: ProxmoxAPI):
    resources = {}

    resources["template"] = select_template(proxmox) or {}

    resources["volume"] = (
        select_storage(proxmox, host=resources["template"]["node"]) or {}
    )

    resources["network"] = (
        select_network(proxmox, host=resources["template"]["node"]) or {}
    )

    try:
        resources["network"]["bridge"] = (
            select_network_bridge(proxmox, host=resources["network"]["node"]) or {}
        )
    except KeyError as error:
        print(error)  # no network selected

    return resources


def delete_vms(proxmox: ProxmoxAPI):
    vms_to_delete = [x for x in select_vms(proxmox)]
    if vms_to_delete and len(vms_to_delete) > 0:
        [print(vm_name(x)) for x in vms_to_delete]
        if confirm("Are you sure to delete these VMs", default=False).ask():
            threads = list()
            for vm in vms_to_delete:
                task = ReturningThread(
                    target=delete_vm,
                    kwargs={
                        "proxmox": proxmox,
                        "vm": vm,
                    },
                )
                threads.append(task)
            start_tasks_delayed(threads, 0)
            return wait_tasks(threads)
        else:
            print("Ok, backing off")
    else:
        print("No VM selected")
    return None


def delete_vm(proxmox: ProxmoxAPI, vm):
    # capture ip address before delete
    vm_ip = None
    try:
        interfaces = (
            proxmox.nodes(vm["node"])(vm["id"]).agent("network-get-interfaces").get()
        )
        if interfaces:
            interface = [
                int["ip-addresses"]
                for int in interfaces["result"]
                if int["name"] == "eth0"
            ][0]
            vm_ip = [
                addr["ip-address"]
                for addr in interface
                if addr["ip-address-type"] == "ipv4"
            ][0]
    except IndexError:
        print(f"Cannot find IP for {vm['name']}")

    if vm["status"] == "running":
        task_waitfor(
            title=f"Stopping {vm['name']}",
            connection=proxmox,
            node=vm["node"],
            task_id=proxmox.nodes(vm["node"])(vm["id"]).status.stop.post(timeout=30),
        )
    task_waitfor(
        title=f"Deleting {vm['name']}",
        connection=proxmox,
        node=vm["node"],
        task_id=proxmox.nodes(vm["node"])(vm["id"]).delete(purge=1),
    )
    if vm_ip:
        # remove from known_hosts
        subprocess.Popen(
            ["ssh-keygen", "-R", vm_ip],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        subprocess.Popen(
            ["ssh-keygen", "-R", vm["name"]],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

        # remove from dns
        if vm_ip and config.get()["NETWORK"]["dns_api"] != "":
            result = technitium_delete_record(hostname=vm["name"], ip=vm_ip)
            if isinstance(result, Response) and result.json()["status"] == "ok":
                print(f"dns record deleted for {vm['name']}")

    return vm["name"]


def delete_templates(proxmox: ProxmoxAPI):
    vms_to_delete = [x for x in select_templates(proxmox)]
    if vms_to_delete and len(vms_to_delete) > 0:
        [print(vm_name(x)) for x in vms_to_delete]
        if confirm("Are you sure to delete these templates", default=False).ask():
            for vm in vms_to_delete:
                if proxmox.nodes(vm["node"])(vm["id"]).delete(purge=1):
                    yield vm["name"]
        else:
            print("Ok, backing off")
    else:
        print("No template selected")
        return None


def get_storage_for(
    connection, content: str = "", plugin: list = [], title: str = "Storage"
):
    content_filter = (
        True if content == "" else lambda x: content in x["content"].split(",")
    )
    plugin_filter = True if plugin == "" else lambda x: x["plugintype"] in plugin
    volumes = [x for x in storage(connection) if content_filter(x) and plugin_filter(x)]  # type: ignore
    if len(volumes) == 0:
        fail(f"No storage available for {content} or {plugin}")
    volume = select_from_list(title, volumes, volume_name, volume_id)
    return volume


def task_waitfor(connection, node, task_id, title):
    task_submitted = task_status(connection, node, task_id)
    if task_submitted["status"] == "stopped":
        fail(task_submitted["exitstatus"])

    print(f"{title}...")
    try:
        while task_status(connection, node, task_id)["status"] != "stopped":
            sleep(3)
    except Exception as error:
        return error

    # task_running = spinner(
    #     title=title,
    #     task=connection.nodes(node).tasks(task_id).status.get,
    #     success=lambda x: x["status"] == "stopped",
    # )

    # if not task_running or isinstance(task_running, Exception):
    #     fail(task_running)

    return True


def download_to_storage(connection, node, storage):
    defaults = config.get()
    images = list(defaults["CLOUDIMG"])
    image_name = select_from_list("Image URL", images, lambda x: x, lambda x: x)
    if image_name:
        image_url = defaults["CLOUDIMG"][image_name]
        if not image_url:
            fail("No image selected for upload")
        # Tricking file extension so API accepts it
        target_filename = f"{os.path.basename(image_url)}.iso"
        task_id = (
            connection.nodes(node)
            .storage(storage)("download-url")
            .post(url=image_url, content="iso", filename=target_filename)
        )

        task_waitfor(connection, node, task_id, "Downloading...")


def create_template(proxmox: ProxmoxAPI):
    defaults = config.get()

    base_image = select_from_list(
        "Base image",
        list(defaults["CLOUDIMG"].keys()),
        lambda x: x,
        lambda x: defaults["CLOUDIMG"][x],
    )

    os_storage = get_storage_for(
        proxmox,
        content="images",
        plugin=["lvmthin", "zfspool", "rbd"],
        title="OS Storage",
    )

    if not os_storage:
        fail("No storage is selected for OS disk")

    else:
        node = os_storage["node"]
        base_image_os = ""
        if base_image:
            for key in defaults["CLOUDIMG"]:
                if base_image in defaults["CLOUDIMG"][key].lower():
                    base_image_os = key
            base_image_full_path = (
                f"/var/lib/vz/template/qemu/{defaults['CLOUDIMG'][base_image_os]}"
            )
            template_name = f"{base_image_os}-template"

            all_vms = vms(proxmox)
            if all_vms:
                num_template = (
                    len([vm for vm in all_vms if template_name in vm["name"]]) + 1
                )
                template_name += str(num_template)

                with open(get_ssh_key_file()) as file:
                    ssh_key = file.read()

                new_vm_id = pve_nextid(proxmox)

                task_id = proxmox.nodes(node).qemu.post(
                    agent="enabled=1,fstrim_cloned_disks=1,freeze-fs-on-backup=0",
                    arch="x86_64",
                    bios="ovmf",
                    boot="order=scsi0",
                    cpu="host",
                    description="Ezlab template",
                    cdrom=f"{os_storage['storage']}:cloudinit",
                    machine="q35",
                    memory="2048",
                    name=template_name,
                    ostype="l26",
                    scsi0=f"{os_storage['storage']}:0,import-from={base_image_full_path},backup=0,discard=on,cache=unsafe,iothread=1,replicate=0,ssd=1",
                    scsihw="virtio-scsi-single",
                    tags="ezlab",
                    template=0,
                    vmid=new_vm_id,
                    ciuser=defaults["CLOUDINIT"]["vm_username"],
                    cipassword=defaults["CLOUDINIT"]["vm_password"],
                    nameserver=defaults["NETWORK"]["vm_nameserver"],
                    searchdomain=defaults["NETWORK"]["vm_domain"],
                    ciupgrade=0,
                    sshkeys=quote(ssh_key, safe=""),
                )

                if task_waitfor(
                    connection=proxmox,
                    node=node,
                    task_id=task_id,
                    title=f"clone for {template_name}",
                ):
                    # refresh cloudinit drive
                    proxmox.nodes(node).qemu(new_vm_id).cloudinit.put()

                    if task_waitfor(
                        connection=proxmox,
                        node=node,
                        task_id=proxmox.nodes(node)
                        .qemu(new_vm_id)
                        .template.post(disk="scsi0"),
                        title="make template",
                    ):
                        yield template_name

                else:
                    fail(f"Failed to clone template {template_name}")


def clone_vms(proxmox: ProxmoxAPI, customisations: dict, nodes: list):
    resources = get_resources(proxmox)
    if not resources["template"]:
        fail("No template selected")

    if not resources["volume"]:
        fail("No volume selected")

    if not resources["network"]:
        fail("No network selected")
    name_index = 0  # index for vm names
    threads = list()
    for ez_node in nodes:
        for idx in range(ez_node["count"]):
            name_index += 1
            task = ReturningThread(
                target=clone_vm,
                kwargs={
                    "proxmox": proxmox,
                    "resources": resources,
                    "customisations": customisations,
                    "ez_node": ez_node,
                    "vm_number": name_index,
                },
            )
            threads.append(task)

    start_tasks_delayed(threads, 2)

    return wait_tasks(threads)


def clone_vm(
    proxmox: ProxmoxAPI,
    resources: dict,
    customisations: dict,
    ez_node: dict,
    vm_number: int,
):
    node = resources["template"]["node"]
    template_type = resources["template"]["type"]
    template_id = resources["template"]["vmid"]
    network_bridge_name = resources["network"]["bridge"]["iface"]

    defaults = config.get()
    vm_gateway = defaults["NETWORK"]["vm_gateway"]
    vm_network_prefix = defaults["NETWORK"]["vm_cidr"].split("/")[1]

    nextid = pve_nextid(proxmox)
    new_vm_name = customisations["vmname"] + str(vm_number)
    ipconfig = "ip="
    vm_ip = ""
    if customisations["first_vm_ip"] == "dhcp":
        ipconfig += "dhcp"
    else:
        vm_ip = str(
            ip_address(customisations["first_vm_ip"]) + (vm_number - 1)
        )  # vm number starting at 1, ip index should start with 0
        ipconfig += f"{vm_ip}/{vm_network_prefix}"
        ipconfig += f",gw={vm_gateway}"

    if task_waitfor(
        connection=proxmox,
        node=node,
        task_id=proxmox.nodes(node)(template_type)(template_id).clone.post(
            newid=nextid,
            name=new_vm_name,
            description=ez_node["name"],
        ),
        title=f"{new_vm_name} cloning",
    ):
        new_vm = proxmox.nodes(node)(template_type)(nextid)

        # configure vm
        new_vm.config.post(
            cores=ez_node["cores"],
            memory=ez_node["memGB"] * 1024,
            net0=f"virtio,bridge={network_bridge_name},firewall=0",
            ipconfig0=ipconfig,
            tags=ez_node["name"],
            onboot=1,
            efidisk0=f"{resources['volume']['storage']}:1,efitype=4m,pre-enrolled-keys=1,size=4M",
        )

        # configure disks
        new_vm.resize.put(disk="scsi0", size=f"{ez_node['os_disk_size']}G")
        # add new disks /// assume no_of_disks are 0 or 1 or 2
        if ez_node["no_of_disks"] > 0:
            new_disk = f"{resources['volume']['storage']}:{ez_node['data_disk_size']},backup=0,discard=on,cache=unsafe,iothread=1,replicate=0,ssd=1"
            new_vm.config.post(scsi1=new_disk)
        if ez_node["no_of_disks"] > 1:
            new_disk = f"{resources['volume']['storage']}:{ez_node['data_disk_size']},backup=0,discard=on,cache=unsafe,iothread=1,replicate=0,ssd=1"
            new_vm.config.post(scsi1=new_disk, scsi2=new_disk)

        # start vm
        new_vm.status.start.post()

    # add to dns
    if vm_ip and defaults["NETWORK"]["dns_api"] != "":
        # TODO: more integrations
        result = technitium_add_record(hostname=new_vm_name, ip=vm_ip)
        if isinstance(result, Response) and result.json()["status"] == "ok":
            print(f"dns record added for {new_vm_name}:{vm_ip}")
        else:
            print(result)
    # apply customisations to vm

    if not wait_for_ssh(vm_ip):
        fail(f"ssh failed for {vm_ip}")

    print(f"configuring {vm_ip}")
    if prepare_vm(
        vm_name=new_vm_name,
        vm_ip=vm_ip,
        product_code=ez_node["product"],
    ):
        print(f"{new_vm_name} configured")

    # # reboot for changes
    # task_waitfor(
    #     connection=proxmox,
    #     node=node,
    #     task_id=new_vm.status.reboot.post(timeout=60),
    #     title=f"reboot {new_vm_name}",
    # )
    return new_vm_name, ez_node["product"]
