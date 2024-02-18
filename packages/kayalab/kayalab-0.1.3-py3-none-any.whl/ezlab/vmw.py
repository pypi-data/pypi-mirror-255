import logging
# from pyVmomi import vim
# from pyVim.connect import SmartConnect, Disconnect
# from .vmw_pchelper import *

logger = logging.getLogger(__name__)

# Constants
VM_COLUMNS = [
    {
        "name": "name",
        "label": "Name",
        "field": "name",
        "align": "left",
        "sortable": True,
    },
    # {"name": "datacenter", "label": "Datacenter", "field": "datacenter", "align": "left"},
    # {"name": "host", "label": "Host", "field": "node", "align": "left"},
    # {"name": "folder", "label": "Folder", "field": "folder", "align": "left"},
    {"name": "status", "label": "Status", "field": "status", "align": "left"},
    {"name": "template", "label": "Template", "field": "template", "align": "left"},
]

DC_COLUMNS = [
    {
        "name": "id",
        "label": "ID",
        "field": "id",
        "align": "left",
        "sortable": True,
    },
    {
        "name": "name",
        "label": "Name",
        "field": "name",
        "align": "left",
        "sortable": True,
    },
]


# Shamelessly borrowed from:
# https://github.com/vmware/pyvmomi-community-samples/tree/master/samples
# def connect(host: str, username: str, password: str):
#     try:
#         return SmartConnect(
#             host=host, user=username, pwd=password, disableSslCertValidation=True
#         )
#         # atexit.register(Disconnect, si)
#     except Exception as e:
#         return e


# def disconnect(si):
#     Disconnect(si)


# def datacenters(si):
#     # return si.RetrieveContent().rootFolder.childEntity
#     content = si.RetrieveContent()
#     dclist = get_all_obj(content, [vim.Datacenter])
#     return [{"id": str(key).strip("'"), "name": dclist[key]} for key in dclist.keys()]


# def vms(si):
#     # for folder in get_all_obj(content, [vim.Folder]):
#     vms = get_all_obj(si.content, [vim.VirtualMachine])
#     for vm in vms:
#         # print(vm.config.name)
#         yield {
#             "id": str(vm).strip("'"),
#             "name": vm.config.name,
#             "config": vm.config,
#             "template": vm.config.template,
#             "parent": vm.parent,
#         }

#     # return [ { 'id': str(key).strip("'"), 'name': vms[key], "config": vms[key].config, "template": vms[key].config.template, "parent": vms[key].parent } for key in vms.keys()]



# ### OLD CODE BELOW

# def select_from_objects(entities, title="Select"):
#     return select_from_list(
#         title=title,
#         list=sorted(entities, key=lambda x: x.name),
#         name_generator=lambda x: x.name,
#     )


# def wait_task_state(task: vim.Task):
#     try:
#         WaitForTask(task)
#     except Exception as e:
#         fail(e)
#     return task.info.state


# def wait_task_result(task: vim.Task):
#     WaitForTask(task)
#     return task.info.result


# def get_resources(si: vim.ServiceInstance):
#     resources = {}
#     content: vim.ServiceInstanceContent = si.RetrieveContent()

#     datacenter: vim.Datacenter = content.rootFolder.childEntity[0]

#     # hostfolder: vim.Folder = datacenter.hostFolder.childEntity[0]

#     # host: vim.HostSystem = hostfolder.host[0]

#     # network: vim.Network = host.network[0]

#     # datastore: vim.Datastore = host.datastore[0]

#     # vm_folder: vim.Folder = datacenter.vmFolder.childEntity[0]

#     # # Handle esxi - no vm_folder childEntity
#     # if isinstance(vm_folder, vim.VirtualMachine):
#     #     vm_folder = datacenter.vmFolder

#     # virtual_machines = [v for v in vms(vm_folder=vm_folder)]
#     # # can use any vm as template, since esxi doesn't support template
#     # # [v for v in get_all_vms(vm_folder=vm_folder) if v.config.template], "Template"

#     # resources.update(
#     # {
#     # "datacenter": datacenter,
#     # "host": host,
#     # "network": network,
#     # "datastore": datastore,
#     # "vm_folder": vm_folder,
#     # "vms": virtual_machines,
#     # }
#     # )

#     return resources


# def create_template(si: vim.ServiceInstance):
#     content: vim.ServiceInstanceContent = si.RetrieveContent()

