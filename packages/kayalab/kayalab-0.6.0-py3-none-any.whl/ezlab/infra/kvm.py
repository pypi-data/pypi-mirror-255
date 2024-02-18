# import subprocess
# from libvirt import *
# from xml.dom import minidom


# def connect(host: str, username: str):
#     conn = open(f"qemu+ssh://{username}@{host}/system")
#     if not conn:
#         raise SystemExit("Failed to open connection to qemu:///system")

#     # caps = conn.getCapabilities()  # caps will be a string of XML
#     # print("Capabilities:\n" + caps)
#     return conn


# def vm(conn: virConnect, id):
#     dom: virDomain = conn.lookupByID(id)
#     if not dom:
#         raise SystemExit("Failed to find domain ID 5")

#     raw_xml = dom.XMLDesc()
#     xml = minidom.parseString(raw_xml)
#     domainTypes = xml.getElementsByTagName("type")
#     for domainType in domainTypes:
#         print(domainType.getAttribute("machine"))
#         print(domainType.getAttribute("arch"))


# def disks(dom: virDomain):
#     raw_xml = dom.XMLDesc()

#     xml = minidom.parseString(raw_xml)

#     diskTypes = xml.getElementsByTagName("disk")
#     for diskType in diskTypes:
#         print(
#             "disk: type="
#             + diskType.getAttribute("type")
#             + " device="
#             + diskType.getAttribute("device")
#         )
#         diskNodes = diskType.childNodes
#         for diskNode in diskNodes:
#             if diskNode.nodeName[0:1] != "#":
#                 print("  " + diskNode.nodeName)
#                 for attr in diskNode.attributes.keys():
#                     print(
#                         "    "
#                         + diskNode.attributes[attr].name
#                         + " = "
#                         + diskNode.attributes[attr].value
#                     )


# def networks(dom):
#     raw_xml = dom.XMLDesc()
#     xml = minidom.parseString(raw_xml)

#     interfaceTypes = xml.getElementsByTagName("interface")
#     for interfaceType in interfaceTypes:
#         print("interface: type=" + interfaceType.getAttribute("type"))
#         interfaceNodes = interfaceType.childNodes
#         for interfaceNode in interfaceNodes:
#             if interfaceNode.nodeName[0:1] != "#":
#                 print("  " + interfaceNode.nodeName)
#                 for attr in interfaceNode.attributes.keys():
#                     print(
#                         "    "
#                         + interfaceNode.attributes[attr].name
#                         + " = "
#                         + interfaceNode.attributes[attr].value
#                     )


# def pools(conn: virConnect):
#     pools = conn.listAllStoragePools()
#     if not pools:
#         return list()
#         # raise SystemExit("Failed to locate any StoragePool objects.")

#     return [pool.name() for pool in pools if pool.isActive() == True]


# def newdisk(conn:virConnect):
#     stgvol_xml = """
#     <volume>
#     <name>sparse.img</name>
#     <allocation>0</allocation>
#     <capacity unit="G">2</capacity>
#     <target>
#         <path>/var/lib/libvirt/images/sparse.img</path>
#         <permissions>
#         <owner>107</owner>
#         <group>107</group>
#         <mode>0744</mode>
#         <label>virt_image_t</label>
#         </permissions>
#     </target>
#     </volume>"""

#     pool = "default"

#     pool = conn.storagePoolLookupByName(pool)
#     if not pool:
#         raise SystemExit("Failed to locate any StoragePool objects.")

#     stgvol = pool.createXML(stgvol_xml, 0)
#     if not stgvol:
#         raise SystemExit("Failed to create a  StorageVol objects.")

#     # remove the storage volume
#     # physically remove the storage volume from the underlying disk media
#     stgvol.wipe()
#     # logically remove the storage volume from the storage pool
#     stgvol.delete()


# def clonedisk(conn:virConnect):
#     stgvol_xml = """
#     <volume>
#         <name>sparse.img</name>
#         <allocation>0</allocation>
#         <capacity unit="G">2</capacity>
#         <target>
#             <path>/var/lib/libvirt/images/sparse.img</path>
#             <permissions>
#                 <owner>107</owner>
#                 <group>107</group>
#                 <mode>0744</mode>
#                 <label>virt_image_t</label>
#             </permissions>
#         </target>
#     </volume>"""

#     stgvol_xml2 = """
#     <volume>
#         <name>sparse2.img</name>
#         <allocation>0</allocation>
#         <capacity unit="G">2</capacity>
#         <target>
#             <path>/var/lib/libvirt/images/sparse.img</path>
#             <permissions>
#                 <owner>107</owner>
#                 <group>107</group>
#                 <mode>0744</mode>
#                 <label>virt_image_t</label>
#             </permissions>
#         </target>
#     </volume>"""

