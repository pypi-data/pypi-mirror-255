import os
import platform
from socket import gethostbyname
# from kubernetes import client as k8s_client, config as k8s_config
import yaml

from .parameters import *
from .utils import *

ez_cluster_name = "ezlab"

ezfab_yaml = os.path.abspath("ezfab.yaml")
orchestratorkubeconfig = os.path.abspath("ezfab-orchestrator-kubeconfig")
workloadkubeconfig = os.path.abspath("ezfab-workload-kubeconfig")
workloadcr = os.path.abspath("ezkf-workload-deploy-cr.yaml")
ezfabricctl = find_app("ezfabricctl")
ezfabrelease = os.path.abspath("ezfab-release.tgz")


def init_orchestrator(
    ip: str,
    ezfabrelease: str = ezfabrelease,
):
    """Install UA orchestrator

    Args:
        ip (str): orchestrator IP address
        ezfabrelease (str): full path to ezfab-release.tgz file
    """

    write_ezfabyaml(filename=ezfab_yaml, purpose="coordinator_init", orchestrator_ip=ip)

    if ezfabricctl is None:
        return f"ezfabricctl not found, check if you get ezfabricctl_{platform.system().lower()}_amd64 binary from the installer container and marked it as executable."


    if is_file(ezfabrelease):
        print("Starting coordinator deployment...")
        for out in execute(
            f"{ezfabricctl} o init -p {ezfabrelease} -i {ezfab_yaml} --save-kubeconfig {orchestratorkubeconfig}"
        ):
            print(out)
    else:
        return "Provide full path to ezfab-release.tgz file"


def add_hosts_to_pool(
    worker_ips: list[str],
    kubeconf: str = orchestratorkubeconfig,
):
    """Add hosts to UA pool

    Args:
        worker_ips (List(str)): hostname/IP address to add (can be provided multiple times)
        kubeconf (str): path to orchestrator kubeconfig
    """

    if ezfabricctl is None:
        return f"ezfabricctl not found, check if you get ezfabricctl_{platform.system().lower()}_amd64 binary from the installer container and marked it as executable."

    write_ezfabyaml(filename=ezfab_yaml, purpose="poolhost_init", workers=worker_ips)

    for out in execute(
        f"{ezfabricctl} ph init -i {ezfab_yaml} -c {os.path.abspath(kubeconf)}"
    ):
        print(out)


def create_workload_cluster(
    orchestrator_ip: str,
    kubeconf: str = orchestratorkubeconfig,
    cluster_name: str = ez_cluster_name,
):
    """Create UA workload cluster

    Args:
        orchestrator (str): controller IP address
        kubeconf (str): path to orchestrator kubeconfig
    """

    if ezfabricctl is None:
        return f"ezfabricctl not found, check if you get ezfabricctl_{platform.system().lower()}_amd64 binary from the installer container and marked it as executable."

    # use full path for the config file
    kubeconf = os.path.abspath(kubeconf)

    write_ezfabyaml(
        filename=ezfab_yaml,
        purpose="workload_init",
        orchestrator_ip=orchestrator_ip,
    )

    for out in execute(f"{ezfabricctl} workload init -i {ezfab_yaml} -c {kubeconf}"):
        print(out)

    # If the orchestrator is ready
    if is_file(kubeconf):
        # Save the workload kubeconfig
        for out in execute(
            f"{ezfabricctl} workload get kubeconfig -n {cluster_name} -c {kubeconf} --save-kubeconfig {workloadkubeconfig}"
        ):
            print(out)
        print(f"Workload kubeconfig saved as {workloadkubeconfig}")
    else:
        return f"Orchestrator kubeconfig file {kubeconf} not found!"


# def applyCr(
#     domain: str,
#     username: str,
#     password: str,
#     cluster_name: str = ez_cluster_name,
# ):
#     # Deploy the workload CR
#     k8s_config.load_kube_config(config_file=orchestratorkubeconfig)

#     # with open(workloadkubeconfig, "r") as f:
#     #     kubeconfig = toB64(f.read())