#     datacenter: vim.Datacenter = select_from_objects(
#         content.rootFolder.childEntity, "Data Center"
#     )

#     hostfolder: vim.Folder = select_from_objects(
#         datacenter.hostFolder.childEntity, "Folder"
#     )

#     host: vim.HostSystem = select_from_objects(hostfolder.host, "Template Host")

#     network: vim.Network = select_from_objects(host.network, "Network")

#     datastore: vim.Datastore = select_from_objects(host.datastore, "Tempate Datastore")

#     vmdk = select_from_list(
#         title="Base OS Image (vmdk)",
#         list=[file_in_ds for file_in_ds in find_vmdks_in_datastore(datastore)],
#         name_generator=lambda x: "".join([x["folderPath"], x["file"].path]),
#     )

#     if vmdk is None:
#         fail("No template disk!")

#     vm_folder: vim.Folder = select_from_objects(
#         datacenter.vmFolder.childEntity, "VM Folder"
#     )
#     # Handle esxi - no vm_folder childEntity
#     if isinstance(vm_folder, vim.VirtualMachine):
#         vm_folder = datacenter.vmFolder

#     # Create template with "generic" host definition
#     ez_node = [node for node in ez_nodes if node["name"] == "generic"][0]

#     if "rhel" in vmdk["file"].path.lower():
#         vm_name = "rhel-template1"
#     else:
#         vm_name = "rocky-template1"

#     # resolve name conflict
#     all_vms = get_all_vms(vm_folder)

#     if vm_name in [vm.name for vm in all_vms]:
#         vm_name = re.sub(
#             "(\d+)(?!.*\d)",
#             lambda x: str(int(x.group(0)) + 1),
#             all_vms[-1].name,
#         )

#     print(f"Creating {vm_name}")
#     try:
#         vm = create_vm(
#             vm_folder=vm_folder,
#             vm_name=vm_name,
#             datastore=datastore,
#             host=host,
#             ez_node=ez_node,
#         )

#         if vm is not None:
#             if not add_scsi_controller(vm):
#                 fail(f"Failed at adding controller to {vm.name}")

#             # source_disk_path = f"{vmdk['folderPath']} {vmdk['file'].path}"
#             # os_disk_path = f"{vmdk['folderPath']} {vm_name}/{vm_name}.vmdk"

#             print(f"Adding disk... ", end="")

#             if not add_os_disk_to_vm(
#                 vm=vm,
#                 vmdk=vmdk,
#                 disk_sizeGB=ez_node["os_disk_size"],
#             ):
#                 fail(f"Failed a adding os disk to {vm.name}")

#             print(f"Adding vNIC... ", end="")

#             if not add_nic_on_network(vm=vm, network=network):
#                 fail(f"Failed at adding vNIC to VM {vm.name}")
#             print(network.name)

#             try:
#                 print("Convert to template.")
#                 vm.MarkAsTemplate()
#             except vmodl.fault.NotSupported:
#                 print("ignoring...")
#                 pass
#             yield vm_name
#         else:
#             fail(f"Failed to create {vm_name}")

#     except Exception as error:
#         print(f"failed at configuring {vm.name}")
#         fail(error)


# def find_vmdks_in_datastore(datastore):
#     spec = vim.host.DatastoreBrowser.SearchSpec(
#         sortFoldersFirst=True, query=[vim.host.DatastoreBrowser.VmDiskQuery()]
#     )
#     spec.searchCaseInsensitive = False
#     spec.matchPattern = ["*.vmdk"]
#     task = datastore.browser.SearchSubFolders(f"[{datastore.name}]", spec)
#     for res in wait_task_result(task):
#         for file in res.file:
#             yield {
#                 "datastore": res.datastore,
#                 "file": file,
#                 "folderPath": res.folderPath,
#             }


# def copy_file(content, datacenter, source, destination):
#     print(f"Copying {source} to {destination}... ", end="")

#     print(
#         wait_task_state(
#             content.fileManager.CopyFile(
#                 sourceName=source,
#                 sourceDatacenter=datacenter,
#                 destinationName=destination,
#                 destinationDatacenter=datacenter,
#             )
#         )
#     )


# def clone_vms(connection: vim.ServiceInstance, customisations: dict, nodes: list):
#     resources = get_resources(connection)

#     name_index = 0  # index for vm names
#     threads = list()

