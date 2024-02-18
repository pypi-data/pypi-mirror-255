"""

:author: Jonathan Decker
"""

import json
import logging

import requests
import urllib3
from requests.sessions import CaseInsensitiveDict, Session

from ironik.config_file_handler.deploy_template import (KubernetesConfig,
                                                        NetworkConfig,
                                                        OpenStackConfig,
                                                        OpenStackCredentials,
                                                        RancherConfig,
                                                        RancherCredentials)
from ironik.util import exceptions

logger = logging.getLogger("logger")


def create_rancher_session(rancher_access_key: str, rancher_secret_key: str, disable_verify: bool = True) -> Session:
    """
    Creates a requests Session used to access Rancher API.
    This needs to be forwarded to any function making API calls to Rancher.
    SSL verification is disabled by default as the test server does not have a valid ssl certificate.
    :param rancher_access_key:
    :param rancher_secret_key:
    :param disable_verify: Determines whether ssl verification and warnings should be disabled.
    :type disable_verify: bool
    :return: A Session object used to make API calls to Rancher.
    :rtype: requests.Session
    """
    session = Session()

    session.auth = (rancher_access_key, rancher_secret_key)
    if disable_verify:
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        session.verify = False
    session.headers = CaseInsensitiveDict({"accept": "application/json", "content-Type": "application/json"})
    logger.debug("Created Rancher session.")
    return session


def verify_rancher_token(session: Session, base_url: str) -> bool:
    """
    Verifies whether a Rancher token is valid by trying to get the given base url using the given Session object.
    Returns True if everything is fine and False if either the token is invalid or the url is unreachable.
    :param session: A Session object initialized by create_rancher_session.
    :type session: requests.Session
    :param base_url: Base url of the Rancher API, should be the URL of the Rancher server with /v3 attached to it.
    :type base_url: str
    :return: True if the token is valid and false if either the token is invalid or the url is unreachable.
    :rtype: bool
    """
    try:
        response = session.get(base_url)
    except requests.exceptions.ConnectionError as exception:
        logger.error(f"Cannot reach Rancher API at {base_url}")
        logger.debug(f"Got error: {exception}")
        return False
    if response.status_code == 401:
        logger.error(
            f"Authentication with Rancher API failed for {base_url},"
            f" please confirm that the Rancher API Token is valid and unscoped."
        )
        return False
    logger.debug(f"Request to {base_url}, received {response.status_code}")
    return True


def create_and_test_rancher_session(
    rancher_credentials: RancherCredentials, rancher_config: RancherConfig
) -> requests.Session:
    """
    Calls create rancher session and communicates possible errors.
    :param rancher_config:
    :param rancher_credentials:
    :return: Returns a requests Session which is configured to authenticate with rancher
    or None if the session is not valid.
    :rtype: requests.Session or None
    """
    session = create_rancher_session(rancher_credentials.rancher_access_key, rancher_credentials.rancher_secret_key)
    if not verify_rancher_token(session, rancher_config.rancher_api_base_url):
        raise exceptions.IronikFatalError(
            f"Rancher token verification failed. Could not access the Rancher API with"
            f" the given token under {rancher_config.rancher_api_base_url}.\n"
            f"Please verify that the Token is unscoped and valid for the Rancher"
            f" server under the given url."
        )
    logger.debug("Rancher token and url are valid.")
    return session


