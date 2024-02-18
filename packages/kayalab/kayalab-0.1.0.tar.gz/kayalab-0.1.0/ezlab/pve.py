from ipaddress import ip_address
import queue
from time import sleep
from urllib.parse import quote
from proxmoxer import ProxmoxAPI


from .utils import *


def connect(host, username, password):
    try:
        return ProxmoxAPI(
            host,
            user=username,
            password=password,
            verify_ssl=False,
        )

    except Exception as error:
        print(error)
        return None


def vms(proxmox):
    return proxmox.cluster.resources.get(type="vm")


def storage(proxmox):
    return proxmox.cluster.resources.get(type="storage")


def networks(proxmox):
    return proxmox.cluster.resources.get(type="sdn")


def bridges(proxmox, fromtemplatename):
    if not fromtemplatename or fromtemplatename == "":
        return []

    try:
        template = [
            t for t in vms(proxmox) if t["template"] and t["name"] == fromtemplatename
        ].pop()
    except IndexError:
        return []

    return (
        proxmox.nodes(template["node"]).network.get(type="any_bridge")
        if template
        else []
    )


@fire_and_forget
def clone_vm(
    proxmox: ProxmoxAPI,
    resources: tuple,
    settings: dict,
    vm_number: int,
    queue: queue.Queue,
    dryrun: bool,
):
    template, volume, bridge, eznode, hostname, first_ip = resources

    node = template["node"]
    template_type = template["type"]
    template_id = template["vmid"]

    vm_gateway = settings["gateway"]
    vm_network_bits = settings["cidr"].split("/")[1]
    privatekey: str = settings["privatekey"]

    # cloudinit requires OpenSSH format public key
    pk = get_privatekey_from_string(privatekey)
    publickey = get_opensshpub(pk)

    multivm = vm_number > 0 

    queue.put(f"Starting clone for VM{str(vm_number) if multivm else ''}")

    # wait for others to request vmid
    sleep(vm_number * 4)
    nextid = proxmox.cluster.nextid.get()
    queue.put(f"Assigned {nextid}")

    vm_name = hostname + str(vm_number if multivm else "")

    ipconfig = "ip="
    vm_ip = ""
    if first_ip == "dhcp":
        ipconfig += "dhcp"
    else:
        vm_ip = str(
            ip_address(first_ip) + vm_number - 1 if multivm else ip_address(first_ip)
        )  # adjust for single VM
        ipconfig += f"{vm_ip}/{vm_network_bits}"
        ipconfig += f",gw={vm_gateway}"

    queue.put(f"{vm_name} ({nextid}) creating")

    if dryrun:
        queue.put(f"Would clone VM as {vm_name}")

    else:
        if task_waitfor(
            proxmox,
            node,
            proxmox.nodes(node)(template_type)(template_id).clone.post(
                newid=nextid,
                name=vm_name,
                description=eznode["name"],
            ),
        ):
            new_vm = proxmox.nodes(node)(template_type)(nextid)
            queue.put(f"{vm_name} cloned")
        else:
            queue.put(TASK_FINISHED)
            return False

    if dryrun:
        queue.put(f"""Would update VM as:
            cores={eznode["cores"]},
            memory={eznode["memGB"] * 1024},
            net0={f"virtio,bridge={bridge},firewall=0"},
            ipconfig0={ipconfig},
            tags={eznode["product"]},
            ciuser={settings["username"]},
            cipassword={'*'*8},
            nameserver={settings["nameserver"]},
            searchdomain={settings["domain"]},
            ciupgrade=0,
            sshkeys={quote(publickey, safe="")},
            onboot=1,
            efidisk0={volume['storage']}:1,efitype=4m,pre-enrolled-keys=1,size=4M",
                  """)

    else:

        # configure vm
        new_vm.config.post(
            cores=eznode["cores"],
            memory=eznode["memGB"] * 1024,
            net0=f"virtio,bridge={bridge},firewall=0",
            ipconfig0=ipconfig,
            tags=eznode["product"],
            ciuser=settings["username"],
            cipassword=settings["password"],
            nameserver=settings["nameserver"],
            searchdomain=settings["domain"],
            ciupgrade=0,
            sshkeys=quote(publickey, safe=""),
            onboot=1,
            efidisk0=f"{volume['storage']}:1,efitype=4m,pre-enrolled-keys=1,size=4M",
        )
        queue.put(f"{vm_name} reconfigured")

    if dryrun:
        queue.put(f"""Would configure disks:
                  OS Disk: {eznode['os_disk_size']}G
                  Data Disks (qty: {eznode["no_of_disks"]}): {volume['storage']}:{eznode['data_disk_size']},backup=0,discard=on,cache=unsafe,iothread=1,replicate=0,ssd=1
                  """)

    else:
        # configure disks
        new_vm.resize.put(disk="scsi0", size=f"{eznode['os_disk_size']}G")
        # add new disks /// assume no_of_disks are 0 or 1 or 2
        if eznode["no_of_disks"] > 0:
            new_disk = f"{volume['storage']}:{eznode['data_disk_size']},backup=0,discard=on,cache=unsafe,iothread=1,replicate=0,ssd=1"
            new_vm.config.post(scsi1=new_disk)
        if eznode["no_of_disks"] > 1:
            new_disk = f"{volume['storage']}:{eznode['data_disk_size']},backup=0,discard=on,cache=unsafe,iothread=1,replicate=0,ssd=1"
            new_vm.config.post(scsi1=new_disk, scsi2=new_disk)

        queue.put(f"{vm_name} disks attached")

        # # create swap disk (recommended for DF 10% of memGB) with roundup
        # swap_size = int(eznode["memGB"] // 10 + 1)
        # swap_disk = f"{volume['storage']}:{swap_size},backup=0,discard=on,cache=unsafe,iothread=1,replicate=0,ssd=1"
        # new_vm.config.post(scsi6=swap_disk)
        # queue.put(f"swap disk added with {swap_size}GB")

        # start vm
        new_vm.status.start.post()

        queue.put(f"{vm_name} started")

        # # add to dns
        # # if vm_ip and defaults["dns_api"] != "":
        # #     result = technitium_add_record(hostname=vm_name, ip=vm_ip)
        # #     if isinstance(result, Response) and result.json()["status"] == "ok":
        # #         print(f"dns record added for {vm_name}:{vm_ip}")
        # #     else:
        # #         print(result)
        # # apply customisations to vm

        if not wait_for_ssh(vm_ip, settings["username"], settings["privatekey"]):
            queue.put(f"SSH failed for {vm_ip}")
            queue.put(TASK_FINISHED)
            return False

        # # reboot for changes
        # task_waitfor(
        #     connection=proxmox,
        #     node=node,
        #     task_id=new_vm.status.reboot.post(timeout=60),
        #     title=f"reboot {vm_name}",
        # )
        queue.put(f"{vm_name} ready for {eznode['product']}")
        queue.put(TASK_FINISHED)

    # catch all
    queue.put(TASK_FINISHED)


def task_waitfor(proxmox, node, task_id):
    task_submitted = proxmox.nodes(node).tasks(task_id).status.get()
    if task_submitted["status"] == "stopped":
        return task_submitted["exitstatus"]

    try:
        status = proxmox.nodes(node).tasks(task_id).status.get()
        while status["status"] != "stopped":
            print(f"{status['type']} is {status['status']}")
            sleep(3)
            status = proxmox.nodes(node).tasks(task_id).status.get()
    except Exception as error:
        return error

    return True
