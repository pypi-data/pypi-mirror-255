"""Domain Routers subcommands."""

from typing import Optional

import typer

from cyberfusion.ClusterCli._utilities import (
    BOOL_MESSAGE,
    DETAILED_MESSAGE,
    EMTPY_TO_CLEAR_MESSAGE,
    catch_api_exception,
    console,
    get_object,
    get_support,
)

app = typer.Typer()


@app.command("list")
@catch_api_exception
def list_(
    detailed: bool = typer.Option(default=False, help=DETAILED_MESSAGE),
) -> None:
    """List domain routers."""
    console.print(
        get_support().get_table(
            objs=get_support().domain_routers, detailed=detailed
        )
    )


@app.command()
@catch_api_exception
def get(
    domain: str,
    detailed: bool = typer.Option(default=False, help=DETAILED_MESSAGE),
) -> None:
    """Show domain router."""
    console.print(
        get_support().get_table(
            objs=[get_object(get_support().domain_routers, domain=domain)],
            detailed=detailed,
        )
    )


@app.command()
@catch_api_exception
def update_force_ssl(
    domain: str,
    state: bool = typer.Argument(default=..., help=BOOL_MESSAGE),
) -> None:
    """Update force SSL."""
    domain_router = get_object(get_support().domain_routers, domain=domain)

    domain_router.force_ssl = state
    domain_router.update()


@app.command()
@catch_api_exception
def update_certificate(
    domain: str,
    certificate_id: Optional[int] = typer.Argument(
        default=None, help=EMTPY_TO_CLEAR_MESSAGE
    ),
) -> None:
    """Update certificate."""
    domain_router = get_object(get_support().domain_routers, domain=domain)

    domain_router.certificate_id = certificate_id
    domain_router.update()


@app.command()
@catch_api_exception
def update_node(
    domain: str,
    node_hostname: Optional[str] = typer.Argument(
        default=None, help=EMTPY_TO_CLEAR_MESSAGE
    ),
) -> None:
    """Update node."""
    domain_router = get_object(get_support().domain_routers, domain=domain)

    if node_hostname is not None:
        node = get_object(get_support().nodes, hostname=node_hostname)
        domain_router.node_id = node.id
    else:
        domain_router.node_id = None

    domain_router.update()


@app.command()
@catch_api_exception
def update_security_txt_policy(
    domain: str,
    security_txt_policy_id: Optional[int] = typer.Argument(
        default=None, help=EMTPY_TO_CLEAR_MESSAGE
    ),
) -> None:
    """Update security.txt policy."""
    domain_router = get_object(get_support().domain_routers, domain=domain)

    domain_router.security_txt_policy_id = security_txt_policy_id
    domain_router.update()