#     pool = conn.storagePoolLookupByName(pool)

#     if not pool:
#         raise SystemExit("Failed to locate any StoragePool objects.")

#     # create a new storage volume
#     stgvol = pool.createXML(stgvol_xml, 0)
#     if not stgvol:
#         raise SystemExit("Failed to create a  StorageVol object.")

#     # now clone the existing storage volume
#     print("This could take some time...")
#     stgvol2 = pool.createXMLFrom(stgvol_xml2, stgvol, 0)
#     if not stgvol2:
#         raise SystemExit("Failed to clone a  StorageVol object.")

#     stgvol2.wipe()
#     stgvol2.delete()

#     stgvol.wipe()
#     stgvol.delete()


# def newvm(conn:virConnect):
#     xmlconfig = """
# <domain type="kvm">
#   <name>demo</name>
#   <uuid>c7a5fdbd-cdaf-9455-926a-d65c16db1809</uuid>
#   <memory>500000</memory>
#   <vcpu>1</vcpu>

#   <os>
#     <type arch="x86_64" machine="pc">hvm</type>
#     <boot dev="hd"/>
#     <boot dev="cdrom"/>
#   </os>

#   <clock offset="utc"/>
#   <on_poweroff>destroy</on_poweroff>
#   <on_reboot>restart</on_reboot>
#   <on_crash>destroy</on_crash>
#   <devices>
#     <emulator>/usr/bin/qemu-kvm</emulator>
#     <disk type="file" device="cdrom">
#       <source file="/var/lib/libvirt/images/rhel5-x86_64-dvd.iso"/>
#       <target dev="hdc" bus="ide"/>
#     </disk>

#     <disk type="file" device="disk">
#       <source file="/var/lib/libvirt/images/demo.img"/>
#       <driver name="qemu" type="raw"/>
#       <target dev="hda"/>
#     </disk>
#     <interface type="bridge">
#       <mac address="52:54:00:d8:65:c9"/>
#       <source bridge="br0"/>
#     </interface>
#     <input type="mouse" bus="ps2"/>
#     <graphics type="vnc" port="-1" listen="127.0.0.1"/>
#   </devices>
# </domain>
# """
#     dom = conn.defineXML(xmlconfig)

#     if not dom:
#         raise SystemExit("Failed to define a domain from an XML definition")

#     if dom.create(dom) < 0:
#         raise SystemExit("Can not boot guest domain")

#     dom.setAutostart(1)  # enable autostart

#     print("Guest " + dom.name() + " has booted")

# def qemu_img_create(file_path, fmt="qcow2", size=None, backing_file=None):
#     cmd = ["qemu-img", "create", "-f", fmt]
#     if backing_file:
#         cmd.extend(["-b", backing_file])
#     cmd.append(file_path)
#     if size:
#         cmd.append(size)
#     subprocess.check_call(cmd)
    
# def build_domain(conn: virConnect, base_img, top_layer):
#     xmlconfig = """
# <domain type="kvm">
#   <name>demo</name>
#   <uuid>c7a5fdbd-cdaf-9455-926a-d65c16db1809</uuid>
#   <memory>500000</memory>
#   <vcpu>1</vcpu>

#   <os>
#     <type arch="x86_64" machine="pc">hvm</type>
#     <boot dev="hd"/>
#     <boot dev="cdrom"/>
#   </os>

#   <clock offset="utc"/>
#   <on_poweroff>destroy</on_poweroff>
#   <on_reboot>restart</on_reboot>
#   <on_crash>destroy</on_crash>
#   <devices>
#     <emulator>/usr/bin/qemu-kvm</emulator>
#     <disk type="file" device="cdrom">
#       <source file="/var/lib/libvirt/images/rhel5-x86_64-dvd.iso"/>
#       <target dev="hdc" bus="ide"/>
#     </disk>

#     <disk type="file" device="disk">
#       <source file="/var/lib/libvirt/images/demo.img"/>
#       <driver name="qemu" type="raw"/>
#       <target dev="hda"/>
#     </disk>
#     <interface type="bridge">
#       <mac address="52:54:00:d8:65:c9"/>
#       <source bridge="br0"/>
#     </interface>
#     <input type="mouse" bus="ps2"/>
#     <graphics type="vnc" port="-1" listen="127.0.0.1"/>
#   </devices>
# </domain>
# """

#     qemu_img_create(base_img, size="100M")
#     qemu_img_create(top_layer, backing_file=base_img)
#     dom = conn.createXML(xmlconfig.format(disk_img=top_layer), 0)
#     return dom



# # conn = connect("10.1.1.5", "ezmeral")

# # pool = pools(conn).pop()

# # print(pool)

# # conn.close()

