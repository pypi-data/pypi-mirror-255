"""

:author: Jonathan Decker
"""

import getpass
import logging
from typing import Tuple

import openstack
from keystoneauth1.exceptions import EndpointNotFound, SSLError, Unauthorized
from openstack.exceptions import ConflictException

from ironik.config_file_handler.deploy_template import (NetworkConfig,
                                                        OpenStackConfig,
                                                        OpenStackCredentials)
from ironik.util import exceptions

logger = logging.getLogger("logger")


def create_openstack_connection(
    username: str,
    password: str,
    project_id: str,
    auth_url: str,
    region_name: str,
    user_domain_name: str,
    project_domain_name: str,
) -> openstack.connection.Connection:
    """
    Creates an openstack.connection.Connection object based on the given credentials and further information from
    gwdg_defaults. This alone does not validate any of the credentials.
    This is the base object for all API calls to Openstack using the openstacksdk.
    Docs can be found here: https://docs.openstack.org/openstacksdk/latest/user/connection.html
    :param username: Openstack username.
    :type username: str
    :param password: Openstack password.
    :type password: str
    :param project_id: Openstack project id for which this tool should run.
    :type project_id: str
    :param auth_url: Openstack authentication url, which should be the identity service url followed by /v3.
    :type auth_url: str
    :return: A connection object from the openstacksdk.
    :rtype: openstack.connection.Connection
    :param region_name:
    :param user_domain_name:
    :param project_domain_name:
    """
    conn = openstack.connection.Connection(
        region_name=region_name,
        auth=dict(
            auth_url=auth_url,
            username=username,
            password=password,
            project_id=project_id,
            user_domain_name=user_domain_name,
            project_domain_name=project_domain_name,
        ),
    )
    return conn


def verify_openstack_connection(conn: openstack.connection.Connection) -> bool:
    """
    Verifies that the openstack connection is valid by making a simple API call.
    Returns True if it is valid and false otherwise.
    :param conn: A connection object initialized by create_openstack_connection.
    :type conn: openstack.connection.Connection
    :return: True if the connection is valid and false otherwise.
    :rtype: bool
    """
    try:
        _ = conn.get_compute_limits()
    except Unauthorized as _:
        logger.error("Authentication with Openstack failed, please verify your credentials.")
        return False
    except EndpointNotFound as _:
        logger.error("Authentication Endpoint not found, make sure the auth url is correct.")
        return False
    except SSLError as _:
        logger.error("SSL Error, make sure the auth url is correct.")
        return False
    logger.debug("Connection to Openstack is valid.")
    return True


def create_and_test_openstack_connection(
    openstack_credentials: OpenStackCredentials, openstack_config: OpenStackConfig
) -> openstack.connection.Connection:
    """
    Call create openstack connection and communicates possible errors.
    :param openstack_credentials:
    :param openstack_config:
    """

    # passsword check for openstack
    openstack_credentials = check_openstack_password(openstack_credentials)

    conn = create_openstack_connection(
        openstack_credentials.username,
        openstack_credentials.password,
        openstack_credentials.project_id,
        openstack_config.openstack_auth_url,
        openstack_config.region_name,
        openstack_config.user_domain_name,
        openstack_config.project_domain_name,
    )
    if not verify_openstack_connection(conn):
        raise exceptions.IronikFatalError(
            f"Openstack verification failed. Could not access Openstack API with the"
            f" given credentials under {openstack_config.openstack_auth_url}.\n"
            f"Please verify that your credentials and the given url are correct."
        )
    logger.debug("Openstack verification successful.")
    return conn


def get_openstack_flavors(conn: openstack.connection.Connection) -> list[dict]:
    """
    Makes a call to the openstack API to receive the available flavors and filters the returned attributes.
    :param conn: A connection object initialized by create_openstack_connection.
    :type conn: openstack.connection.Connection
    :return: A list of dictionaries each describing a flavor.
    :rtype: list[dict]
    """
    flavors = []
    count = 1
    for flavor in conn.list_flavors():
        flavors.append(
            {
                "name": flavor["name"],
                "id": flavor["id"],
                "ram": flavor["ram"],
                "vcpus": flavor["vcpus"],
                "disk": flavor["disk"],
            }
        )
    flavors.sort(key=lambda ele: ele.get("name"))
    for flavor in flavors:
        flavor["number"] = count
        count += 1
    return flavors