def create_rancher_node_template(
    session: Session,
    openstack_credentials: OpenStackCredentials,
    openstack_config: OpenStackConfig,
    rancher_config: RancherConfig,
    template_name: str,
) -> str:
    """
    Queries rancher API to create a new node template based on the given instructions
    and returns the id of the template.
    :param rancher_config:
    :param openstack_config:
    :param openstack_credentials:
    :param session: A Session object initialized by create_rancher_session.
    :type session: requests.Session
    :param template_name: The name of the template in rancher.
    :type template_name: str
    :return: Id of the node template created in rancher.
    :rtype: str
    """
    data = {  # "amazonec2Config": None,
        # "azureConfig": None,
        # "digitaloceanConfig": None,
        # "engineInsecureRegistry": [],
        # "engineRegistryMirror": [],
        "engineInstallURL": f"{rancher_config.engine_install_url}",
        # "linodeConfig": None,
        "name": f"{template_name}",
        # "nodeTaints": [],
        "openstackConfig": {
            # "activeTimeout": "200",
            "authUrl": f"{openstack_config.openstack_auth_url}",
            "bootFromVolume": True,  # This flag only works for Compute API microversion 2.67 onwards, see rancher-machine source code
            # "configDrive": False,
            "domainName": f"{openstack_config.user_domain_name}",
            "endpointType": "publicURL",
            "flavorName": f"{openstack_config.default_flavor_name}",
            "imageName": f"{openstack_config.default_image_name}",
            "insecure": False,
            "ipVersion": "4",
            "netId": f"{openstack_config.private_network_id}",
            "novaNetwork": False,
            "region": f"{openstack_config.region_name}",
            "secGroups": f"{openstack_config.security_group_name}",
            "sshPort": "22",
            "sshUser": f"{rancher_config.ssh_user}",
            "tenantDomainName": f"{openstack_config.project_domain_name}",
            "tenantId": f"{openstack_credentials.project_id}",
            "username": f"{openstack_credentials.username}",
            "password": f"{openstack_credentials.password}",
            "volumeName": f"{template_name}-volume",
            "volumeSize": f"{str(openstack_config.volume_size)}",
            # "volumeType": f"{openstack_config.volume_type}",
        },
        # "vmwarevsphereConfig": None
    }
    data_json = json.dumps(data)
    response = session.post(rancher_config.rancher_api_base_url + "/nodetemplates", data=data_json)
    logger.debug(f"Received response with code {response.status_code}")
    if not 200 <= response.status_code <= 299:
        raise exceptions.IronikFatalError(
            f"Node template creation failed with status {response.status_code}\n" f"{response.text}"
        )

    node_template_dict = json.loads(response.text)
    return node_template_dict.get("id")


def get_rancher_kubernetes_engine_config(kubernetes_config: KubernetesConfig, network_config: NetworkConfig) -> dict:
    """

    Args:
        kubernetes_config:
        network_config:

    Returns:

    """
    rancher_kubernetes_engine_config = {
        "addonJobTimeout": 30,
        "authentication": {"strategy": "x509|webhook"},
        "authorization": {},
        "bastionHost": {"sshAgentAuth": False},
        "dns": {"nodelocal": {"ipAddress": "", "nodeSelector": None, "updateStrategy": {}}},
        "ignoreDockerVersion": True,
        "cloudProvider": {"name": "external"},
        #
        # # Currently only nginx ingress provider is supported.
        # # To disable ingress controller, set `provider: none`
        # # To enable ingress on specific nodes, use the node_selector, eg:
        #    provider: nginx
        #    node_selector:
        #      app: ingress
        #
        "ingress": {"provider": "nginx"},
        "kubernetesVersion": f"{kubernetes_config.version}",
        "monitoring": {"provider": "metrics-server", "replicas": 1},
        # # To specify flannel interface
        #
        #    network:
        #      plugin: flannel
        #      flannel_network_provider:
        #      iface: eth1
        #
        # # To specify flannel interface for canal plugin
        #
        #    network:
        #      plugin: canal
        #      canal_network_provider:
        #        iface: eth1
        #
        "network": {"mtu": 0, "options": {"flannelBackendType": "vxlan"}, "plugin": "canal"},
        #
        #    services:
        #      kube-api:
        #        service_cluster_ip_range: 10.43.0.0/16
        #      kube-controller:
        #        cluster_cidr: 10.42.0.0/16
        #        service_cluster_ip_range: 10.43.0.0/16
        #      kubelet:
        #        cluster_domain: cluster.local
        #        cluster_dns_server: 10.43.0.10
        #
        "services": {
            "etcd": {
                "backupConfig": {"enabled": True, "intervalHours": 12, "retention": 6, "safeTimestamp": False},
                "creation": "12h",
                "extraArgs": {"election-timeout": 5000, "heartbeat-interval": 500},
                "gid": 0,
                "retention": "72h",
                "snapshot": False,
                "uid": 0,
            },
            "kubeApi": {
                "alwaysPullImages": False,
                "podSecurityPolicy": False,
                "serviceNodePortRange": f"{network_config.worker_port_range_min}-{network_config.worker_port_range_max}",
            },
        },
        "sshAgentAuth": False,
        "upgradeStrategy": {
            "drain": False,
            "maxUnavailableControlplane": "1",
            "maxUnavailableWorker": "10%",
            "nodeDrainInput": {
                "deleteLocalData": False,
                "force": False,
                "gracePeriod": -1,
                "ignoreDaemonSets": True,
                "timeout": 120,
            },
        },
    }

    return rancher_kubernetes_engine_config