#     for ez_node in nodes:
#         for idx in range(ez_node["count"]):
#             name_index += 1
#             vm_ip = customisations["first_vm_ip"]
#             if vm_ip != "dhcp":
#                 # vm number starting at 1, ip index should start with 0
#                 vm_ip = str(
#                     ip_address(customisations["first_vm_ip"]) + (name_index - 1)
#                 )

#             # yield clone_vm(
#             #     vm_name=customisations["vmname"] + str(name_index),
#             #     vm_ip=vm_ip,
#             #     ez_node=ez_node,
#             #     resources=resources,
#             # )

#             task = ReturningThread(
#                 target=clone_vm,
#                 kwargs={
#                     "vm_name": customisations["vmname"] + str(name_index),
#                     "vm_ip": vm_ip,
#                     "ez_node": ez_node,
#                     "resources": resources,
#                 },
#             )
#             threads.append(task)

#     start_tasks_delayed(threads, 2)

#     return wait_tasks(threads)


# def clone_vm(vm_name: str, vm_ip: str, ez_node: dict, resources: dict):
#     """
#     Clone a VM from a template/VM

#     """

#     # datacenter: vim.Datacenter = resources["datacenter"]
#     datastore: vim.Datastore = resources["datastore"]
#     # network: vim.Network = resources["network"]
#     host: vim.HostSystem = resources["host"]
#     vm_folder: vim.Folder = resources["vm_folder"]
#     template_vm: vim.VirtualMachine = resources["template_vm"]

#     defaults = config.get()
#     # vm_netmask = defaults["NETWORK"]["vm_cidr"].split("/")[1]
#     vm_netmask = str(ip_network(defaults["NETWORK"]["vm_cidr"]).netmask)
#     vm_gateway = defaults["NETWORK"]["vm_gateway"]
#     vm_domain = defaults["NETWORK"]["vm_domain"]
#     vm_nameserver = defaults["NETWORK"]["vm_nameserver"]

#     # set relospec
#     relospec = vim.vm.RelocateSpec()
#     relospec.datastore = template_vm.datastore[0]
#     relospec.pool = host.parent.resourcePool

#     nic = vim.vm.device.VirtualDeviceSpec()
#     nic.operation = vim.vm.device.VirtualDeviceSpec.Operation.edit
#     nic.device = get_net_device(vm=template_vm)
#     nic.device.addressType = "assigned"
#     nic.device.connectable = vim.vm.device.VirtualDevice.ConnectInfo()
#     nic.device.connectable.startConnected = True
#     nic.device.connectable.allowGuestControl = True

#     guest_map = vim.vm.customization.AdapterMapping()
#     guest_map.adapter = vim.vm.customization.IPSettings()
#     if vm_ip == "dhcp":
#         guest_map.adapter.ip = vim.vm.customization.DhcpIpGenerator()
#     else:
#         guest_map.adapter.ip = vim.vm.customization.FixedIp()
#         guest_map.adapter.ip.ipAddress = vm_ip
#         guest_map.adapter.subnetMask = vm_netmask
#         guest_map.adapter.gateway = vm_gateway
#         guest_map.adapter.dnsDomain = vm_domain
#         guest_map.adapter.dnsServerList = [vm_nameserver]

#     # VM config spec
#     vmconf = new_vm_spec(
#         datastore=template_vm.datastore[0], ez_node=ez_node, name=vm_name
#     )
#     vmconf.deviceChange = [nic]

#     # DNS settings
#     globalip = vim.vm.customization.GlobalIPSettings()
#     globalip.dnsServerList = [vm_nameserver]
#     globalip.dnsSuffixList = [vm_domain]

#     # Hostname settings
#     # ident = vim.vm.customization.LinuxPrep()
#     # ident.domain = vm_domain
#     # ident.hostName = vim.vm.customization.FixedName()
#     # ident.hostName.name = vm_name
#     # ident.timeZone = "Europe/London"

#     cloudinit_spec = vim.vm.customization.CloudinitPrep()
#     ssh_pubkey = ""
#     with open(os.path.expanduser(defaults["CLOUDINIT"]["ssh_keyfile"])) as f:
#         ssh_pubkey = f.read()

#     password_hash = crypt.crypt(defaults["CLOUDINIT"]["vm_password"])

