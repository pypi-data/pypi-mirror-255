"""
Command-line interface.

:author: Jonathan Decker
"""

import datetime
import logging
import time
from pathlib import Path

import click
from rich import print

import ironik
from ironik.cli import cli_helper
from ironik.config_file_handler import deploy_template
from ironik.openstack_handler import openstack_api_caller, resource_calculator
from ironik.rancher import rancher_api_caller
from ironik.util import exceptions
from ironik.util.ironik_logger import setup_logger

logger = logging.getLogger("logger")


def print_version(context: click.Context, _, value):
    """

    :param context:
    :param _:
    :param value:
    :return:
    """
    if not value or context.resilient_parsing:
        return
    try:
        print(f"[bold blue]ironik version {ironik.__version__} by {ironik.__author__} ({ironik.__email__})")
        context.exit()
    except click.ClickException:
        context.fail("An error occurred while fetching ironik version number!")


@click.group()
@click.option(
    "--version",
    is_flag=True,
    callback=print_version,
    expose_value=False,
    is_eager=True,
    help="Print the current version of ironik installed.",
)
@click.option("-v", "--verbose", "--debug", is_flag=True, default=False, help="Enable verbose debug logging.")
def ironik_cli(verbose=False):
    """

    :param verbose:
    :return:
    """

    if verbose:
        print("Running in verbose mode, extensive logging is active.")
        setup_logger(console_level=logging.DEBUG, log_file_level=logging.DEBUG)
    else:
        setup_logger(console_level=logging.ERROR, log_file_level=logging.INFO)

    if verbose:
        logger.debug("Running in verbose mode, extensive logging is active.")


@ironik_cli.command(name="dummy", short_help="This is a dummy test command.", hidden=True)
def dummy() -> None:
    """

    :return:
    """
    print("Dummy command")


