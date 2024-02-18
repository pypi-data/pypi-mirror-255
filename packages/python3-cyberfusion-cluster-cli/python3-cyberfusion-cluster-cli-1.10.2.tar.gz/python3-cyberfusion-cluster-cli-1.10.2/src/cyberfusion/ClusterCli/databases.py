"""Databases subcommands."""

from typing import Optional

import typer

from cyberfusion.ClusterCli._utilities import (
    BOOL_MESSAGE,
    CONFIRM_MESSAGE,
    DETAILED_MESSAGE,
    RANDOM_PASSWORD_MESSAGE,
    catch_api_exception,
    console,
    delete_api_object,
    get_object,
    get_support,
    get_usages_plot,
    get_usages_timestamp,
    handle_manual_error,
    print_warning,
    wait_for_task,
)
from cyberfusion.ClusterSupport.database_user_grants import (
    DatabaseUserGrant,
    Privilege,
)
from cyberfusion.ClusterSupport.database_users import (
    DatabaseServerSoftwareName,
    DatabaseUser,
    Host,
)
from cyberfusion.ClusterSupport.databases import Database
from cyberfusion.Common import generate_random_string

app = typer.Typer()


@app.command("list")
@catch_api_exception
def list_(
    detailed: bool = typer.Option(default=False, help=DETAILED_MESSAGE)
) -> None:
    """List databases."""
    console.print(
        get_support().get_table(
            objs=get_support().databases,
            detailed=detailed,
        )
    )


@app.command()
@catch_api_exception
def get(
    name: str,
    detailed: bool = typer.Option(default=False, help=DETAILED_MESSAGE),
) -> None:
    """Show database."""
    console.print(
        get_support().get_table(
            objs=[get_object(get_support().databases, name=name)],
            detailed=detailed,
        )
    )


@app.command()
@catch_api_exception
def list_users(
    detailed: bool = typer.Option(default=False, help=DETAILED_MESSAGE)
) -> None:
    """List database users."""
    console.print(
        get_support().get_table(
            objs=get_support().database_users,
            detailed=detailed,
        )
    )


@app.command()
@catch_api_exception
def get_user(
    id_: int = typer.Argument(metavar="id", default=...),
    detailed: bool = typer.Option(default=False, help=DETAILED_MESSAGE),
) -> None:
    """Show database user."""
    console.print(
        get_support().get_table(
            objs=[get_object(get_support().database_users, id_=id_)],
            detailed=detailed,
        )
    )


@app.command()
@catch_api_exception
def list_user_grants(
    detailed: bool = typer.Option(default=False, help=DETAILED_MESSAGE),
    database_user_id: Optional[int] = typer.Argument(default=None),
) -> None:
    """List user grants."""
    console.print(
        get_support().get_table(
            objs=get_support().get_database_user_grants(
                database_user_id=database_user_id
            ),
            detailed=detailed,
        )
    )


@app.command()
@catch_api_exception
def usage(
    name: str,
    hours_before: Optional[int] = None,
    days_before: Optional[int] = None,
    # Typer has a bug where show_default can't be a string in typer.Option
    # https://github.com/tiangolo/typer/issues/158
    amount: Optional[int] = typer.Option(default=None, show_default="All"),  # type: ignore[call-overload]
) -> None:
    """Show disk usage graph.

    Using --hours-before OR --days-before is required.
    """
    database = get_object(get_support().databases, name=name)

    timestamp, time_unit = get_usages_timestamp(
        days_before=days_before, hours_before=hours_before
    )

    usages = get_support().database_usages(
        database_id=database.id,
        timestamp=timestamp,
        time_unit=time_unit,
    )[:amount]

    typer.echo(get_usages_plot(usages=usages))


@app.command()
@catch_api_exception
def create(
    name: str,
    cluster_name: str,
    server_software: DatabaseServerSoftwareName = typer.Argument(
        default=..., case_sensitive=False
    ),
    optimizing_enabled: bool = typer.Option(
        False, "--optimize/--dont-optimize"
    ),
    backups_enabled: bool = typer.Option(True, "--backup/--dont-backup"),
) -> None:
    """Create database."""
    database = Database(get_support())

    cluster = get_object(get_support().clusters, name=cluster_name)

    database.create(
        name=name,
        server_software_name=server_software.value,
        optimizing_enabled=optimizing_enabled,
        backups_enabled=backups_enabled,
        cluster_id=cluster.id,
    )