def get_openstack_images(conn: openstack.connection.Connection) -> list[dict]:
    """
    Makes a call to the openstack API to receive the available images and filter the returned attributes.
    :param conn: A connection object initialized by create_openstack_connection.
    :type conn: openstack.connection.Connection
    :return: A list of dictionaries each describing an image.
    :rtype: list[dict]
    """
    images = []
    count = 1
    for image in conn.list_images():
        images.append(
            {
                "name": image["name"],
                "id": image["id"],
                "disk_format": image["disk_format"],
                "size": image["size"],
                "visibility": image["visibility"],
            }
        )
    images.sort(key=lambda ele: ele.get("name"))
    for image in images:
        image["number"] = count
        count += 1
    return images


def get_openstack_compute_limits(conn: openstack.connection.Connection) -> dict:
    """
    Makes a call to the openstack API for the compute limits, converts it into a dictionary and returns it.
    :param conn: A connection object initialized by create_openstack_connection.
    :type conn: openstack.connection.Connection
    :return: A dictionary containing the compute limits of the openstack account.
    :rtype: dict
    """
    limits = conn.get_compute_limits()
    limits_dict = {
        "max_cores": limits["max_total_cores"],
        "max_instances": limits["max_total_instances"],
        "max_ram": limits["max_total_ram_size"],
        "used_cores": limits["total_cores_used"],
        "used_instances": limits["total_instances_used"],
        "used_ram": limits["total_ram_used"],
    }
    return limits_dict


def find_out_openstack_floating_ip_is_free(conn: openstack.connection.Connection) -> Tuple[int, bool]:
    """
    Make a call to the openstack API to get the current floating IPs and check whether an IP is not attached.
    It further tries to claim another floating IP to check whether quota is still left for additional floating IPs
    in case all listed floating IPs are already attached.
    Returns a tuple with the number of attached IPs and a bool than indicates whether at least one floating IP is free.
    :param conn: A connection object initialized by create_openstack_connection.
    :type conn: openstack.connection.Connection
    :return: A tuple with an int that represents the number of attached IPs
    and a bool that indicates whether at least one floating IP is free
    :rtype: (int, bool)
    """
    floating_ips = conn.list_floating_ips()
    unattached = False
    attached_ips = 0
    logger.debug("Received floating IPs:")
    logger.debug(*map(lambda x: x.get("floating_ip_address"), floating_ips))
    for ip_address in floating_ips:
        if ip_address["attached"] is False:
            unattached = True
        else:
            attached_ips += 1
    if unattached:
        logger.debug("At least one IP was not attached.")
        return attached_ips, True
    try:
        response = conn.available_floating_ip()
        logger.debug(f"Got response to floating IP request: {response}")
    except ConflictException as exception:
        logger.debug(f"Got ConflictException, assuming Quota was exceeded: {exception}")
        return attached_ips, False
    return attached_ips, True


def get_openstack_public_and_private_networks(conn: openstack.connection.Connection) -> Tuple[dict, list[dict]]:
    """
    Makes a request to the openstack API for all networks and finds the public network and declares all other
    networks as private networks.
    Returns a tuple with the public network and the list of private networks.
    :param conn: A connection object initialized by create_openstack_connection.
    :type conn: openstack.connection.Connection
    :return: A tuple with a dictionary for the public network and a list of dictionaries for the private networks.
    :rtype: (dict, list[dict])
    """
    public_network = {}
    private_networks = []
    for net in conn.list_networks():
        if net["name"] == "public":
            public_network["name"] = net["name"]
            public_network["id"] = net["id"]
        else:
            private_networks.append({"name": net["name"], "id": net["id"]})
    logger.debug(f"Received public network: {public_network}")
    logger.debug(f"Received private networks: {private_networks}")
    return public_network, private_networks


