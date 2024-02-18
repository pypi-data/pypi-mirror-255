"""

:author: Jonathan Decker
"""

import datetime
import logging
import secrets
import string
import time

import requests
from rich import print

from ironik.config_file_handler import cloud_conf_parser
from ironik.config_file_handler.deploy_template import (KubernetesConfig,
                                                        OpenStackConfig,
                                                        OpenStackCredentials,
                                                        RancherConfig)
from ironik.rancher import kubernetes_api_caller, rancher_api_caller
from ironik.util import exceptions

logger = logging.getLogger("logger")


def remove_all_but_alphanum_dash_from_string_and_lower(dirty_string: str) -> str:
    """
    Removes non-alphanumeric characters from the given string except dash "-" and lowers it before returning it.
    This is done to make user input comply with restrictions on names in the API.
    :param dirty_string: A string.
    :type dirty_string: str
    :return: The string without any non alphanumeric characters except dashes and in lower case.
    :rtype: str
    """
    dirty_list = list(dirty_string)
    clean_list = []
    for char in dirty_list:
        if char.isalnum() or char == "-":
            clean_list.append(char.lower())
    clean_string = "".join(clean_list)
    return clean_string


def generate_random_string(length: int) -> str:
    """
    Generates a secure random string of the given length and returns it.
    :param length: Length of the random string to return, only positive integers are allowed.
    :type length: int
    :return: A random string generated with the secrets built-in library.
    :rtype: str
    """
    source = string.ascii_letters + string.digits
    random_string = "".join(secrets.choice(source) for _ in range(length))
    return random_string


def check_and_prepare_cluster_name(name: str) -> str:
    raw_name = name
    name = remove_all_but_alphanum_dash_from_string_and_lower(name)
    if raw_name != name:
        print("Only lowercase alphanumeric characters are allowed for the cluster name.")
        print(f"Cluster name set to: {name}")
    if len(name) <= 1:
        raise exceptions.IronikFatalError(f"Cluster name '{name}' is too short.")
    return name


def validate_key_in_dict(key: str, list_dicts: list[dict]) -> bool:
    """

    :param key:
    :param list_dicts:
    :return:
    """
    if key in map(lambda x: x.get("name"), list_dicts):
        return True
    logger.error(f"Could not find {key}.")
    print(f"Could not find {key}.")
    print("Available are:")
    print(*map(lambda x: x.get("name"), list_dicts))
    return False


def get_router_id_from_routers(public_network_id: str, routers: list[dict]) -> str:
    """

    :param public_network_id:
    :param routers:
    :return:
    """
    if len(routers) == 0:
        raise exceptions.IronikFatalError("Could not find any routers in OpenStack.")
    filtered_router = filter(lambda key: key.get("network_id") == public_network_id, routers)
    router_dict = [*filtered_router].pop()
    router_id = router_dict.get("id", None)
    if router_id is None:
        raise exceptions.IronikFatalError(f"Could not find the id of router: {router_dict}")
    logger.info(f"Found router id: {router_id}")
    print(f"Found router id: {router_id}")
    return router_id


def wait_for_nodes_ready(
    kubernetes_config: KubernetesConfig,
    rancher_config: RancherConfig,
    rancher_session: requests.Session,
    cluster_id: str,
    timeout_in_s: int = 3600,
) -> bool:
    """

    Args:
        kubernetes_config:
        rancher_config:
        rancher_session:
        cluster_id:
        timeout_in_s:

    Returns:

    """
    timeout = datetime.timedelta(seconds=timeout_in_s)
    previous_ready_count = 0
    total_nodes = kubernetes_config.number_master_nodes + kubernetes_config.number_worker_nodes
    print(f"0 out of {total_nodes} nodes are ready.")

    # For some reason the nodes are listed as ready for the first moments of their existence, which confuses this
    # ready check. To circumvent that, the check will wait some time before checking the first time as nodes take
    # some time to set up anyway.
    time.sleep(120)
    start = datetime.datetime.now()
    while previous_ready_count < total_nodes:
        now_ready = rancher_api_caller.check_rancher_nodes_ready(rancher_session, cluster_id, rancher_config)
        if now_ready > previous_ready_count:
            print(f"{now_ready} out of {total_nodes} nodes are ready.")
            previous_ready_count = now_ready
        else:
            if datetime.datetime.now() - start > timeout:
                return False
            time.sleep(5)
    return True


