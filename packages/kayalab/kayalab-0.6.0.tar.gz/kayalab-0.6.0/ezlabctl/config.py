import configparser
from typing import Annotated
from questionary import password, text, path as qpath
from rich import print

import typer

from .parameters import ini_file

app = typer.Typer(add_completion=True, no_args_is_help=True)

config = configparser.ConfigParser()

config_keys = [
    {
        "title": "VM Network CIDR",
        "section": "NETWORK",
        "key": "vm_cidr",
        "default": "192.168.0.0/24",
        "type": text,
    },
    {
        "title": "VM Network Gateway",
        "section": "NETWORK",
        "key": "vm_gateway",
        "default": "192.168.0.1",
        "type": text,
    },
    {
        "title": "VM DNS Server",
        "section": "NETWORK",
        "key": "vm_nameserver",
        "default": "192.168.0.1",
        "type": text,
    },
    {
        "title": "VM DNS Domain",
        "section": "NETWORK",
        "key": "vm_domain",
        "default": "ez.lab",
        "type": text,
    },
    {
        "title": "DNS API",
        "section": "NETWORK",
        "key": "dns_api",
        "default": "",
        "type": text,
    },
    {
        "title": "PROXY",
        "section": "NETWORK",
        "key": "proxy",
        "default": "",
        "type": text,
    },
    {
        "title": "YUM_PROXY",
        "section": "NETWORK",
        "key": "yum_proxy",
        "default": "",
        "type": text,
    },
    {
        "title": "MAPR_REPO",
        "section": "NETWORK",
        "key": "mapr_repo",
        "default": "",
        "type": text,
    },
    {
        "title": "VM admin username",
        "section": "CLOUDINIT",
        "key": "vm_username",
        "default": "ezmeral",
        "type": text,
    },
    {
        "title": "VM admin password",
        "section": "CLOUDINIT",
        "key": "vm_password",
        "default": "",
        "type": password,
    },
    {
        "title": "SSH Public Key path",
        "section": "CLOUDINIT",
        "key": "ssh_keyfile",
        "default": "~/.ssh/id_rsa.pub",
        "type": qpath,
    },
    {
        "title": "Rocky Base Image",
        "section": "CLOUDIMG",
        "key": "rocky",
        "default": "Rocky-8-GenericCloud.latest.x86_64.qcow2",
        "type": text,
    },
    {
        "title": "RHEL8 Base Image",
        "section": "CLOUDIMG",
        "key": "rhel",
        "default": "rhel-8.8-cloudvm-qemu.qcow2",
        "type": text,
    },
]


def key_default(key):
    """
    Returns the existing or default value for the key
    """
    return (
        config[key["section"]][key["key"]]
        if config.has_option(key["section"], key["key"])
        else key["default"]
    )


@app.command()
def set():
    config.read(ini_file)
    print(f"using {ini_file}")

    # pre-populate config if values are missing
    if "NETWORK" not in config.sections():
        config.add_section("NETWORK")
    if "CLOUDINIT" not in config.sections():
        config.add_section("CLOUDINIT")
    if "CLOUDIMG" not in config.sections():
        config.add_section("CLOUDIMG")

    try:
        for key in config_keys:
            config[key["section"]][key["key"]] = key["type"](
                key["title"],
                default=key_default(key),
            ).ask(kbi_msg=f"Reverting to default {key_default(key)}") or key_default(
                key
            )
            # add trailing slash for mapr_repo
            if key["key"] == "mapr_repo":
                if not config[key["section"]]["mapr_repo"].endswith("/"):
                    config[key["section"]]["mapr_repo"] += "/"
            # remove trailing slash from yum_repo
            elif key["key"] == "yum_proxy":
                if config[key["section"]]["yum_proxy"].endswith("/"):
                    config[key["section"]]["yum_proxy"] = config[key["section"]]["yum_proxy"].rstrip("/")

    except TypeError as error:
        print(error)
        print("Incorrect entry for settings")
        exit(1)

    with open(ini_file, "w") as configfile:
        config.write(configfile)


@app.command()
def get(
    out: Annotated[bool, typer.Option("--print", "-p", help="Print the config")] = False
):
    config.read(ini_file)
    dictionary = {s: dict(config.items(s)) for s in config.sections()}
    # check if all settings are provided

    if out:
        print(dictionary)
    return dictionary