#     # k8s_config = {
#     #     "apiVersion": "v1",
#     #     "kind": "Secret",
#     #     "metadata": {
#     #         "name": "k8sconfig",
#     #         "namespace": cluster_name
#     #     },
#     #     "data": {
#     #         "kubeconfig": kubeconfig
#     #     }
#     # }

#     v1 = k8s_client.CoreV1Api()
#     secrets = v1.list_namespaced_secret(cluster_name)
#     if "authconfig" not in [secret.metadata.name for secret in secrets.items]:
#         admin = {
#             "admin_user": {
#                 "username": username,
#                 "fullname": "Ezlab Admin User",
#                 "email": f"{username}@{domain}",
#                 "password": password,
#             }
#         }
#         auth_config = {
#             "apiVersion": "v1",
#             "kind": "Secret",
#             "metadata": {"name": "authconfig", "namespace": cluster_name},
#             "data": {"internal_auth": toB64(str(admin))},
#         }
#         v1.create_namespaced_secret(cluster_name, body=auth_config)

#     api = k8s_client.CustomObjectsApi()

#     if cluster_name not in [
#         deployment["metadata"]["name"]
#         for deployment in getDeploymentCRs(api, cluster_name)
#     ]:
#         cr = api.create_namespaced_custom_object(
#             namespace=cluster_name,
#             group="ezkfops.hpe.ezkf-ops.com",
#             version="v1alpha1",
#             plural="ezkfworkloaddeploys",
#             body=get_ezkfcr_json(cluster_name=cluster_name),
#         )
#         if cluster_name in cr["metadata"]["name"]:
#             print(f"Deployment created for {cluster_name}")
#     else:
#         print(f"{cluster_name} exists, remove from EzkfWorkloadDeploy CR to retry")

#     return "This process doesn't work with the error: ERROR: in cluster_deploy - Error creating serializer: {'deployname': [ErrorDetail(string='This field may not be null.', code='null')], 'domainname': [ErrorDetail(string='This field may not be null.', code='null')], 'deployallapps': [ErrorDetail(string='This field may not be null.', code='null')], 'deployallinfra': [ErrorDeta..."


def remove(
    host: str,
    ezfabrelease: str = ezfabrelease,
    kubeconf: str = orchestratorkubeconfig,
):
    """Remove UA

    Args:
        host (str): hostname/IP address to destroy
    """

    if ezfabricctl is None:
        return f"ezfabricctl not found, check if you get ezfabricctl_{platform.system().lower()}_amd64 binary from the installer container and marked it as executable."

    write_ezfabyaml(
        filename=ezfab_yaml, purpose="coordinator_init", orchestrator_ip=host
    )

    if is_file(ezfabrelease):
        print("Destroying EZUA...")
        for out in execute(
            f"{ezfabricctl} o destroy --force -p {ezfabrelease} -i {ezfab_yaml} -c {os.path.abspath(kubeconf)}"
        ):
            print(out)
        print("Removing kubeconfig and cr files")
        for file in [orchestratorkubeconfig, workloadkubeconfig, ezfab_yaml]:
            if is_file(file):
                os.remove(file)
            else:
                print(f"{os.path.basename(file)} not found, skipping...")

    else:
        return "Provide full path to ezfab-release.tgz file"