@app.command()
@catch_api_exception
def create_user(
    name: str,
    cluster_name: str,
    server_software: DatabaseServerSoftwareName = typer.Argument(
        default=..., case_sensitive=False
    ),
    password: str = typer.Option(
        default=generate_random_string,
        prompt=True,
        hide_input=True,
        show_default=False,
        help=RANDOM_PASSWORD_MESSAGE,
    ),
    user_grant_database_name: Optional[str] = typer.Option(
        default=None, help="Specify this to give user access to a database"
    ),
    user_grant_table: Optional[str] = typer.Option(
        default=None,
        help="Only works in combination with --user-grant-database, omit for all tables",
    ),
    user_grant_privilege: Privilege = typer.Option(
        default=Privilege.ALL,
        help="Only works in combination with --user-grant-database.",
        show_default="ALL",  # type: ignore[call-overload]
        case_sensitive=False,
    ),
) -> None:
    """Create database user."""
    database_user = DatabaseUser(get_support())

    cluster = get_object(get_support().clusters, name=cluster_name)

    host = Host.ALL

    if server_software == DatabaseServerSoftwareName.POSTGRESQL:
        host = None

    database_user.create(
        name=name,
        host=host,
        password=password,
        server_software_name=server_software.value,
        phpmyadmin_firewall_groups_ids=None,
        cluster_id=cluster.id,
    )

    if user_grant_database_name:
        database_user_grant = DatabaseUserGrant(get_support())

        database_user_grant.create(
            database_id=get_object(
                get_support().databases, name=user_grant_database_name
            ).id,
            database_user_id=database_user.id,
            table_name=user_grant_table,
            privilege_name=user_grant_privilege,
        )


@app.command()
@catch_api_exception
def create_user_grant(
    database_user_id: int,
    database_name: str,
    table_name: Optional[str] = typer.Argument(
        default=None, help="Leave empty for all tables"
    ),
    user_grant_privilege: Privilege = typer.Option(
        default=Privilege.ALL,
        show_default="ALL",  # type: ignore[call-overload]
        case_sensitive=False,
    ),
) -> None:
    """Create database user grant."""
    database_user = get_object(
        get_support().database_users, id_=database_user_id
    )
    database = get_object(get_support().databases, name=database_name)

    database_user_grant = DatabaseUserGrant(get_support())

    database_user_grant.create(
        database_id=database.id,
        database_user_id=database_user.id,
        table_name=table_name,
        privilege_name=user_grant_privilege,
    )


@app.command()
@catch_api_exception
def create_all(
    name: str,
    user_name: str,
    cluster_name: str,
    server_software: DatabaseServerSoftwareName = typer.Argument(
        default=..., case_sensitive=False
    ),
    password: str = typer.Option(
        default=generate_random_string,
        prompt=True,
        hide_input=True,
        show_default=False,
        help=RANDOM_PASSWORD_MESSAGE,
    ),
    user_grant_privilege: Privilege = typer.Option(
        default=Privilege.ALL,
        show_default="ALL",  # type: ignore[call-overload]
        case_sensitive=False,
    ),
    optimizing_enabled: bool = typer.Option(
        False, "--optimize/--dont-optimize"
    ),
    backups_enabled: bool = typer.Option(True, "--backup/--dont-backup"),
) -> None:
    """Create database with user and user grant."""
    cluster = get_object(get_support().clusters, name=cluster_name)

    # Prevent a database from being created when the user already exists. There
    # is no need to check for the database itself. If it already exists, the API
    # will return an error on creation

    if get_support().get_database_users(name=user_name, cluster_id=cluster.id):
        handle_manual_error("Database user already exists")

    database = Database(get_support())
    database_user = DatabaseUser(get_support())
    database_user_grant = DatabaseUserGrant(get_support())

    host = Host.ALL

    if server_software == DatabaseServerSoftwareName.POSTGRESQL:
        host = None

    database.create(
        name=name,
        server_software_name=server_software.value,
        cluster_id=cluster.id,
        optimizing_enabled=optimizing_enabled,
        backups_enabled=backups_enabled,
    )

    database_user.create(
        name=user_name,
        host=host,
        password=password,
        server_software_name=server_software.value,
        phpmyadmin_firewall_groups_ids=None,
        cluster_id=cluster.id,
    )

    if server_software == DatabaseServerSoftwareName.MARIADB:
        database_user_grant.create(
            database_id=database.id,
            database_user_id=database_user.id,
            table_name=None,
            privilege_name=user_grant_privilege,
        )
    else:
        print_warning(
            "Skipping database user grant. This is only supported on MariaDB servers."
        )


