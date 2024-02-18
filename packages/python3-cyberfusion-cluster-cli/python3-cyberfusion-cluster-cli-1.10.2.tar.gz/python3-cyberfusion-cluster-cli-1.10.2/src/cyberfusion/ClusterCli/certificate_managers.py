"""certificate managers subcommands."""

from typing import List, Optional

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
from cyberfusion.ClusterSupport.certificate_managers import (
    CertificateManager,
    ProviderName,
)

app = typer.Typer()


@app.command("list")
@catch_api_exception
def list_(
    detailed: bool = typer.Option(default=False, help=DETAILED_MESSAGE),
    deleted: bool = typer.Option(
        default=False, help="Show soft deleted certificate managers"
    ),
) -> None:
    """List certificate managers."""
    if deleted:
        certificate_managers = [
            certificate_manager
            for certificate_manager in get_support().certificate_managers
            if certificate_manager.deleted_at is not None
        ]
    else:
        certificate_managers = [
            certificate_manager
            for certificate_manager in get_support().certificate_managers
            if certificate_manager.deleted_at is None
        ]

    console.print(
        get_support().get_table(
            objs=certificate_managers,
            detailed=detailed,
        )
    )


@app.command()
@catch_api_exception
def get(
    main_common_name: str,
    detailed: bool = typer.Option(default=False, help=DETAILED_MESSAGE),
) -> None:
    """Get certificate manager."""
    console.print(
        get_support().get_table(
            objs=[
                get_object(
                    get_support().certificate_managers,
                    main_common_name=main_common_name,
                )
            ],
            detailed=detailed,
        )
    )


@app.command()
@catch_api_exception
def create(common_names: List[str], cluster_name: str) -> None:
    """Create certificate manager."""
    certificate_manager = CertificateManager(get_support())

    cluster = get_object(get_support().clusters, name=cluster_name)

    certificate_manager.create(
        common_names=common_names,
        provider_name=ProviderName.LETS_ENCRYPT,
        request_callback_url=None,
        cluster_id=cluster.id,
    )


@app.command()
@catch_api_exception
def request(main_common_name: str) -> None:
    """Request certificate."""
    certificate_manager = get_object(
        get_support().certificate_managers, main_common_name=main_common_name
    )

    task_collection = certificate_manager.request()

    wait_for_task(task_collection_uuid=task_collection.uuid)


@app.command()
@catch_api_exception
def update_request_callback_url(
    main_common_name: str,
    request_callback_url: Optional[str] = typer.Argument(
        default=None, help=EMTPY_TO_CLEAR_MESSAGE
    ),
) -> None:
    """Update request callback URL."""
    certificate_manager = get_object(
        get_support().certificate_managers, main_common_name=main_common_name
    )

    certificate_manager.request_callback_url = request_callback_url
    certificate_manager.update()


@app.command()
@catch_api_exception
def delete(
    main_common_name: str,
    confirm: bool = typer.Option(
        default=False,
        help=CONFIRM_MESSAGE,
    ),
) -> None:
    """Delete certificate manager."""
    certificate_manager = get_object(
        get_support().certificate_managers, main_common_name=main_common_name
    )

    delete_api_object(obj=certificate_manager, confirm=confirm)


@app.command()
@catch_api_exception
def restore(
    main_common_name: str,
) -> None:
    """Restore certificate manager."""
    certificate_manager = get_object(
        get_support().certificate_managers,
        main_common_name=main_common_name,
    )

    certificate_manager.restore()
