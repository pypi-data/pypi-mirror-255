"""
Definition and functions for spawning deployment templates.

:author: Jonathan Decker
"""

import logging
from dataclasses import dataclass, field
from pathlib import Path

import yaml
from rich import print

from ironik.util.exceptions import IronikFatalError

logger = logging.getLogger("logger")


@dataclass
class RancherCredentials(yaml.YAMLObject):
    """
    Dataclass for Rancher credentials that can be parsed in YAML.
    """

    rancher_access_key: str = ""
    rancher_secret_key: str = ""
    yaml_tag = "!RancherCredentials"
    yaml_loader = yaml.SafeLoader


@dataclass
class OpenStackCredentials(yaml.YAMLObject):
    """
    Dataclass for OpenStack credentials that can be parsed in YAML.
    """

    username: str = ""
    password: str = ""
    project_id: str = ""
    yaml_tag = "!OpenStackCredentials"
    yaml_loader = yaml.SafeLoader


@dataclass
class RancherConfig(yaml.YAMLObject):
    """
    Dataclass for Rancher config that can be parsed in YAML.
    """

    rancher_api_base_url: str = ""
    ssh_user: str = ""
    new_cluster_admin_user_name: str = ""
    new_cluster_admin_user_password: str = ""
    engine_install_url: str = "https://releases.rancher.com/install-docker/20.10.sh"
    yaml_tag = "!RancherConfig"
    yaml_loader = yaml.SafeLoader


@dataclass
class OpenStackConfig(yaml.YAMLObject):
    """
    Dataclass for OpenStack configuration that can be parsed in YAML.
    """

    openstack_auth_url: str = ""
    user_domain_name: str = ""
    project_domain_name: str = ""
    lb_provider: str = ""
    default_flavor_name: str = ""
    default_image_name: str = ""
    remote_ip_prefix: str = ""
    private_network_id: str = ""
    region_name: str = "RegionOne"
    use_octavia: bool = False
    security_group_name: str = "ironik-k8s-node"
    volume_size: int = 20
    # volume_type: str = "ssd"
    yaml_tag = "!OpenStackConfig"
    yaml_loader = yaml.SafeLoader


@dataclass
class NetworkConfig(yaml.YAMLObject):
    """
    Dataclass for network configuration that can be parsed in YAML.
    """

    required_tcp_ports: list[int] = field(default_factory=list)
    required_udp_ports: list[int] = field(default_factory=list)
    worker_port_range_min: int = 30000
    worker_port_range_max: int = 32767
    #required_tcp_ports =
    #required_udp_ports = [8443, 8472]
    yaml_tag = "!NetworkConfig"
    yaml_loader = yaml.SafeLoader


@dataclass
class KubernetesConfig(yaml.YAMLObject):
    """
    Dataclass for Kubernetes configuration that can be parsed in YAML.
    """

    master_node_roles: str = "master, etcd, worker"
    worker_node_roles: str = "worker"
    version: str = "v1.24.8-rancher1-1"
    number_master_nodes: int = 1
    number_worker_nodes: int = 1
    yaml_tag = "!KubernetesConfig"
    yaml_loader = yaml.SafeLoader


@dataclass
class DeploymentOptions(yaml.YAMLObject):
    """
    Dataclass for deployment options that can be parsed in YAML.
    """

    deploy_example_workload: bool = False
    example_workload_image: str = "rancher/hello-world"
    example_workload_name: str = "hello-world-example"
    deploy_nginx_workload: bool = False
    nginx_ingress_version: str = "4.4.0"
    nginx_ingress_repo: str = "https://kubernetes.github.io/ingress-nginx"
    nginx_ingress_app_name: str = "nginx-ingress-lb"
    install_cinder_driver: bool = False
    deploy_example_volume: bool = False
    cleanup_example_workload: bool = True
    cleanup_nginx_ingress: bool = True
    cleanup_example_volume: bool = True
    yaml_tag = "!DeploymentOptions"
    yaml_loader = yaml.SafeLoader