@app.command()
@catch_api_exception
def update_user_password(
    user_id: int,
    password: str = typer.Option(
        default=generate_random_string,
        prompt=True,
        hide_input=True,
        show_default=False,
        help=RANDOM_PASSWORD_MESSAGE,
    ),
) -> None:
    """Update database user password."""
    database_user = get_object(get_support().database_users, id_=user_id)

    database_user.password = password
    database_user.update()


@app.command()
@catch_api_exception
def update_backups(
    name: str,
    state: bool = typer.Argument(default=..., help=BOOL_MESSAGE),
) -> None:
    """Update backups."""
    database = get_object(get_support().databases, name=name)

    database.backups_enabled = state
    database.update()


@app.command()
@catch_api_exception
def update_optimizing(
    name: str,
    state: bool = typer.Argument(default=..., help=BOOL_MESSAGE),
) -> None:
    """Update optimizing."""
    database = get_object(get_support().databases, name=name)

    if not database.server_software_name == DatabaseServerSoftwareName.MARIADB:
        print_warning(
            "Optimizing is compatible only with the MariaDB server software."
        )

        return

    database.optimizing_enabled = state
    database.update()


@app.command()
@catch_api_exception
def delete(
    name: str,
    confirm: bool = typer.Option(
        default=False,
        help=CONFIRM_MESSAGE,
    ),
) -> None:
    """Delete database."""
    database = get_object(get_support().databases, name=name)

    delete_api_object(obj=database, confirm=confirm)


@app.command()
@catch_api_exception
def delete_user(
    id_: int = typer.Argument(metavar="id", default=...),
    confirm: bool = typer.Option(
        default=False,
        help=CONFIRM_MESSAGE,
    ),
) -> None:
    """Delete database user."""
    database_user = get_object(get_support().database_users, id_=id_)

    delete_api_object(obj=database_user, confirm=confirm)


@app.command()
@catch_api_exception
def sync(
    left_database_name: str,
    right_database_name: str,
) -> None:
    """Sync database."""
    left_database = get_object(
        get_support().databases, name=left_database_name
    )
    right_database = get_object(
        get_support().databases, name=right_database_name
    )

    task_collection = left_database.sync(right_database_id=right_database.id)

    wait_for_task(task_collection_uuid=task_collection.uuid)


@app.command()
@catch_api_exception
def compare(
    left_database_name: str,
    right_database_name: str,
    sort_alphabetically: bool = typer.Option(default=True),
) -> None:
    """Compare databases."""
    left_database = get_object(
        get_support().databases, name=left_database_name
    )
    right_database = get_object(
        get_support().databases, name=right_database_name
    )

    (
        _identical_tables_names,
        _not_identical_tables_names,
        _only_left_tables_names,
        _only_right_tables_names,
    ) = left_database.get_comparison(right_database_id=right_database.id)

    console.print(
        get_support().get_comparison_table(
            left_column_name="Table",
            left_label=left_database.name,
            right_label=right_database.name,
            identical=_identical_tables_names,
            different=_not_identical_tables_names,
            left_only=_only_left_tables_names,
            right_only=_only_right_tables_names,
            sort_alphabetically=sort_alphabetically,
        )
    )