def get_rke_template(kubernetes_config: KubernetesConfig, network_config: NetworkConfig) -> dict:
    """

    :param kubernetes_config:
    :param network_config:
    :return:
    """
    # The Rancher API spec demands camel case and refuses to use snake case,
    # even if the options are later parsed as snake case

    rancher_kubernetes_engine_config = get_rancher_kubernetes_engine_config(kubernetes_config, network_config)

    rke_template = {
        "answers": {},
        "dockerRootDir": "/var/lib/docker",
        "enableClusterAlerting": False,
        "enableClusterMonitoring": False,
        "enableNetworkPolicy": False,
        "localClusterAuthEndpoint": {"enabled": True},
        "rancherKubernetesEngineConfig": rancher_kubernetes_engine_config,
        "windowsPreferedCluster": False,
    }

    return rke_template


def create_rancher_cluster(
    session: Session, rancher_config: RancherConfig, cluster_name: str, iso_time_stamp: str, rke_config: dict
) -> str:
    """
    Makes an API call to rancher to create a new cluster using the given parameters.
    :param rancher_config:
    :param session: A Session object initialized by create_rancher_session.
    :type session: requests.Session
    :param cluster_name: The name for the cluster in Rancher.
    :type cluster_name: str
    :param iso_time_stamp: Iso time stamp which is written to the description of the new cluster.
    :type iso_time_stamp: str
    :param rke_config: Rancher kubernetes engine configuration as produced by rke template.
    :type rke_config: dict
    :return: The id of the new cluster in rancher.
    :rtype: str
    """
    data = {
        "amazonElasticContainerServiceConfig": None,
        "nodeAnnotations": {"lifecycle.cattle.io/create.cluster-provisioner-controller": True},
        "answers": None,
        "azureKubernetesServiceConfig": None,
        "clusterTemplateRevisionId": None,
        "defaultClusterRoleForProjectMembers": "",
        "defaultPodSecurityPolicyTemplateId": "",
        "description": f"Cluster created on {iso_time_stamp}",
        "dockerRootDir": "/var/lib/docker",
        "eksConfig": None,
        "enableClusterAlerting": False,
        "enableClusterMonitoring": False,
        "googleKubernetesEngineConfig": None,
        "k3sConfig": None,
        "name": f"{cluster_name}",
        "rancherKubernetesEngineConfig": rke_config,  # rancher_kubernetes_engine_config
        "rke2Config": None,
        "scheduledClusterScan": None,
        "windows_prefered_cluster": False,
    }
    data_json = json.dumps(data)
    response = session.post(rancher_config.rancher_api_base_url + "/clusters", data=data_json)
    logger.debug(f"Received response with code {response.status_code}")
    if not 200 <= response.status_code <= 299:
        raise exceptions.IronikFatalError(
            f"Cluster creation failed with status {response.status_code}" f"\n{response.text}"
        )

    cluster_dict = json.loads(response.text)
    return cluster_dict.get("id")