#     cloudinit_spec.userdata = get_userdata(
#         username=defaults["CLOUDINIT"]["vm_username"],
#         password=password_hash,
#         ssh_pubkey=ssh_pubkey,
#         vm_name=vm_name,
#         vm_domain=vm_domain,
#     )
#     # TODO: Handle dhcp assigned IP
#     cloudinit_spec.metadata = get_metadata(
#         vm_name=vm_name,
#         vm_ip=vm_ip,
#         vm_netmask=vm_netmask,
#         vm_gateway=vm_gateway,
#         vm_nameserver=vm_nameserver,
#         vm_domain=vm_domain,
#     )

#     print(cloudinit_spec)

#     customspec = vim.vm.customization.Specification()
#     customspec.nicSettingMap = [guest_map]
#     customspec.globalIPSettings = globalip
#     customspec.identity = cloudinit_spec

#     clonespec = vim.vm.CloneSpec()
#     clonespec.location = relospec
#     clonespec.config = vmconf
#     clonespec.customization = customspec
#     clonespec.powerOn = False
#     clonespec.template = False

#     print(clonespec)

#     print(f"{vm_name} cloning... ", end="")
#     try:
#         task = template_vm.Clone(folder=vm_folder, name=vm_name, spec=clonespec)
#         vm: vim.VirtualMachine = wait_task_result(task)
#         print("ok")
#     except vmodl.fault.NotSupported:
#         fail("esxi doesn't support vm clones, please use vcenter")

#     # add new disks /// assume no_of_disks are 0 or 1 or 2
#     if ez_node["no_of_disks"] > 0:
#         for i in range(ez_node["no_of_disks"]):
#             add_new_disk_to_vm(
#                 vm=vm, datastore=datastore, disk_size=ez_node["data_disk_size"]
#             )

#     # start vm
#     print(f"{vm.name} starting... ", end="")
#     print(wait_task_state(vm.PowerOn()))

#     # add to dns
#     if defaults["NETWORK"]["dns_api"] != "":
#         # assume technitium api url provided
#         # TODO: more integrations
#         result = technitium_add_record(hostname=vm_name, ip=vm_ip)
#         if isinstance(result, Response) and result.json()["status"] == "ok":
#             print(f"{vm.name} {vm_ip} added to dns")

#     if not wait_for_ssh(vm_ip):
#         fail(f"ssh failed for {vm_ip}")

#     # apply customisations to vm
#     print(f"{vm.name} configuring for {ez_node['product']}... ", end="")
#     if prepare_vm(
#         vm_name=vm.name,
#         vm_ip=vm_ip,
#         product_code=ez_node["product"],
#     ):
#         print(f"{vm_name} configured")

#     print("ok")

#     return vm.name, ez_node["product"]


# def create_vm(vm_folder: vim.Folder, vm_name, datastore, host, ez_node):
#     source_pool = host.parent.resourcePool
#     config = new_vm_spec(datastore=datastore, ez_node=ez_node, name=vm_name)
#     try:
#         task = vm_folder.CreateVm(config=config, pool=source_pool, host=host)
#         return wait_task_result(task=task)
#     except Exception as error:
#         fail(error)
#     return None


# def vms(vm_folder: vim.Folder):
#     return sorted(
#         [vm for vm in vm_folder.childEntity if isinstance(vm, vim.VirtualMachine)],
#         key=lambda x: x.name,
#     )


# def new_vm_spec(datastore, ez_node, name):
#     config = vim.vm.ConfigSpec()
#     config.annotation = f"Created by kayalab for {ez_node['name']} use"
#     config.memoryMB = int(ez_node["memGB"] * 1024)
#     config.guestId = "rhel8_64Guest"
#     config.name = name
#     config.numCPUs = ez_node["cores"]
#     config.cpuHotAddEnabled = True
#     config.memoryHotAddEnabled = True
#     files = vim.vm.FileInfo()
#     files.vmPathName = f"[{datastore.name}]"
#     config.files = files
#     return config


# def get_net_device(vm: vim.VirtualMachine):
#     nic_dev = None
#     for device in vm.config.hardware.device:
#         if isinstance(device, vim.vm.device.VirtualVmxnet3):
#             nic_dev = device

#     if nic_dev is None:
#         fail(f"Network device not found for {vm.config.name}")

#     return nic_dev


# def get_scsi_controller(vm: vim.VirtualMachine):
#     controller = None
#     for device in vm.config.hardware.device:
#         if isinstance(device, vim.vm.device.ParaVirtualSCSIController):
#             controller = device

#     if controller is None:
#         fail(f"PVSCSI Controller not found for {vm.config.name}")

#     return controller