def wait_for_cluster_ready(
    rancher_config: RancherConfig, rancher_session: requests.Session, cluster_id: str, timeout_in_s: int = 3600
) -> bool:
    """

    Args:
        rancher_config:
        rancher_session:
        cluster_id:
        timeout_in_s:

    Returns:

    """
    timeout = datetime.timedelta(seconds=timeout_in_s)
    time.sleep(10)
    start = datetime.datetime.now()
    while True:
        time.sleep(5)
        ready = rancher_api_caller.check_rancher_cluster_ready(rancher_session, cluster_id, rancher_config)
        if ready:
            logger.debug("Cluster passed first ready check.")
            break
        if datetime.datetime.now() - start > timeout:
            return False
    # Do it twice as the cluster sometimes needs to update before it is truly ready
    time.sleep(10)
    while True:
        time.sleep(5)
        ready = rancher_api_caller.check_rancher_cluster_ready(rancher_session, cluster_id, rancher_config)
        if ready:
            logger.debug("Cluster passed second ready check.")
            break
        if datetime.datetime.now() - start > timeout:
            return False
    return True


def ensure_rancher_user(rancher_config: RancherConfig, rancher_session: requests.Session) -> str:
    """

    Args:
        rancher_config:
        rancher_session:

    Returns:

    """
    user_id = rancher_api_caller.get_rancher_user_id(rancher_session, rancher_config)
    if user_id is None or len(user_id) == 0:
        if len(rancher_config.new_cluster_admin_user_password) == 0:
            logger.info("No password given for user, generating a new one.")
            print("No password given for user, generating a new one.")
            rancher_config.new_cluster_admin_user_password = generate_random_string(16)
            print(f"Generated password: \n'{rancher_config.new_cluster_admin_user_password}'")
            user_id = rancher_api_caller.create_rancher_user(rancher_session, rancher_config)
    else:
        print(f"User {rancher_config.new_cluster_admin_user_name} already exists, skipping creation.")
    return user_id


@exceptions.passing_error_handler
def update_rancher_user(rancher_config: RancherConfig, rancher_session: requests.Session, cluster_id: str) -> bool:
    """

    Args:
        rancher_config:
        rancher_session:
        cluster_id:

    Returns:

    """

    user_id = ensure_rancher_user(rancher_config, rancher_session)

    if rancher_api_caller.add_rancher_base_binding_to_user(rancher_session, rancher_config, user_id):
        logger.info("Added role bindings to user.")
        print("Added role bindings to user.")
        if rancher_api_caller.make_rancher_user_cluster_owner(rancher_session, cluster_id, rancher_config, user_id):
            logger.info(f"Made {user_id} owner of cluster with id {cluster_id}")
            print(f"Made {user_id} owner of cluster with id {cluster_id}")
    return True


@exceptions.passing_error_handler
def handle_kubernetes_setup(
    openstack_credentials: OpenStackCredentials,
    openstack_config: OpenStackConfig,
    rancher_config: RancherConfig,
    rancher_session: requests.Session,
    cluster_id: str,
    subnet_id: str,
    public_network_id: str,
    router_id: str,
) -> bool:
    """

    Args:
        openstack_credentials:
        openstack_config:
        rancher_config:
        rancher_session:
        cluster_id:
        subnet_id:
        public_network_id:
        router_id:

    Returns:

    """
    # Fetch kubeconfig from Rancher
    kube_config_str = rancher_api_caller.request_kubeconfig(rancher_session, cluster_id, rancher_config)

    kube_client = kubernetes_api_caller.init_client(kube_config_str)
    # Verify that the client works
    kubernetes_api_caller.verify_client(kube_client)
    # Fill out cloud conf
    cloud_conf = cloud_conf_parser.get_cloud_conf(
        openstack_credentials, openstack_config, subnet_id, public_network_id, router_id
    )
    cloud_conf_str = cloud_conf_parser.config_ini_to_string(cloud_conf)
    if not kubernetes_api_caller.create_cloud_conf_secret(kube_client, cloud_conf_str):
        raise exceptions.IronikPassingError("Failed to create cloud conf secret.")

    # Deploy cloud controller manager
    if not kubernetes_api_caller.apply_controller_manager_manifests(kube_client, openstack_config):
        raise exceptions.IronikPassingError("Failed to apply controller manager manifests.")

    # Validate that it works by checking container status and node taints

    # Deploy CSI driver
    if not kubernetes_api_caller.apply_csi_driver_manifests(kube_client):
        raise exceptions.IronikPassingError("Failed to apply CSI driver manifests.")

    return True