def get_openstack_subnets(conn: openstack.connection.Connection) -> list[dict]:
    """
    Makes a request to the openstack API to get all subnets, filter some attributes and return a list of dictionaries.
    :param conn: A connection object initialized by create_openstack_connection.
    :type conn: openstack.connection.Connection
    :return: A list of dictionaries where each entry represents a subnet.
    :rtype: list[dict]
    """
    subnets = []
    for subnet in conn.list_subnets():
        subnets.append({"network_id": subnet["network_id"], "id": subnet["id"], "name": subnet["name"]})
    logger.debug(f"Received subnets: {subnets}")
    return subnets


def get_openstack_routers(conn: openstack.connection.Connection) -> list[dict]:
    """
    Make a request to the Openstack API to get all routers, filter some attributes and return a list of dictionaries.
    :param conn: A connection object initialized by create_openstack_connection.
    :type conn: openstack.connection.Connection
    :return: A list of dictionaries where each entry represents a router.
    :rtype: list[dict]
    """
    routers = []
    for router in conn.list_routers():
        routers.append(
            {"name": router["name"], "id": router["id"], "network_id": router["external_gateway_info"]["network_id"]}
        )
    logger.debug(f"Received routers: {routers}")
    return routers


def create_openstack_security_group(
    conn: openstack.connection.Connection,
    openstack_config: OpenStackConfig,
    network_config: NetworkConfig,
    cluster_name: str,
) -> bool:
    """
    Checks whether a security group with the given name already exists and if yes, tries to delete and recreate it.
    Finally, returns the name of the newly created security group.
    :param conn: Valid openstack connection
    :type conn: openstack.connection.Connection
    :param openstack_config:
    :param network_config:
    :param cluster_name:
    :return:
    :rtype: bool
    """
    security_groups = conn.list_security_groups()
    name_exists = False
    if openstack_config.security_group_name in map(lambda key: key.get("name"), security_groups):
        name_exists = True
    else:
        logger.debug(f"Security group with the name {openstack_config.security_group_name} already exists.")
    if name_exists:
        try:
            response = conn.delete_security_group(openstack_config.security_group_name)
        except ConflictException as exception:
            raise exceptions.IronikFatalError(f"Error when trying to delete security group: {exception}")
        if response:
            logger.debug(f"Deleted security group {openstack_config.security_group_name}.")
        else:
            raise exceptions.IronikFatalError(f"Failed to delete security group {openstack_config.security_group_name}")
    try:
        conn.create_security_group(openstack_config.security_group_name, f"Internal security group for {cluster_name}")
    except ConflictException as exception:
        raise exceptions.IronikFatalError(f"Error when trying to create new security group: {exception}")
    for tcp_port in network_config.required_tcp_ports:
        conn.create_security_group_rule(
            openstack_config.security_group_name, tcp_port, tcp_port, "TCP", openstack_config.remote_ip_prefix
        )
    for udp_port in network_config.required_udp_ports:
        conn.create_security_group_rule(
            openstack_config.security_group_name, udp_port, udp_port, "UDP", openstack_config.remote_ip_prefix
        )
    conn.create_security_group_rule(
        openstack_config.security_group_name,
        network_config.worker_port_range_min,
        network_config.worker_port_range_max,
        "TCP",
        openstack_config.remote_ip_prefix,
    )
    conn.create_security_group_rule(
        openstack_config.security_group_name,
        network_config.worker_port_range_min,
        network_config.worker_port_range_max,
        "UDP",
        openstack_config.remote_ip_prefix,
    )
    logger.debug(f"Created Security group {openstack_config.security_group_name}")
    return True


def find_openstack_load_balancer_port_id_by_ip(
    conn: openstack.connection.Connection, openstack_config: OpenStackConfig, load_balancer_internal_ip: str
) -> str:
    """
    Makes a call to the openstack API to find the id of port belonging to a load balancer with the given ip.
    :param conn: A connection object initialized by create_openstack_connection.
    :type conn: openstack.connection.Connection
    :param openstack_config:
    :param load_balancer_internal_ip: Ip of the load balancer device.
    :type load_balancer_internal_ip: str
    :return: Id of the target port.
    :rtype: str
    """
    target_port = ""
    for port in conn.list_ports():
        if port["device_owner"] == openstack_config.load_balancer_device_type:
            fixed_ip = port["fixed_ips"][0]
            if fixed_ip["ip_address"] == load_balancer_internal_ip:
                target_port = port["id"]
    if target_port == "":
        raise exceptions.IronikPassingError(f"Failed to find target port for loadbalancer: {load_balancer_internal_ip}")
    logger.debug(f"Target port for load balancer with internal ip {load_balancer_internal_ip} has id: {target_port}")
    return target_port