# def add_new_disk_to_vm(
#     vm: vim.VirtualMachine, datastore: vim.Datastore, disk_size: int
# ):
#     """
#     Add new disk to vm
#     """
#     controller = get_scsi_controller(vm)

#     disk_sizeB = int(disk_size) * 1024 * 1024 * 1024
#     disk_number = len(controller.device)

#     disk_spec = vim.vm.device.VirtualDeviceSpec()
#     disk_spec.operation = vim.vm.device.VirtualDeviceSpec.Operation.add
#     disk_spec.device = vim.vm.device.VirtualDisk()
#     disk_spec.device.backing = vim.vm.device.VirtualDisk.SeSparseBackingInfo()
#     disk_spec.device.backing.diskMode = "persistent"
#     disk_spec.device.backing.datastore = datastore
#     disk_spec.device.backing.fileName = (
#         f"[{datastore.name}] {vm.name}/{vm.name}-{disk_number}.vmdk"
#     )
#     disk_spec.device.unitNumber = disk_number
#     disk_spec.device.controllerKey = controller.key
#     disk_spec.device.key = -1
#     disk_spec.device.capacityInBytes = disk_sizeB
#     disk_spec.fileOperation = "create"

#     print(f"{vm.name} add {disk_size}GB disk...", end="")
#     print(reconfigure_vm(vm, disk_spec))

#     return vm


# def add_os_disk_to_vm(vm: vim.VirtualMachine, vmdk, disk_sizeGB: int):
#     controller = get_scsi_controller(vm)

#     disk_spec = vim.vm.device.VirtualDeviceSpec()
#     disk_spec.operation = vim.vm.device.VirtualDeviceSpec.Operation.add
#     disk_spec.device = vim.vm.device.VirtualDisk()
#     disk_spec.device.deviceInfo = vim.Description(label="ez-os-template")
#     disk_spec.device.backing = vim.vm.device.VirtualDisk.FlatVer2BackingInfo()
#     disk_spec.device.backing.diskMode = (
#         vim.vm.device.VirtualDiskOption.DiskMode.persistent
#     )
#     # disk_spec.device.backing.thinProvisioned = True
#     # print(vmdk)
#     disk_spec.device.backing.fileName = f"{vmdk['folderPath']} {vmdk['file'].path}"

#     disk_spec.device.unitNumber = len(controller.device)
#     disk_spec.device.controllerKey = controller.key
#     # disk_spec.fileOperation = "create"

#     if reconfigure_vm(vm, disk_spec):
#         print(vmdk["file"].path)

#     # Resize OS disk
#     print("Resizing... ", end="")
#     disk_sizeB = int(disk_sizeGB) * 1024 * 1024 * 1024

#     vdisk = None
#     for device in vm.config.hardware.device:
#         if isinstance(device, vim.vm.device.VirtualDisk):
#             vdisk = device
#             break

#     disk_spec = vim.vm.device.VirtualDeviceSpec()
#     disk_spec.device = vdisk
#     disk_spec.operation = vim.vm.device.VirtualDeviceSpec.Operation.edit
#     disk_spec.device.capacityInBytes = disk_sizeB
#     if reconfigure_vm(vm, disk_spec):
#         print(f"{disk_sizeGB}GB")
#         return True

#     return False

# def confirm():
#     # dumb function
#     return True

# def delete_templates(si: vim.ServiceInstance):
#     content = si.RetrieveContent()
#     datacenter = select_from_objects(content.rootFolder.childEntity, "Data Center")

#     vmfolder = select_from_objects(datacenter.vmFolder.childEntity, "VM Folder")

#     vms = multiselect_from_list(
#         title="VMs",
#         list=[vm for vm in get_all_vms(vmfolder) if vm.config.template],
#         name_generator=lambda x: x.name,
#     )

#     if confirm(f"Are you sure to delete {[vm.name for vm in vms]}", default=False):
#         for vm in vms:
#             vm_name = vm.config.name
#             vm = typing.cast(vim.VirtualMachine, vm)
#             # disconnect template disk so it doesn't get deleted after last tempalte is deleted
#             print("Remove OS disk... ", end="")
#             if delete_os_disk_from_vm(vm):
#                 print(f"Destroy {vm.name}... ", end="")
#                 try:
#                     print(wait_task_state(vm.Destroy_Task()))
#                     yield vm_name
#                 except vim.fault.InvalidVmState as error:
#                     print(
#                         f"Failed to destroy {vm.name} with message: {error.faultMessage[0].message}"
#                     )

