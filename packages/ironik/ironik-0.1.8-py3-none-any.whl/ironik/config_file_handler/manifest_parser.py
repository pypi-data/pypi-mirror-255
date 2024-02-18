"""

:author: Jonathan Decker
"""

import logging
import os
import pathlib

import yaml

from ironik.config_file_handler.deploy_template import OpenStackConfig
from ironik.util import exceptions

logger = logging.getLogger("logger")

CLOUD_CONTROLLER_MANAGER_ROLES_MANIFEST = "cloud-controller-manager-roles.yaml"

CLOUD_CONTROLLER_MANAGER_ROLE_BINDINGS_MANIFEST = "cloud-controller-manager-role-bindings.yaml"

OPENSTACK_CLOUD_CONTROLLER_MANAGER_DS_MANIFEST = "openstack-cloud-controller-manager-ds.yaml"

CSI_PLUGIN_MANIFEST = "cinder-csi-plugin.yaml"

path_to_self = pathlib.Path(os.path.abspath(__file__))
path_to_manifests = path_to_self.parent.parent / "manifests"


def get_manifest_path(manifest: str) -> pathlib.Path:
    path = pathlib.Path(path_to_manifests / manifest)
    if path.is_file():
        return path
    raise exceptions.IronikPassingError(f"Could not find manifest {manifest} in {path}")


def get_openstack_controller_manager_manifest(openstack_config: OpenStackConfig) -> list[dict]:
    """

    Args:
        openstack_config:

    Returns:

    """
    path = get_manifest_path(OPENSTACK_CLOUD_CONTROLLER_MANAGER_DS_MANIFEST)
    with open(path, "r", encoding="utf-8") as file:
        yaml_dicts = list(x for x in yaml.safe_load_all(file))
    target_dict = yaml_dicts[1]
    target_entry_list = target_dict["spec"]["template"]["spec"]["containers"][0]["args"]
    target_entry_list.pop()
    value_to_insert = f"--cluster-cidr={openstack_config.remote_ip_prefix}"
    target_entry_list.append(value_to_insert)

    return yaml_dicts


def get_cloud_controller_roles_manifest() -> dict:
    path = get_manifest_path(CLOUD_CONTROLLER_MANAGER_ROLES_MANIFEST)
    with open(path, "r", encoding="utf-8") as file:
        yaml_dict = yaml.safe_load(file)
    return yaml_dict


def get_cloud_controller_role_bindings_manifest() -> dict:
    path = get_manifest_path(CLOUD_CONTROLLER_MANAGER_ROLE_BINDINGS_MANIFEST)
    with open(path, "r", encoding="utf-8") as file:
        yaml_dict = yaml.safe_load(file)
    return yaml_dict


def get_csi_plugin_manifest() -> list[dict]:
    path = get_manifest_path(CSI_PLUGIN_MANIFEST)
    with open(path, "r", encoding="utf-8") as file:
        yaml_dicts = list(x for x in yaml.safe_load_all(file))
    return yaml_dicts
