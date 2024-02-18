# Ezlab UI

UI to create virtual machines and install HPE Ezmeral products.

## Usage

It supports install operations for Virtual Machines on Proxmox VE.
Libvirt/KVM and VMware might come too.

### Prepare Templates

Download base cloud images for template creation.

Tested images can be found at:
Rocky8:
`https://download.rockylinux.org/pub/rocky/8/images/x86_64/Rocky-8-GenericCloud.latest.x86_64.qcow2`

RHEL8 (login required):
`https://access.cdn.redhat.com/content/origin/files/sha256/5f/5f9cd94d9a9a44ac448b434f3e28d24465deef089bbd452392b3f10e96cb8eaa/rhel-8.8-x86_64-kvm.qcow2`

#### Vmware

THIS IS NOT WORKING YET/AGAIN!!!

Install required package

`virt-customize -a Rocky-8-GenericCloud.latest.x86_64.qcow2 --install open-vm-tools`
Convert qcow2 image

`qemu-img convert -f qcow2 -O vmdk -o subformat=streamOptimized Rocky-8-GenericCloud.latest.x86_64.qcow2 Rocky-8-GenericCloud.latest.x86_64.img`

Enable SSH for the ESX host
vCenter - Host - Configure - Services - SSH -> Start

Copy image to a datastore (change your host name and datastore path)
`scp Rocky-8-GenericCloud.latest.x86_64.img root@<esx.host>:/vmfs/volumes/<datastore>`

Login to the esx host (change your host name)
`ssh root@<esx.host>`

Convert image to disk
`vmkfstools -i Rocky-8-GenericCloud.latest.x86_64.img rocky-template.vmdk -W file -d thin -N`

#### Proxmox VE

Copy qcow2 base image file(s) into /var/lib/vz/template/qemu folder (create the qemu folder first)

### Configure Utility

Use Settings menu to save environment details. Use placeholder text to see correct/expected format.

Leave empty if not used (ie, proxy, local repository...)

### VMs Menu

Login to hypervisor (currently only ProxmoxVE)

New VM:

Select correct template, if bridge name doesn't pop up, close the dialog (`ESC`) and re-open.

Select the pre-defined configuration:

    UA Control Plane    | 2 VMs | 4 cores | 32GB Memory
    UA Workers          | 3 VMs | 32 cores | 128GB Memory
    DF Single Node      | 1 VM | 16 cores | 64GB Memory
    DF 5-Node Cluster   | 5 VMs | 16 cores | 32GB Memory
    Generic (Client)    | 1 VM | 2 cores | 4GB Memory

### Ezmeral Menu

Only Data Fabric for now. 

#### Install Ezmeral Data Fabric

Version 7.6 with EEP 9.2.1 will be installed on as many hosts provided. Installer will be installed on the first node and system will automatically distribute services across other nodes. Single node installation is also possible. 

Core components (fileserver, DB, Kafka/Streams, s3server, Drill, HBase, Hive) and monitoring tools (Grafana, OpenTSDB...) will be installed. Subject to change to optimize installation time & complexity.

##### Configure Step

Prepare for Data Fabric installation.

Add nodes to prepare multiple nodes.

##### Install Step

Create Data Fabric cluster on as many nodes as given.

##### Cross-Cluster Step

Will be working soon!

##### Connect Step

Will download secure files from the server and install/configure the client for the cluster.

## NOTES

If API servers (ProxmoxVE and/or vSphere) are using self-signed certificates, insecure connection warnings will mess up your screen. You can avoid this using environment variable (this is not recommended due to security concerns):

`export PYTHONWARNINGS="ignore:Unverified HTTPS request"`

## TODO

[ ] Proper documentation and code clean up

[ ] Test on standalone ESX host

[ ] Test airgap
