"""

:author: Jonathan Decker
"""

import logging

import openstack
from rich import print

from ironik.config_file_handler.deploy_template import (DeploymentOptions,
                                                        KubernetesConfig,
                                                        OpenStackConfig)
from ironik.openstack_handler import openstack_api_caller
from ironik.util import exceptions

logger = logging.getLogger("logger")


def calculate_free_resources(
    conn: openstack.connection.Connection,
    flavor_dict: dict,
    kubernetes_config: KubernetesConfig,
    openstack_config: OpenStackConfig,
    check_ip: bool,
) -> bool:
    """Check whether compute limits can satisfy requested deployment and give an overview.

    Calls get openstack compute limits, as well as get openstack volume limits and calculates how many resources
    will be used by deploying the given number of master and worker nodes with the given flavors and volumes.
    Also displays an overview.

    Args:
        conn (openstack.connection.Connection): Valid openstack connection.
        flavor_dict (dict): Dictionary of the master flavor as returned by ask for flavor.
        kubernetes_config (KubernetesConfig):
        openstack_config (OpenStackConfig):
        check_ip (bool): Whether to skip checking for free floating IPs, will skip if False.

    Returns:
        bool: A bool that is true if the required resources fit within the maximum allowed compute limits
    """
    compute_limits = openstack_api_caller.get_openstack_compute_limits(conn)
    logger.debug(f"Received compute_limits: {compute_limits}")
    volume_limits = openstack_api_caller.get_openstack_volume_limits(conn)
    logger.debug(f"Received volume_limits: {volume_limits}")
    used_instances_after = (
        compute_limits["used_instances"] + kubernetes_config.number_master_nodes + kubernetes_config.number_worker_nodes
    )
    used_vcpus_after = (
        compute_limits["used_cores"]
        + kubernetes_config.number_master_nodes * flavor_dict["vcpus"]
        + kubernetes_config.number_worker_nodes * flavor_dict["vcpus"]
    )
    used_ram_after = (
        compute_limits["used_ram"]
        + kubernetes_config.number_master_nodes * flavor_dict["ram"]
        + kubernetes_config.number_worker_nodes * flavor_dict["ram"]
    )
    used_volume_number_after = (
        volume_limits["used_number"]
        + (kubernetes_config.number_master_nodes if openstack_config.volume_size > 0 else 0)
        + (kubernetes_config.number_worker_nodes if openstack_config.volume_size > 0 else 0)
    )
    used_volume_size_after = (
        volume_limits["used_size"]
        + kubernetes_config.number_master_nodes * openstack_config.volume_size
        + kubernetes_config.number_worker_nodes * openstack_config.volume_size
    )

    output = ""
    dash = "-" * 48
    output = output + "{:<12s}{:>12s}{:>12s}{:>12s}".format("Resource", "Used Now", "Used After", "Max") + "\n"
    output = output + dash + "\n"
    output = (
        output
        + "{:<12s}{:>12d}{:>12d}{:>12d}".format(
            "Instances", compute_limits["used_instances"], used_instances_after, compute_limits["max_instances"]
        )
        + "\n"
    )
    output = (
        output
        + "{:<12s}{:>12d}{:>12d}{:>12d}".format(
            "VCPUs", compute_limits["used_cores"], used_vcpus_after, compute_limits["max_cores"]
        )
        + "\n"
    )
    output = (
        output
        + "{:<12s}{:>12d}{:>12d}{:>12d}".format(
            "RAM", compute_limits["used_ram"], used_ram_after, compute_limits["max_ram"]
        )
        + "\n"
    )
    output = (
        output
        + "{:<12s}{:>12d}{:>12d}{:>12d}".format(
            "Volume size", volume_limits["used_size"], used_volume_size_after, volume_limits["max_size"]
        )
        + "\n"
    )
    output = (
        output
        + "{:<12s}{:>12d}{:>12d}{:>12d}".format(
            "Volumes", volume_limits["used_number"], used_volume_number_after, volume_limits["max_number"]
        )
        + "\n"
    )

    if check_ip:
        used_floating_ips, min_one_floating_ip_is_free = openstack_api_caller.find_out_openstack_floating_ip_is_free(
            conn
        )
        logger.debug(
            f"Received used_floating_ips {used_floating_ips},"
            f" min_one_floating_ip_is_free {min_one_floating_ip_is_free}"
        )

        if min_one_floating_ip_is_free:
            used_floating_ips_str = f"min {used_floating_ips + 1}"
        else:
            used_floating_ips_str = f"{used_floating_ips}"
        output = (
            output
            + "{:<12s}{:>12d}{:>12d}{:>12s}".format(
                "Floating IPs", used_floating_ips, used_floating_ips + 1, used_floating_ips_str
            )
            + "\n"
        )
    print(output)

    insufficient = False
    if used_instances_after > compute_limits["max_instances"]:
        logger.error("Not enough instances available to satisfy the requirements.")
        print("Not enough instances available to satisfy the requirements.")
        insufficient = True
    if used_vcpus_after > compute_limits["max_cores"]:
        logger.error("Not enough cores available to satisfy the requirements.")
        print("Not enough cores available to satisfy the requirements.")
        insufficient = True
    if used_ram_after > compute_limits["max_ram"]:
        logger.error("Not enough memory available to satisfy the requirements.")
        print("Not enough memory available to satisfy the requirements.")
        insufficient = True
    if check_ip:
        if not min_one_floating_ip_is_free:
            logger.error("No free floating IP available to satisfy the requirements.")
            print("No free floating IP available to satisfy the requirements.")
            insufficient = True

    if used_volume_size_after > volume_limits["max_size"]:
        logger.error("Not enough volume size available to satisfy the requirements.")
        print("Not enough volume size available to satisfy the requirements.")
        insufficient = True
    if used_volume_number_after > volume_limits["max_number"]:
        logger.error("Not enough volumes available to satisfy the requirements.")
        print("Not enough volumes available to satisfy the requirements.")
        insufficient = True

    if insufficient:
        raise exceptions.IronikFatalError("Due to unsatisfied requirements the process will terminate here.")

    logger.info("Enough resources are available to satisfy the requirements.")
    print("Enough resources are available to satisfy the requirements.")
    return True


def preprocess_and_calculate_resource_consumption(
    openstack_config: OpenStackConfig,
    deployment_options: DeploymentOptions,
    kubernetes_config: KubernetesConfig,
    openstack_connection: openstack.connection.Connection,
    flavors: list[dict],
    images: list[dict],
) -> bool:
    """

    Args:
        openstack_config:
        deployment_options:
        kubernetes_config:
        openstack_connection:
        flavors:
        images:

    Returns:

    """
    filter_flavors = filter(lambda key: key.get("name") == openstack_config.default_flavor_name, flavors)
    flavor_dict = [*filter_flavors].pop()
    logger.debug(f"Using flavor dict: {flavor_dict}")
    filtered_images = filter(lambda key: key.get("name") == openstack_config.default_image_name, images)
    image_dict = [*filtered_images].pop()
    logger.debug(f"Using image dict: {image_dict}")
    check_ip = deployment_options.deploy_nginx_workload
    if not calculate_free_resources(openstack_connection, flavor_dict, kubernetes_config, openstack_config, check_ip):
        return False
    return True
