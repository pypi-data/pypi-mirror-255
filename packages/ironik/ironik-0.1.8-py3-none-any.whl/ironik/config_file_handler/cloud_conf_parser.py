"""

:author: Jonathan Decker
"""

import configparser
import io
import logging

from ironik.config_file_handler.deploy_template import (OpenStackConfig,
                                                        OpenStackCredentials)

logger = logging.getLogger("logger")


def get_cloud_conf(
    openstack_credentials: OpenStackCredentials,
    openstack_config: OpenStackConfig,
    subnet_id: str,
    public_network_id: str,
    router_id: str,
) -> configparser.ConfigParser:
    """

    :param openstack_credentials:
    :param openstack_config:
    :param subnet_id:
    :param public_network_id:
    :param router_id:
    :return:
    """
    cloud_conf = configparser.ConfigParser()
    cloud_conf["Global"] = {
        "auth-url": openstack_config.openstack_auth_url,
        "username": openstack_credentials.username,
        "password": openstack_credentials.password,
        "region": openstack_config.region_name,
        "tenant-id": openstack_credentials.project_id,
        "domain-name": openstack_config.project_domain_name,
    }
    cloud_conf["BlockStorage"] = {"ignore-volume-az": "true", "trust-device-path": "false"}
    cloud_conf["Networking"] = {"public-network-name": "public"}
    cloud_conf["LoadBalancer"] = {
        "use-octavia": str(openstack_config.use_octavia).lower(),
        "subnet-id": subnet_id,
        "floating-network-id": public_network_id,
        "create-monitor": "false",
        "manage-security-groups": "true",
        "monitor-max-retries": "0",
        "enabled": "true",
        "lb-version": "v2",
        "lb-provider": openstack_config.lb_provider,
    }
    cloud_conf["Route"] = {"router-id": router_id}
    cloud_conf["Metadata"] = {"request-timeout": "0"}

    return cloud_conf


def config_ini_to_string(cloud_conf: configparser.ConfigParser) -> str:
    in_memory_file = io.StringIO()
    cloud_conf.write(in_memory_file)
    cloud_conf_str = in_memory_file.getvalue()
    in_memory_file.close()
    return cloud_conf_str
