"""Firewall Groups subcommands."""

from typing import List

import typer

from cyberfusion.ClusterCli._utilities import (
    CONFIRM_MESSAGE,
    DETAILED_MESSAGE,
    catch_api_exception,
    console,
    delete_api_object,
    exit_with_status,
    get_object,
    get_support,
    handle_manual_error,
    print_warning,
)
from cyberfusion.ClusterSupport.firewall_groups import FirewallGroup

app = typer.Typer()


@app.command("list")
@catch_api_exception
def list_(
    detailed: bool = typer.Option(default=False, help=DETAILED_MESSAGE),
) -> None:
    """List firewall groups."""
    console.print(
        get_support().get_table(
            objs=get_support().firewall_groups, detailed=detailed
        )
    )


@app.command()
@catch_api_exception
def get(
    name: str,
    detailed: bool = typer.Option(default=False, help=DETAILED_MESSAGE),
) -> None:
    """Show firewall group."""
    console.print(
        get_support().get_table(
            objs=[get_object(get_support().firewall_groups, name=name)],
            detailed=detailed,
        )
    )


@app.command()
@catch_api_exception
def create(
    name: str,
    cluster_name: str,
    ip_networks: List[str],
) -> None:
    """Create firewall group."""
    firewall_group = FirewallGroup(get_support())

    cluster = get_object(get_support().clusters, name=cluster_name)

    firewall_group.create(
        name=name, ip_networks=ip_networks, cluster_id=cluster.id
    )


@app.command()
@catch_api_exception
def add_ip_networks(name: str, ip_networks: List[str]) -> None:
    """Add IP networks."""
    firewall_group = get_object(get_support().firewall_groups, name=name)

    firewall_group.ip_networks.extend(ip_networks)
    firewall_group.update()


@app.command()
@catch_api_exception
@exit_with_status
def remove_ip_networks(name: str, ip_networks: List[str]) -> int:
    """Remove IP networks."""
    firewall_group = get_object(get_support().firewall_groups, name=name)

    exit_code = 0
    success = False

    for ip_network in ip_networks:
        try:
            firewall_group.ip_networks.remove(ip_network)
            success = True
        except ValueError:
            print_warning(f"IP network '{ip_network}' not found, skipping.")
            exit_code = 64

    if not success:
        handle_manual_error("No IP networks have been removed")

    firewall_group.update()

    return exit_code


@app.command()
@catch_api_exception
def delete(
    name: str,
    confirm: bool = typer.Option(
        default=False,
        help=CONFIRM_MESSAGE,
    ),
) -> None:
    """Delete firewall group."""
    firewall_group = get_object(get_support().firewall_groups, name=name)

    delete_api_object(obj=firewall_group, confirm=confirm)