@dataclass
class DeployConfig(yaml.YAMLObject):
    """
    Dataclass for holding together all other data classes that can be parsed in YAML.
    """

    rancher_credentials: RancherCredentials = field(default_factory=RancherCredentials)
    openstack_credentials: OpenStackCredentials = field(default_factory=OpenStackCredentials)
    rancher_config: RancherConfig = field(default_factory=RancherConfig)
    openstack_config: OpenStackConfig = field(default_factory=OpenStackConfig)
    network_config: NetworkConfig = field(default_factory=NetworkConfig)
    kubernetes_config: KubernetesConfig = field(default_factory=KubernetesConfig)
    deployment_options: DeploymentOptions = field(default_factory=DeploymentOptions)
    yaml_tag = "!DeployConfig"
    yaml_loader = yaml.SafeLoader


def write_deploy_template(path: Path, overwrite: bool) -> None:
    """

    :param path:
    :param overwrite:
    :return:
    """
    logger.debug("Preparing to write deploy template.")

    exists = path.exists()
    if exists:
        if path.is_dir():
            logger.debug("Path is dir, adding 'ironik_template.yaml' as file name.")
            path = path / "ironik_template.yaml"

    exists = path.exists()
    if exists:
        logger.info(f"File {path} already exists.")
        print(f"File {path} already exists.")
        if overwrite:
            logger.info("Replacing existing file with template.")
            print("Replacing existing file with template.")
        else:
            logger.info("Overwrite is not enabled, cannot proceed, stopping.")
            print("Overwrite is not enabled, cannot proceed, stopping.")
            return

    template = DeployConfig()

    logger.debug(f"Opening {path}...")
    with open(path, "w+", encoding="utf-8") as file:
        logger.debug("Attempting to dump template into file...")
        yaml.dump(template, file)
    logger.debug("Closed file.")

    logger.info(f"Template has been written to {path.absolute()}")
    print(f"Template has been written to {path.absolute()}")


# TODO: complete this
def get_template_schema() -> dict:
    schema = {"deployment_options": {"type": "string", "anyof": [{"!DeploymentOptions"}]}}
    return schema


def load_deploy_template(path: Path) -> DeployConfig:
    """

    :param path:
    :return:
    """

    exists = path.exists()
    if not exists:
        logger.info(f"Given path does not exist: {path.absolute()}")
        print(f"Given path does not exist: {path.absolute()}")
        raise IronikFatalError(f"Given path does not exist: {path.absolute()}")

    is_file = path.is_file()
    if not is_file:
        logger.info(f"Given path is not a file: {path.absolute()}")
        print(f"Given path is not a file: {path.absolute()}")
        raise IronikFatalError(f"Given path is not a file: {path.absolute()}")

    logger.debug(f"Attempting to open {path.absolute()}")
    with open(path, "r", encoding="utf-8") as file:
        logger.debug("Attempting to parse file as yaml.")
        try:
            deploy_config = yaml.safe_load(file)
        except yaml.YAMLError as exception:
            logger.info(f"Parsing of yaml file failed with error: {exception}")
            print("Parsing of template failed with the following error:")
            print(exception)
            raise IronikFatalError(f"Parsing of yaml file failed with error: {exception}") from exception
        if not isinstance(deploy_config, DeployConfig):
            logger.info("Could not parse yaml file as Deployment Configuration. Make sure to use the template.")
            print("Could not parse yaml file as Deployment Configuration. Make sure to use the template.")
            logger.debug(f"Type of loaded yaml should be DeployConfig but is {type(DeployConfig)}")
            raise IronikFatalError(
                "Could not parse yaml file as Deployment Configuration. Make sure to use the " "template."
            )

    # TODO: Instead of printing this should validate the config by checking if all attrs are not None and len > 0
    print("Loaded template.")
    # print(deploy_config)
    # TODO: Validate that their is at least one master and one etcd and one worker

    return deploy_config


def validate_deploy_template():
    pass