#     return None


# def delete_vms(si: vim.ServiceInstance):
#     content = si.RetrieveContent()
#     datacenter = select_from_objects(content.rootFolder.childEntity, "Data Center")

#     vmfolder = select_from_objects(datacenter.vmFolder.childEntity, "VM Folder")

#     vms = multiselect_from_list(
#         title="VMs",
#         list=[vm for vm in get_all_vms(vmfolder) if not vm.config.template],
#         name_generator=lambda x: x.name,
#     )

#     if len(vms) > 0 and confirm(
#         f"Are you sure to delete {[vm.name for vm in vms]}", default=False
#     ).ask(kbi_msg="Cancelled delete..."):
#         for vm in vms:
#             vm = typing.cast(vim.VirtualMachine, vm)
#             # capture name and ip for dns deletion
#             vm_name = vm.name
#             vm_ip = vm.summary.guest.ipAddress
#             if format(vm.runtime.powerState) == "poweredOn":
#                 print(f"Attempting to power off {vm.name}... ", end="")
#                 print(wait_task_state(vm.PowerOffVM_Task()))

#             print(f"Destroying {vm.name}... ", end="")
#             try:
#                 print(wait_task_state(vm.Destroy_Task()))
#                 if vm_ip:
#                     # remove from known_hosts
#                     subprocess.Popen(
#                         ["ssh-keygen", "-R", vm_ip],
#                         stdout=subprocess.DEVNULL,
#                         stderr=subprocess.DEVNULL,
#                     )
#                     subprocess.Popen(
#                         ["ssh-keygen", "-R", vm_name],
#                         stdout=subprocess.DEVNULL,
#                         stderr=subprocess.DEVNULL,
#                     )

#                     # remove from dns
#                     if config.get()["NETWORK"]["dns_api"] != "":
#                         result = technitium_delete_record(hostname=vm_name, ip=vm_ip)
#                         if (
#                             isinstance(result, Response)
#                             and result.json()["status"] == "ok"
#                         ):
#                             print(f"dns record deleted for {vm_name}")
#                         else:
#                             print(result.json())
#                 yield vm_name
#             except vim.fault.InvalidVmState as error:
#                 print(
#                     f"Failed to destroy {vm.name} with message: {error.faultMessage[0].message}"
#                 )

#     return None


# def delete_os_disk_from_vm(vm: vim.VirtualMachine):
#     os_disk = None
#     for dev in vm.config.hardware.device:
#         if (
#             isinstance(dev, vim.vm.device.VirtualDisk)
#             # and dev.deviceInfo.label == "ez-os-template"
#         ):
#             os_disk = dev
#     if os_disk is None:
#         fail(f"OS disk not found on {vm.name}")

#     # convert to vm first
#     # attach to the first host found for datastore
#     host: vim.HostSystem = os_disk.backing.datastore.host[0].key
#     try:
#         parent: vim.ComputeResource = host.parent
#         vm.MarkAsVirtualMachine(host=host, pool=parent.resourcePool)
#     except vmodl.fault.NotSupported:
#         print("ignoring...")
#         pass
#     disk_spec = vim.vm.device.VirtualDeviceSpec()
#     disk_spec.operation = vim.vm.device.VirtualDeviceSpec.Operation.remove
#     disk_spec.device = os_disk

#     if reconfigure_vm(vm, disk_spec):
#         print(os_disk.deviceInfo.label)
#         return True

#     return False


# def add_scsi_controller(vm):
#     controller_spec = vim.vm.device.VirtualDeviceSpec()
#     controller_spec.operation = vim.vm.device.VirtualDeviceSpec.Operation.add
#     controller_spec.device = vim.vm.device.ParaVirtualSCSIController()
#     controller_spec.device.deviceInfo = vim.Description()
#     controller_spec.device.slotInfo = vim.vm.device.VirtualDevice.PciBusSlotInfo()
#     controller_spec.device.hotAddRemove = True
#     controller_spec.device.sharedBus = "noSharing"

#     return reconfigure_vm(vm, controller_spec)


# def add_nic_on_network(vm, network: vim.Network):
#     nic_spec = vim.vm.device.VirtualDeviceSpec()
#     nic_spec.operation = vim.vm.device.VirtualDeviceSpec.Operation.add
#     nic_spec.device = vim.vm.device.VirtualVmxnet3()
#     nic_spec.device.deviceInfo = vim.Description()