def create_rancher_node_pool(
    session: Session,
    cluster_name: str,
    cluster_id: str,
    node_template_id: str,
    is_master: bool,
    kubernetes_config: KubernetesConfig,
    rancher_config: RancherConfig,
) -> str:
    """
    Makes an API call the rancher API to create a new node pool for the given cluster with the given node template.
    Quantity of 0 will be accepted but the new node pool will not show up in the UI.
    :param rancher_config:
    :param kubernetes_config:
    :param cluster_name: Name of the cluster, used to prefix the name of the nodes.
    :type cluster_name: str
    :param session: A Session object initialized by create_rancher_session.
    :type session: requests.Session
    :param cluster_id: Id of the cluster in rancher.
    :type cluster_id: str
    :param node_template_id: Id of the node template to use for the cluster.
    :type node_template_id: str
    :param is_master: Indicates whether the nodes are supposed to be master nodes for the kubernetes cluster or
    just worker nodes. Master nodes also get the roles etcd and controlPlane in addition to worker.
    Worker only get the worker role. Further the name prefix for master nodes is master and worker for worker.
    :type is_master: bool
    :return: Id of the node pool in rancher.
    :rtype: str
    """
    if is_master:
        host_name_prefix = cluster_name + "-master"
        quantity = kubernetes_config.number_master_nodes
        control_plane = "master" in kubernetes_config.master_node_roles
        etcd = "etcd" in kubernetes_config.master_node_roles
        worker = "worker" in kubernetes_config.master_node_roles
        pool_name = "master"
    else:
        host_name_prefix = cluster_name + "-worker"
        quantity = kubernetes_config.number_worker_nodes
        control_plane = "master" in kubernetes_config.worker_node_roles
        etcd = "etcd" in kubernetes_config.worker_node_roles
        worker = "worker" in kubernetes_config.worker_node_roles
        pool_name = "worker"
    data = {
        "clusterId": f"{cluster_id}",
        "controlPlane": control_plane,
        "deleteNotReadyAfterSecs": 0,
        "etcd": etcd,
        "hostnamePrefix": f"{host_name_prefix}",
        "name": f"{pool_name}",
        "namespaceId": "",
        "nodeTaints": [],
        "nodeTemplateId": f"{node_template_id}",
        "quantity": quantity,
        "worker": worker,
    }
    data_json = json.dumps(data)
    response = session.post(rancher_config.rancher_api_base_url + "/nodepools", data=data_json)
    logger.debug(f"Received response with code {response.status_code}")
    if not 200 <= response.status_code <= 299:
        raise exceptions.IronikFatalError(
            f"Node pool creation failed with status {response.status_code}\n" f"{response.text}"
        )

    node_pool_dict = json.loads(response.text)
    return node_pool_dict.get("id")


def check_rancher_nodes_ready(session: Session, cluster_id: str, rancher_config: RancherConfig) -> int:
    """
    Checks how many nodes for the given cluster are in an active state and returns the number.
    :param rancher_config:
    :param session: A Session object initialized by create_rancher_session.
    :type session: requests.Session
    :param cluster_id: Id of the cluster to which the nodes should belong.
    :type cluster_id: str
    :return: The number of active nodes.
    :rtype: init
    """
    active_count = 0
    not_active_count = 0
    response = session.get(rancher_config.rancher_api_base_url + "/nodes")
    logger.debug(f"Received response with code {response.status_code}")
    response_dict = json.loads(response.text)
    response_dict_data = response_dict["data"]
    for entry in response_dict_data:
        if entry["clusterId"] == cluster_id:
            if entry["state"] == "active":
                active_count += 1
            else:
                not_active_count += 1
    logger.debug(
        f"Detected {active_count} active nodes and {not_active_count} not" f" ready nodes for cluster: {cluster_id}"
    )
    return active_count


def check_rancher_cluster_ready(session: Session, cluster_id: str, rancher_config: RancherConfig) -> bool:
    """

    :param session:
    :param cluster_id:
    :param rancher_config:
    :return:
    """
    response = session.get(rancher_config.rancher_api_base_url + "/clusters/" + cluster_id)
    logger.debug(f"Received response with code {response.status_code}\n")
    # logger.debug(r.text)
    response_dict = json.loads(response.text)
    state = response_dict["state"]
    logger.debug(f"Cluster {cluster_id} is in state {state}.")
    if state == "active":
        return True
    return False