def associate_openstack_floating_ip_with_port_id(
    conn: openstack.connection.Connection, public_network_id: str, target_port: str
) -> dict:
    """
    Makes API calls to openstack to delete unattached floating IPs and create a new one and attach it to the given port.
    :param conn: A connection object initialized by create_openstack_connection.
    :type conn: openstack.connection.Connection
    :param public_network_id: Id of the public network from which the floating IP should come.
    :type public_network_id: str
    :param target_port: Id of the port, the new floating IP should be attached to.
    :type target_port: str
    :return: Dictionary or munch representing the newly assigned floating IP.
    :rtype: dict
    """
    conn.delete_unattached_floating_ips()
    new_floating_ip = conn.create_floating_ip(public_network_id, port=target_port)
    return new_floating_ip


def find_floating_ip_for_internal_ip(conn: openstack.connection.Connection, internal_ip: str) -> str:
    """
    :param conn: A connection object initialized by create_openstack_connection.
    :type conn: openstack.connection.Connection
    :param internal_ip: The internal IP inside OpenStack of an instance or load balancer.
    :type internal_ip: str
    :return: The respective floating IP associated with the internal IP or an empty string.
    :rtype: str
    """
    floating_ips = conn.list_floating_ips()
    target_floating_ip = ""
    for floating_ip in floating_ips:
        if floating_ip["fixed_ip_address"] == internal_ip:
            target_floating_ip = floating_ip["floating_ip_address"]
            break
    return target_floating_ip


def get_openstack_volume_limits(conn: openstack.connection.Connection) -> dict:
    """Returns a dict with the volume limits for the given OpenStack connection.

    Args:
        conn (conn:openstack.connection.Connection): A connection object initialized by create_openstack_connection.

    Returns:
        dict: A dictionary containing the volume limits of the openstack account.
    """
    limits = conn.get_volume_limits()
    limits_dict = {
        "max_size": limits["absolute"]["maxTotalVolumeGigabytes"],
        "used_size": limits["absolute"]["totalGigabytesUsed"],
        "max_number": limits["absolute"]["maxTotalVolumes"],
        "used_number": limits["absolute"]["totalVolumesUsed"],
    }
    return limits_dict


def match_subnet(conn: openstack.connection.Connection, network_id: str) -> dict:
    """
    Calls get openstack subnets and matches the subnet with the given network id or calls ask for subnet if there are
    multiple subnets.
    :param conn: Valid openstack connection
    :type conn: openstack.connection.Connection
    :param network_id: Network Id of the external network of the GWDG openstack deployment.
    :type network_id: str
    :return: Dictionary representing the subnet
    :rtype: dict
    """
    subnets = get_openstack_subnets(conn)
    filtered_subnets = []
    for subnet in subnets:
        if subnet["network_id"] == network_id:
            filtered_subnets.append(subnet)
    logger.debug(f"Filtered subnets for network_id {network_id}: {filtered_subnets}")
    if len(filtered_subnets) == 0:
        return {}
    return filtered_subnets[0]


def check_openstack_password(openstack_credentials: OpenStackCredentials) -> OpenStackCredentials:
    """
    Check if password is available in ironik_template.yaml or not.
    If not available ask user from command line.
    :param openstack_credentials: object contains data for openstack connection
    :type openstack_credentials: OpenStackCredentials
    :return openstack_credentials: object contains data for openstack connection with password
    :type openstack_credentials: OpenStackCredentials
    """

    if openstack_credentials.password == "":
        logger.info("Password for openstack is not available.")
        print("Password for openstack is not available.\n")
        password = getpass.getpass(prompt="Enter Password:")
        openstack_credentials.password = password

    return openstack_credentials