#     if isinstance(network, vim.OpaqueNetwork):
#         nic_spec.device.backing = (
#             vim.vm.device.VirtualEthernetCard.OpaqueNetworkBackingInfo()
#         )
#         nic_spec.device.backing.opaqueNetworkType = network.summary.opaqueNetworkType
#         nic_spec.device.backing.opaqueNetworkId = network.summary.opaqueNetworkId
#     else:
#         nic_spec.device.backing = vim.vm.device.VirtualEthernetCard.NetworkBackingInfo()
#         nic_spec.device.backing.useAutoDetect = False
#         nic_spec.device.backing.deviceName = network.name

#     nic_spec.device.connectable = vim.vm.device.VirtualDevice.ConnectInfo()
#     nic_spec.device.connectable.startConnected = True
#     nic_spec.device.connectable.allowGuestControl = True
#     nic_spec.device.connectable.connected = False
#     nic_spec.device.connectable.status = "untried"
#     nic_spec.device.wakeOnLanEnabled = True
#     nic_spec.device.addressType = "generated"

#     return reconfigure_vm(vm, nic_spec)


# def reconfigure_vm(
#     vm: vim.VirtualMachine, device_spec: vim.vm.device.VirtualDeviceSpec
# ):
#     spec = vim.vm.ConfigSpec()
#     spec.deviceChange = [device_spec]
#     try:
#         return wait_task_state(vm.ReconfigVM_Task(spec=spec))
#     except Exception as error:
#         fail(error)


# def boot_from_cd(vm, iso_path):
#     cdspec = None
#     for device in vm.config.hardware.device:
#         if isinstance(device, vim.vm.device.VirtualCdrom):
#             cdspec = vim.vm.device.VirtualDeviceSpec()
#             cdspec.device = device
#             cdspec.operation = vim.vm.device.VirtualDeviceSpec.Operation.edit

#             cdspec.device.backing = vim.vm.device.VirtualCdrom.IsoBackingInfo()
#             for datastore in vm.datastore:
#                 cdspec.device.backing.datastore = datastore
#                 break
#             cdspec.device.backing.fileName = iso_path
#             cdspec.device.connectable = vim.vm.device.VirtualDevice.ConnectInfo()
#             cdspec.device.connectable.startConnected = True
#             cdspec.device.connectable.allowGuestControl = True

#     vmconf = vim.vm.ConfigSpec()
#     vmconf.deviceChange = [cdspec]
#     vmconf.bootOptions = vim.vm.BootOptions(
#         bootOrder=[vim.vm.BootOptions.BootableCdromDevice()]
#     )

#     task = vm.ReconfigVM_Task(vmconf)


# def get_userdata(
#     username,
#     password,
#     ssh_pubkey,
#     vm_name,
#     vm_domain,
# ):
#     return """
# #cloud-config
# hostname: {vm_name}
# fqdn: {vm_name}.{vm_domain}

# users:
#   - name: {username}
#     primary_group: {username}
#     passwd: {password}
#     shell: /bin/bash
#     sudo:  ALL=(ALL) NOPASSWD:ALL
#     groups: sudo, wheel
#     lock_passwd: false
#     ssh_authorized_keys:
#       - {ssh_pubkey}
# chpasswd:
#   expire: False

# package_upgrade: false
# """.format(
#         username=username,
#         password=password,
#         ssh_pubkey=ssh_pubkey,
#         vm_name=vm_name,
#         vm_domain=vm_domain,
#     )


# def get_metadata(
#     vm_name,
#     vm_ip,
#     vm_netmask,
#     vm_gateway,
#     vm_domain,
#     vm_nameserver,
# ):
#     return """instance-id: {vm_name}
# local-hostname: {vm_name}
# ssh_pwauth: true
# manage_resolv_conf: true
# network:
#   version: 1
#   config:
#     - type: physical
#       name: eth0
#       subnets:
#         - type: static
#           address: {vm_ip}
#           netmask: {vm_netmask}
#           gateway: {vm_gateway}
#     - type: nameserver
#       address:
#         - {vm_nameserver}
#       search:
#         - {vm_domain}
# """.format(
#         vm_name=vm_name,
#         vm_ip=vm_ip,
#         vm_netmask=vm_netmask,
#         vm_gateway=vm_gateway,
#         vm_domain=vm_domain,
#         vm_nameserver=vm_nameserver,
#     )
