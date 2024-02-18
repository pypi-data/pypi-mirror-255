"""Nodes subcommands."""

from typing import Any, List, Optional

import typer

from cyberfusion.ClusterCli._utilities import (
    CONFIRM_MESSAGE,
    DETAILED_MESSAGE,
    EMTPY_TO_CLEAR_MESSAGE,
    catch_api_exception,
    console,
    delete_api_object,
    get_object,
    get_support,
    wait_for_task,
)
from cyberfusion.ClusterSupport.nodes import Node, NodeGroup

app = typer.Typer()


@app.command("list")
@catch_api_exception
def list_(
    detailed: bool = typer.Option(default=False, help=DETAILED_MESSAGE)
) -> None:
    """List nodes."""
    console.print(
        get_support().get_table(objs=get_support().nodes, detailed=detailed)
    )


@app.command()
@catch_api_exception
def get(
    hostname: str,
    detailed: bool = typer.Option(default=False, help=DETAILED_MESSAGE),
) -> None:
    """Show node."""
    console.print(
        get_support().get_table(
            objs=[get_object(get_support().nodes, hostname=hostname)],
            detailed=detailed,
        )
    )


@app.command()
@catch_api_exception
def create(
    cluster_name: str,
    product: str,
    groups: List[NodeGroup] = typer.Option(..., "--group", show_default=False),
    comment: Optional[str] = typer.Option(default=None),
) -> None:
    """Create node."""
    node = Node(get_support())

    cluster = get_object(get_support().clusters, name=cluster_name)

    groups_properties: dict[NodeGroup, Optional[dict[str, Any]]] = {}

    for group in [NodeGroup.REDIS, NodeGroup.MARIADB]:
        if group in groups:
            existing_nodes = get_support().get_nodes(
                cluster_id=cluster.id, groups=group
            )

            groups_properties[group] = {"is_master": len(existing_nodes) == 0}
        else:
            groups_properties[group] = None

    task_collection = node.create(
        groups=groups,
        comment=comment,
        load_balancer_health_checks_groups_pairs={},
        groups_properties=groups_properties,
        cluster_id=cluster.id,
        product=product,
    )

    wait_for_task(task_collection_uuid=task_collection.uuid)


@app.command()
@catch_api_exception
def add_groups(hostname: str, groups: List[NodeGroup]) -> None:
    """Add groups."""
    node = get_object(get_support().nodes, hostname=hostname)

    groups_properties = node.groups_properties

    for group in [NodeGroup.REDIS, NodeGroup.MARIADB]:
        # Skip if the group isn't added, or the node already has this group

        if group not in groups or group in node.groups:
            continue

        existing_nodes = get_support().get_nodes(
            cluster_id=node.cluster_id, groups=group
        )

        groups_properties[group] = {"is_master": len(existing_nodes) == 0}

    node.groups.extend(groups)
    node.groups_properties = groups_properties
    node.update()


@app.command()
@catch_api_exception
def update_comment(
    hostname: str,
    comment: Optional[str] = typer.Argument(
        default=None, help=EMTPY_TO_CLEAR_MESSAGE
    ),
) -> None:
    """Update comment."""
    node = get_object(get_support().nodes, hostname=hostname)

    node.comment = comment
    node.update()


@app.command()
@catch_api_exception
def get_health_checks(
    hostname: str,
) -> None:
    """Get health checks for node."""
    node = get_object(get_support().nodes, hostname=hostname)

    for group in node.load_balancer_health_checks_groups_pairs:
        console.print(
            f"{group}: {', '.join(node.load_balancer_health_checks_groups_pairs[group])}"
        )


@app.command()
@catch_api_exception
def set_health_check(
    hostname: str,
    primary_group: NodeGroup,
    additional_groups: List[NodeGroup] = typer.Argument(
        default=None, help=EMTPY_TO_CLEAR_MESSAGE
    ),
) -> None:
    """Set health check for group."""
    node = get_object(get_support().nodes, hostname=hostname)

    if not additional_groups:
        del node.load_balancer_health_checks_groups_pairs[primary_group]
    else:
        node.load_balancer_health_checks_groups_pairs[primary_group] = (
            additional_groups
        )

    node.update()


@app.command()
@catch_api_exception
def delete(
    hostname: str,
    confirm: bool = typer.Option(
        default=False,
        help=CONFIRM_MESSAGE,
    ),
) -> None:
    """Delete node."""
    node = get_object(get_support().nodes, hostname=hostname)

    delete_api_object(obj=node, confirm=confirm)