def get_rancher_user_id(session: Session, rancher_config: RancherConfig) -> str:
    """
    Queries the rancher API to check if a user exists and returns true if it does and false otherwise.
    :param rancher_config:
    :param session: A Session object initialized by create_rancher_session.
    :type session: requests.Session
    :return:
    :rtype:
    """
    response = session.get(rancher_config.rancher_api_base_url + "/users")
    if response.status_code == 200:
        response_dict = json.loads(response.text)
        data_dicts = response_dict.get("data")
        for entry in data_dicts:
            if entry.get("username") == rancher_config.new_cluster_admin_user_name:
                return entry.get("id")
            if entry.get("name") == rancher_config.new_cluster_admin_user_name:
                return entry.get("id")
    return ""


def create_rancher_user(session: Session, rancher_config: RancherConfig) -> str:
    """
    Makes an API call to rancher to create a new user in rancher with the given name and password,
    setting must change password on first login to true.
    :param rancher_config:
    :param session: A Session object initialized by create_rancher_session.
    :type session: requests.Session
    :return: Id of the user.
    :rtype: str
    """
    data = {
        "enabled": True,
        "mustChangePassword": True,
        "name": f"{rancher_config.new_cluster_admin_user_name}",
        "password": f"{rancher_config.new_cluster_admin_user_password}",
        "principalIds": [],
        "username": f"{rancher_config.new_cluster_admin_user_name}",
    }
    data_json = json.dumps(data)
    response = session.post(rancher_config.rancher_api_base_url + "/users", data=data_json)
    logger.debug(f"Received response with code {response.status_code}")
    if not 200 <= response.status_code <= 299:
        raise exceptions.IronikPassingError(f"User creation failed with status {response.status_code}\n{response.text}")
    response_dict = json.loads(response.text)
    return response_dict["id"]


def add_rancher_base_binding_to_user(session: Session, rancher_config: RancherConfig, user_id: str) -> bool:
    """
    Makes an API call to rancher to add the user-base role binding to the given user id.
    :param rancher_config:
    :param session: A Session object initialized by create_rancher_session.
    :type session: requests.Session
    :param user_id:
    :return: True if it worked and false otherwise.
    :rtype: bool
    """
    data = {"globalRoleId": "user-base", "name": "", "userId": f"{user_id}"}
    data_json = json.dumps(data)
    response = session.post(rancher_config.rancher_api_base_url + "/globalrolebindings", data=data_json)
    logger.debug(f"Received response with code {response.status_code}")
    if not 200 <= response.status_code <= 299:
        raise exceptions.IronikPassingError(
            f"Binding user id to user-base failed with status " f"{response.status_code}\n{response.text}"
        )
    return True


def make_rancher_user_cluster_owner(
    session: Session, cluster_id: str, rancher_config: RancherConfig, user_id: str
) -> bool:
    """
    Makes an API call to rancher to make the given user id owner of the given cluster.
    :param rancher_config:
    :param session: A Session object initialized by create_rancher_session.
    :type session: requests.Session
    :param cluster_id: Id of the cluster.
    :type cluster_id: str
    :param user_id:
    :return: True if it worked and false otherwise.
    :rtype: bool
    """
    data = {
        "clusterId": f"{cluster_id}",
        "name": "",
        "namespaceId": "",
        "roleTemplateId": "cluster-owner",
        "userId": f"{user_id}",
    }
    data_json = json.dumps(data)
    response = session.post(rancher_config.rancher_api_base_url + "/clusterroletemplatebindings", data=data_json)
    logger.debug(f"Received response with code {response.status_code}")
    if not 200 <= response.status_code <= 299:
        raise exceptions.IronikPassingError(
            f"Making user id to cluster owner failed with status" f" {response.status_code}\n{response.text}"
        )
    return True


def request_kubeconfig(session: Session, cluster_id: str, rancher_config: RancherConfig) -> str:
    """

    :param session:
    :param cluster_id:
    :param rancher_config:
    :return:
    """
    response = session.post(
        rancher_config.rancher_api_base_url + "/clusters/" + cluster_id + "?action=generateKubeconfig"
    )
    logger.debug(f"Received response with code {response.status_code}")
    # logger.debug(r.text)
    if not 200 <= response.status_code <= 299:
        raise exceptions.IronikPassingError(f"Failed to request kubeconfig {response.status_code}\n{response.text}")
    response_dict = json.loads(response.text)
    return response_dict["config"]
