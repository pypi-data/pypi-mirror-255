"""

:author: Jonathan Decker
"""

import logging

import yaml
from kubernetes import client
from kubernetes.client import ApiException
from kubernetes.config.kube_config import KubeConfigLoader
from kubernetes.utils import FailToCreateError, create_from_yaml
from rich import print

from ironik.config_file_handler import manifest_parser
from ironik.config_file_handler.deploy_template import OpenStackConfig
from ironik.util import exceptions

logger = logging.getLogger("logger")


def init_client(kube_config: str) -> client.CoreV1Api:
    """

    :param kube_config:
    :return:
    """
    kube_config_dict = yaml.safe_load(kube_config)

    # Workaround to load kube config in memory without saving to a temp file
    kcl = KubeConfigLoader(kube_config_dict)
    configuration = client.Configuration()
    kcl.load_and_set(configuration)
    api_client = client.ApiClient(configuration)
    v1_client = client.CoreV1Api(api_client)

    return v1_client


def create_cloud_conf_secret(kube_client: client.CoreV1Api, cloud_conf_str: str) -> bool:
    """

    Args:
        kube_client:
        cloud_conf_str:

    Returns:

    """
    metadata = client.V1ObjectMeta(name="cloud-config", namespace="kube-system")
    secret_body = client.V1Secret(string_data={"cloud.conf": cloud_conf_str}, metadata=metadata)
    try:
        response = kube_client.create_namespaced_secret("kube-system", secret_body)
        logger.debug("Created cloud conf secret, got response: ")
        logger.debug(response)
    except ApiException as exception:
        raise exceptions.IronikPassingError(f"Creating secret for cloud conf failed: {exception}")
    return True


def apply_controller_manager_manifests(kube_client: client.CoreV1Api, openstack_config: OpenStackConfig) -> bool:
    """

    Args:
        kube_client:
        openstack_config:

    Returns:

    """
    controller_roles_yaml = manifest_parser.get_cloud_controller_roles_manifest()
    controller_role_bindings_yaml = manifest_parser.get_cloud_controller_role_bindings_manifest()
    controller_manager_yamls = manifest_parser.get_openstack_controller_manager_manifest(openstack_config)

    try:
        create_from_yaml(kube_client.api_client, yaml_objects=[controller_roles_yaml])
        logger.info("Applied controller roles manifest.")
        print("Applied controller roles manifest.")
        create_from_yaml(kube_client.api_client, yaml_objects=[controller_role_bindings_yaml])
        logger.info("Applied controller role bindings manifest.")
        print("Applied controller role bindings manifest.")
        create_from_yaml(kube_client.api_client, yaml_objects=controller_manager_yamls)
        logger.info("Applied openstack controller manager manifest.")
        print("Applied openstack controller manager manifest.")
    except FailToCreateError as exception:
        raise exceptions.IronikPassingError(f"Applying controller manifests failed with error: {exception}")
    return True


def apply_csi_driver_manifests(kube_client: client.CoreV1Api) -> bool:
    """

    Args:
        kube_client:

    Returns:

    """
    csi_driver_yamls = manifest_parser.get_csi_plugin_manifest()

    try:
        create_from_yaml(kube_client.api_client, yaml_objects=csi_driver_yamls)
        logger.info("Applied csi driver manifest.")
        print("Applied csi driver manifest.")
    except FailToCreateError as exception:
        raise exceptions.IronikPassingError(f"Applying csi driver manifests failed with error: {exception}")
    return True


def verify_client(kube_client: client.CoreV1Api) -> bool:
    """

    Args:
        kube_client:

    Returns:

    """
    try:
        response = kube_client.list_node()
    except ApiException as exception:
        raise exceptions.IronikPassingError(f"Could not verify kube client: {exception}")
    node_names = []
    for ele in response.items:
        node_names.append(ele.metadata.name)
    if len(node_names) == 0:
        raise exceptions.IronikPassingError("Could not verify kube client: No nodes found.")
    return True