@ironik_cli.command(
    name="deploy",
    short_help="Deploy a new Kubernetes cluster using the given configuration.\n"
    "Requires a name for the cluster to be given as well as a filled out template.",
)
@click.argument("name", type=str, required=True)
@click.argument("path", type=click.Path(path_type=Path), required=True)
@click.option("-d", "--dry-run", is_flag=True, default=False, help="Start dry-run, no data will be written.")
@click.option("-y", "--yes", is_flag=True, default=False, help="Bypass confirmation before deployment.")
def deploy(name: str, path: Path, dry_run: bool, yes: bool) -> None:
    """

    :param name:
    :param path:
    :param dry_run:
    :param yes:
    :return:
    """

    logger.debug(f"Deploy called for name: {name} and {path}")

    if dry_run:
        print("Running in dry-run mode, no data will be written.")
        logger.debug("Running in dry-run mode, no data will be written.")

    if yes:
        logger.debug("Confirmation bypass is enabled.")

    try:
        name = cli_helper.check_and_prepare_cluster_name(name)

        # Load template from given path
        deploy_config = deploy_template.load_deploy_template(path)

        # Query missing parameter
        # Later with Feature: Prompts

        # Validate Rancher credentials
        rancher_session = rancher_api_caller.create_and_test_rancher_session(
            deploy_config.rancher_credentials, deploy_config.rancher_config
        )
        # Validate OpenStack credentials
        openstack_connection = openstack_api_caller.create_and_test_openstack_connection(
            deploy_config.openstack_credentials, deploy_config.openstack_config
        )

        print("Credential validation successful!")
        logger.info("Credential validation successful!")

        # Fetch OpenStack resources
        # Later with Feature: Remove

        # Validate request cluster against available resources
        # Check if flavor exists in OS
        flavors = openstack_api_caller.get_openstack_flavors(openstack_connection)
        logger.debug(
            f"Checking if given flavor {deploy_config.openstack_config.default_flavor_name} "
            f"is among available flavors."
        )

        if not cli_helper.validate_key_in_dict(deploy_config.openstack_config.default_flavor_name, flavors):
            raise exceptions.IronikFatalError("Could not find given flavor.")

        # Check if image exists in OS
        images = openstack_api_caller.get_openstack_images(openstack_connection)
        logger.debug(
            f"Checking if given image {deploy_config.openstack_config.default_image_name} "
            f"is among available images."
        )

        if not cli_helper.validate_key_in_dict(deploy_config.openstack_config.default_image_name, images):
            raise exceptions.IronikFatalError("Could not find given image.")

        # Calculate projected resource consumption against available resources in OS
        if not resource_calculator.preprocess_and_calculate_resource_consumption(
            deploy_config.openstack_config,
            deploy_config.deployment_options,
            deploy_config.kubernetes_config,
            openstack_connection,
            flavors,
            images,
        ):
            raise exceptions.IronikFatalError("Insufficient resources available on OpenStack.")

        # Lookup public and private network id in OS
        public_network, private_networks = openstack_api_caller.get_openstack_public_and_private_networks(
            openstack_connection
        )
        public_network_id = public_network.get("id")
        logging.info(f"Found public network id: {public_network_id}")
        print(f"Found public network id: {public_network_id}")

        if deploy_config.openstack_config.private_network_id not in map(lambda key: key.get("id"), private_networks):
            raise exceptions.IronikFatalError(
                f"Could not find given private network id on OpenStack. "
                f"Found private network ids are: "
                f"{map(lambda key: key.get('id'), private_networks)}"
            )

        if public_network_id is None or len(public_network_id) == 0:
            raise exceptions.IronikFatalError("Could not find the public network id in OpenStack.")

        # Get router id
        routers = openstack_api_caller.get_openstack_routers(openstack_connection)
        router_id = cli_helper.get_router_id_from_routers(public_network_id, routers)

        # Get subnet id
        subnet_id = openstack_api_caller.match_subnet(
            openstack_connection, deploy_config.openstack_config.private_network_id
        ).get("id", None)
        if subnet_id is None or len(subnet_id) == 0:
            raise exceptions.IronikFatalError(
                f"Could not find valid subnet id for private network:"
                f" {deploy_config.openstack_config.private_network_id}"
            )

        # Get confirmation before beginning deployment
        if dry_run:
            print("Dry Run ends here.")
            return

        if yes:
            print("-y flag was set, bypassing confirmation and beginning deployment.")
        else:
            if not click.confirm(
                "Please confirm that the deployment will begin and resources in Openstack"
                " will be allocated\nand the necessary resources in Openstack and Rancher"
                " will be created.",
                default=False,
            ):
                raise exceptions.IronikFatalError("No deployment start confirmation received.")

        # Save OpenStack resources before deployment
        # Later with Feature: Remove

        # Create or reuse OpenStack security group
        if not openstack_api_caller.create_openstack_security_group(
            openstack_connection, deploy_config.openstack_config, deploy_config.network_config, name
        ):
            raise exceptions.IronikFatalError(
                f"Creating security group " f"{deploy_config.openstack_config.security_group_name} failed."
            )

        # Create Node template in Rancher
        iso_time_stamp = datetime.datetime.now().isoformat()[:-7]
        node_template_name = name + "-" + iso_time_stamp
        logger.info(f"Creating node template with name {node_template_name}")
        print(f"Creating node template with name '{node_template_name}'")
        node_template_id = rancher_api_caller.create_rancher_node_template(
            rancher_session,
            deploy_config.openstack_credentials,
            deploy_config.openstack_config,
            deploy_config.rancher_config,
            node_template_name,
        )

        logger.info(f"Created node template with id {node_template_id}")
        print(f"Created node template with id '{node_template_id}'")

        # Fill out RKE template
        rke_template = rancher_api_caller.get_rke_template(
            deploy_config.kubernetes_config, deploy_config.network_config
        )

        # Create cluster in Rancher
        cluster_id = rancher_api_caller.create_rancher_cluster(
            rancher_session, deploy_config.rancher_config, name, iso_time_stamp, rke_template
        )
        logger.info(f"Created cluster with name {name} and id {cluster_id}")
        print(f"Created cluster with name '{name}' and id '{cluster_id}'")

        # Wait a moment for Rancher to propagate the new cluster internally
        time.sleep(5)

        # Create master node pool
        master_node_pool_id = rancher_api_caller.create_rancher_node_pool(
            rancher_session,
            name,
            cluster_id,
            node_template_id,
            True,
            deploy_config.kubernetes_config,
            deploy_config.rancher_config,
        )
        print(f"Created master node pool with id '{master_node_pool_id}'")

        # Create worker node pool
        worker_node_pool_id = rancher_api_caller.create_rancher_node_pool(
            rancher_session,
            name,
            cluster_id,
            node_template_id,
            False,
            deploy_config.kubernetes_config,
            deploy_config.rancher_config,
        )
        print(f"Created worker node pool with id '{worker_node_pool_id}'")

        # Wait for nodes and cluster to be ready
        print("Waiting for nodes to be ready. This takes usually around 8 to 10 minutes...")

        if not cli_helper.wait_for_nodes_ready(
            deploy_config.kubernetes_config, deploy_config.rancher_config, rancher_session, cluster_id
        ):
            raise exceptions.IronikFatalError("Reached timeout while waiting for nodes to be ready.")

        logger.info("All nodes are now ready.")
        print("All nodes are now ready.")

        # Wait for cluster to be ready
        print("Waiting for cluster to be ready...")
        if not cli_helper.wait_for_cluster_ready(deploy_config.rancher_config, rancher_session, cluster_id):
            raise exceptions.IronikFatalError("Reached timeout while waiting for cluster to be ready.")

        # Create new Rancher user or make existing user cluster owner
        if cli_helper.update_rancher_user(deploy_config.rancher_config, rancher_session, cluster_id):
            logger.debug("Finished updating Rancher user.")
            print("Finished updating Rancher user.")
        else:
            print("Updating the Rancher user failed, please create a new cluster owner manually.")

        if not cli_helper.handle_kubernetes_setup(
            deploy_config.openstack_credentials,
            deploy_config.openstack_config,
            deploy_config.rancher_config,
            rancher_session,
            cluster_id,
            subnet_id,
            public_network_id,
            router_id,
        ):
            print("Applying Kubernetes manifests failed. Please manually apply the manifests.")

        # Fetch OpenStack resources again
        # Later with Feature: Remove

        # Determine what resources were created
        # Later with Feature: Remove

        # Save created resources to a file
        # Later with Feature: Remove

        # Deploy a sample workload if requested

        # Validate that it works

        # Deploy a load balancer if requested

        # Validate that it works

        # Expose the sample workload if it was deployed along with a load balancer

        # Validate that the workload is reachable

        # Deploy a database with a sample volume

        # Validate that the volume was created in OpenStack

        # Clean up resources as configured

        # Show what was done

        # Done
        print("Done!")
    except exceptions.IronikFatalError as exception:
        print(exception)


@ironik_cli.command(
    name="template", short_help="Spawn a yaml configuration file template. Give path with -f or use current directory."
)
@click.argument("path", type=click.Path(writable=True, path_type=Path), default=Path.cwd(), required=False)
@click.option(
    "-o",
    "--overwrite",
    is_flag=True,
    type=bool,
    default=False,
    help="Enable overwriting of existing file when creating template.",
)
def template(path: Path, overwrite: bool) -> None:
    """

    :param path:
    :param overwrite:
    :return:
    """
    print(f"Preparing to write template to {path}")
    logger.debug(f"Given path for template: {path}")

    deploy_template.write_deploy_template(path, overwrite)