def write_ezfabyaml(
    username: str,
    filename: str,
    purpose: str,
    orchestrator_ip: str = "",
    workers: list = [],
    cluster_name: str = ez_cluster_name,
) -> bool:
    """Generate yaml as input for ezfabctl
    TODO: should be using yaml module for proper yaml generation
    """

    response = False

    try:
        # Just in case hostname/fqdn is provided for orchestrator (we assume IP address for the rest)
        if not validate_ip(orchestrator_ip):
            try:
                orchestrator_ip = gethostbyname(orchestrator_ip)
            except Exception as error:
                return f"Cannot get host IP: {error}"

        # get private key from public key path, assuming private key file has the same name with public key without the .pub suffix
        ssh_prvkey = ""
        with open(os.path.abspath(os.path.expanduser(SSHKEYNAME)), "r") as f:
            ssh_prvkey = f.read()

        obj = {
            "defaultHostCredentials": {
                "sshUserName": username,
                "sshPrivateKey": toB64(ssh_prvkey),
            },
            "airgap": {
                "registryUrl": "lr1-bd-harbor-registry.mip.storage.hpecorp.net/develop/",
                "registryInsecure": True,
            },
            "hosts": [],
        }

        if purpose == "coordinator_init":
            obj["hosts"] = [{"host": orchestrator_ip}]

        elif purpose == "poolhost_init":
            for host in workers:
                obj["hosts"].append(
                    {
                        "host": host,
                        "labels": {
                            "role": "worker"
                            if workers.index(host) > 0
                            # first one is the control plane (K8s master)
                            else "controlplane"
                        },
                    }
                )

        elif purpose == "workload_init":
            obj["workload"] = {
                "deployEnv": "ezkube",
                "workloadType": "ezua",
                "clusterName": cluster_name,
                "resources": {"vcpu": 96},
                "controlplane": {"controlPlaneEndpoint": workers[0]},
                "controlPlaneHostLabels": {"role": "controlplane"},
                "workerHostLabels": {"role": "worker"},
            }

        with open(filename, "w") as f:
            f.write(yaml.safe_dump(obj))

    except Exception as error:
        print(error)
        response = False

    return response


# def getDeploymentCRs(
#     api: k8s_client.CustomObjectsApi, namespace: str = ez_cluster_name
# ):
#     crs = api.list_namespaced_custom_object(
#         namespace=namespace,
#         group="ezkfops.hpe.ezkf-ops.com",
#         version="v1alpha1",
#         plural="ezkfworkloaddeploys",
#     )
#     if crs is not None and len(crs) > 0:
#         _, deployments, _, _ = crs.values()
#     else:
#         deployments = []

#     return deployments


def get_ezkfcr_json(cluster_name: str = ez_cluster_name):
    """Generate yaml for EzkfWorkloadDeploy CR"""

    cr = {
        "apiVersion": "ezkfops.hpe.ezkf-ops.com/v1alpha1",
        "kind": "EzkfWorkloadDeploy",
        "metadata": {"name": cluster_name, "namespace": cluster_name},
        "spec": {
            "clustername": cluster_name,
            "deployallapps": True,
            "deployallinfra": True,
            "deployenv": "ezkube",
            "deploytarget": "pph",
            "domainname": "testdom.com",
            "workloadtype": "ezua",
            "authconfig": {"secret_name": "authconfig"},
        },
    }
    # "k8sconfig": { "secret_name": "k8sconfig" },
    # "tlsconfig":{ "secret_name": "tlsconfig" },
    # TODO: Not sure if this is needed or works
    # if vm_proxy != "":
    #     cr["spec"]["proxy"] = {
    #         "httpProxy": vm_proxy,
    #         "httpsProxy": vm_proxy,
    #         "noProxy": get_proxy_environment().split("no_proxy=")[1],
    #     }

    # # TODO: Not tested
    # if "airgap_registry" in defaults["NETWORK"]:
    #     cr["spec"]["airgap"] = {
    #         "secret_name": "airgap",
    #         "registryUrl": {defaults["NETWORK"]["airgap_registry"]},
    #         "registryInsecure": {
    #             "true"
    #             if defaults["NETWORK"]["airgap_registry"].split("://")[0] == "http"
    #             else "false"
    #         },
    #     }

    return cr


# Will be available on FY24-Q1 release
def precheck():
    """Fabric pre-checks for roles"""

    payload = """
defaultHostCredentials:
  sshUserName: "user"
  sshPassword: "base64encode password"
prechecks:
  coordinator:
    controlplane:
    - host: "IP address or FQDN"
      #hostCredentials: {} # per-host credentials, same format as defaultHostCredentials
      #hostSudoPrefix: "" # per-host sudo prefix
  ua:
    controlplane:
    - host: "IP address or FQDN"
    worker:
    - host: "IP address or FQDN"
    - host: "IP address or FQDN"
"""


def install(
    orchestrator_ip: str,
    workers: 
        list[str],
):
    init_orchestrator(ip=orchestrator_ip)
    add_hosts_to_pool(worker_ips=workers)
    create_workload_cluster(orchestrator_ip=orchestrator_ip)
