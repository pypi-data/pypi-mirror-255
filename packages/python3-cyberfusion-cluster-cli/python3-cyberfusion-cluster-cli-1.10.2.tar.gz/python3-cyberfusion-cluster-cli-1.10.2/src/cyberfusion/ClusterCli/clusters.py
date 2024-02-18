"""Clusters subcommands."""

import json
from typing import Any, List, Optional, Union

import typer
from rich.panel import Panel
from rich.table import Table

from cyberfusion.ClusterCli._utilities import (
    BOOL_MESSAGE,
    CONFIRM_MESSAGE,
    DETAILED_MESSAGE,
    EMTPY_TO_CLEAR_MESSAGE,
    RANDOM_PASSWORD_MESSAGE,
    catch_api_exception,
    console,
    delete_api_object,
    exit_with_status,
    get_object,
    get_support,
    get_usages_plot,
    get_usages_timestamp,
    handle_manual_error,
    print_warning,
)
from cyberfusion.ClusterSupport import Cluster
from cyberfusion.ClusterSupport.clusters import (
    ClusterGroup,
    PHPExtension,
    UNIXUserHomeDirectory,
)
from cyberfusion.Common import generate_random_string

app = typer.Typer()

HELP_PANEL_SHOW = "Show cluster"
HELP_PANEL_UPDATE = "Update cluster"


@app.command("list")
@catch_api_exception
def list_(
    detailed: bool = typer.Option(default=False, help=DETAILED_MESSAGE)
) -> None:
    """List clusters."""
    console.print(
        get_support().get_table(objs=get_support().clusters, detailed=detailed)
    )


@app.command(rich_help_panel=HELP_PANEL_SHOW)
@catch_api_exception
def get(
    name: str,
    detailed: bool = typer.Option(default=False, help=DETAILED_MESSAGE),
) -> None:
    """Show cluster."""
    console.print(
        get_support().get_table(
            objs=[get_object(get_support().clusters, name=name)],
            detailed=detailed,
        )
    )


@app.command(rich_help_panel=HELP_PANEL_SHOW)
@catch_api_exception
def get_borg_ssh_key(
    name: str,
) -> None:
    """Show Borg SSH key."""
    cluster = get_object(get_support().clusters, name=name)

    console.print(cluster.get_borg_public_ssh_key())


def _parse_json_to_dict(value: Union[str, None]) -> dict[str, Any]:
    """Convert the JSON input to a Dict."""
    if value is None:
        return {}

    return json.loads(value)


@app.command()
@catch_api_exception
def create(
    customer_team_code: Optional[str] = typer.Option(
        default=None, help="Do not set unless superuser"
    ),
    groups: List[ClusterGroup] = typer.Option(
        ..., "--group", show_default=False
    ),
    description: str = typer.Option(default=...),
    kernelcare_license_key: Optional[str] = typer.Option(default=None),
    unix_users_home_directory: Optional[UNIXUserHomeDirectory] = typer.Option(
        default=None, help="Groups: Web, Mail, Borg Server", show_default=False
    ),
    sync_toolkit_enabled: bool = typer.Option(
        False, "--with-sync-toolkit", help="Groups: Web, Database"
    ),
    php_versions: List[str] = typer.Option(
        default=[], rich_help_panel="Group: Web"
    ),
    php_settings: str = typer.Option(
        default=None, rich_help_panel="Group: Web"
    ),
    custom_php_modules_names: List[PHPExtension] = typer.Option(
        default=[], rich_help_panel="Group: Web"
    ),
    php_ioncube_enabled: bool = typer.Option(
        False, "--with-php-ioncube", rich_help_panel="Group: Web"
    ),
    php_sessions_spread_enabled: bool = typer.Option(
        False, "--with-php-sessions-spread", rich_help_panel="Group: Web"
    ),
    nodejs_version: Optional[int] = typer.Option(
        default=None, rich_help_panel="Group: Web"
    ),
    nodejs_versions: List[str] = typer.Option(
        default=[], rich_help_panel="Group: Web"
    ),
    wordpress_toolkit_enabled: bool = typer.Option(
        False, "--with-wordpress-toolkit", rich_help_panel="Group: Web"
    ),
    bubblewrap_toolkit_enabled: bool = typer.Option(
        False, "--with-bubblewrap-toolkit", rich_help_panel="Group: Web"
    ),
    malware_toolkit_enabled: bool = typer.Option(
        False, "--with-malware-toolkit", rich_help_panel="Group: Web"
    ),
    malware_toolkit_scans_enabled: bool = typer.Option(
        False, "--with-malware-toolkit-scans", rich_help_panel="Group: Web"
    ),
    mariadb_version: Optional[str] = typer.Option(
        default=None, rich_help_panel="Group: Database"
    ),
    mariadb_cluster_name: Optional[str] = typer.Option(
        default=None, rich_help_panel="Group: Database"
    ),
    mariadb_backup_interval: Optional[int] = typer.Option(
        default=None, rich_help_panel="Group: Database"
    ),
    postgresql_version: Optional[int] = typer.Option(
        default=None, rich_help_panel="Group: Database"
    ),
    postgresql_backup_interval: Optional[int] = typer.Option(
        default=None, rich_help_panel="Group: Database"
    ),
    redis_password: Optional[str] = typer.Option(
        default=generate_random_string,
        prompt=True,
        hide_input=True,
        show_default=False,
        help=RANDOM_PASSWORD_MESSAGE,
        rich_help_panel="Group: Database",
    ),
    redis_memory_limit: Optional[int] = typer.Option(
        default=None, rich_help_panel="Group: Database"
    ),
    database_toolkit_enabled: bool = typer.Option(
        False, "--with-database-toolkit", rich_help_panel="Group: Database"
    ),
    automatic_borg_repositories_prune_enabled: bool = typer.Option(
        False,
        "--with-automatic-borg-repositories-prune",
        rich_help_panel="Group: Borg Client",
    ),
    http_retry_properties: str = typer.Option(
        default=None, rich_help_panel="Group: Web"
    ),
) -> None:
    """Create cluster."""
    cluster = Cluster(get_support())

    if customer_team_code:
        if not get_support().is_superuser:
            handle_manual_error(
                "Customer team code must be unset when not superuser"
            )

        customer_id = get_object(
            get_support().customers, team_code=customer_team_code
        ).id
    else:
        if get_support().is_superuser:
            handle_manual_error(
                "Customer team code must be set when superuser"
            )

        customer_id = get_support().customer_id

    php_settings_dict = _parse_json_to_dict(php_settings)
    http_retry_properties_dict = _parse_json_to_dict(http_retry_properties)

    if ClusterGroup.DB not in groups:
        redis_password = None  # Reset default value

    cluster.create(
        customer_id=customer_id,
        groups=groups,
        description=description,
        kernelcare_license_key=kernelcare_license_key,
        unix_users_home_directory=unix_users_home_directory,
        sync_toolkit_enabled=sync_toolkit_enabled,
        php_versions=php_versions,
        php_settings=php_settings_dict,
        custom_php_modules_names=custom_php_modules_names,
        php_ioncube_enabled=php_ioncube_enabled,
        php_sessions_spread_enabled=php_sessions_spread_enabled,
        nodejs_version=nodejs_version,
        nodejs_versions=nodejs_versions,
        wordpress_toolkit_enabled=wordpress_toolkit_enabled,
        bubblewrap_toolkit_enabled=bubblewrap_toolkit_enabled,
        malware_toolkit_enabled=malware_toolkit_enabled,
        malware_toolkit_scans_enabled=malware_toolkit_scans_enabled,
        mariadb_version=mariadb_version,
        mariadb_cluster_name=mariadb_cluster_name,
        mariadb_backup_interval=mariadb_backup_interval,
        postgresql_version=postgresql_version,
        postgresql_backup_interval=postgresql_backup_interval,
        redis_password=redis_password,
        redis_memory_limit=redis_memory_limit,
        database_toolkit_enabled=database_toolkit_enabled,
        automatic_borg_repositories_prune_enabled=automatic_borg_repositories_prune_enabled,
        http_retry_properties=http_retry_properties_dict,
    )


@app.command(rich_help_panel=HELP_PANEL_UPDATE)
@catch_api_exception
def add_groups(name: str, groups: List[ClusterGroup]) -> None:
    """Add groups."""
    cluster = get_object(get_support().clusters, name=name)

    cluster.groups.extend(groups)
    cluster.update()


@app.command(rich_help_panel=HELP_PANEL_UPDATE)
@catch_api_exception
def update_description(name: str, description: str) -> None:
    """Update description."""
    cluster = get_object(get_support().clusters, name=name)

    cluster.description = description
    cluster.update()


@app.command(rich_help_panel=HELP_PANEL_UPDATE)
@catch_api_exception
def update_kernelcare_license_key(
    name: str,
    kernelcare_license_key: Optional[str] = typer.Argument(
        default=..., help=EMTPY_TO_CLEAR_MESSAGE
    ),
) -> None:
    """Update KernelCare license key."""
    cluster = get_object(get_support().clusters, name=name)

    cluster.kernelcare_license_key = kernelcare_license_key
    cluster.update()


@app.command(rich_help_panel=HELP_PANEL_UPDATE)
@catch_api_exception
def add_php_versions(name: str, php_versions: List[str]) -> None:
    """Add PHP versions."""
    cluster = get_object(get_support().clusters, name=name)

    cluster.php_versions.extend(php_versions)
    cluster.update()


@app.command(rich_help_panel=HELP_PANEL_UPDATE)
@catch_api_exception
@exit_with_status
def remove_php_versions(name: str, php_versions: List[str]) -> int:
    """Remove PHP versions."""
    cluster = get_object(get_support().clusters, name=name)

    exit_code = 0
    success = False

    for php_version in php_versions:
        try:
            cluster.php_versions.remove(php_version)
            success = True
        except ValueError:
            print_warning(f"PHP version '{php_version}' not found, skipping.")
            exit_code = 64

    if not success:
        handle_manual_error("No PHP versions have been removed")

    cluster.update()

    return exit_code


@app.command(rich_help_panel=HELP_PANEL_UPDATE)
@catch_api_exception
def update_php_settings(
    name: str,
    php_settings: str,
) -> None:
    """Update PHP settings."""
    cluster = get_object(get_support().clusters, name=name)

    php_settings_dict = _parse_json_to_dict(php_settings)

    cluster.php_settings = php_settings_dict
    cluster.update()


@app.command(rich_help_panel=HELP_PANEL_UPDATE)
@catch_api_exception
def update_http_retry_properties(
    name: str,
    http_retry_properties: str,
) -> None:
    """Update HTTP retry properties."""
    cluster = get_object(get_support().clusters, name=name)

    http_retry_properties_dict = _parse_json_to_dict(http_retry_properties)

    cluster.http_retry_properties = http_retry_properties_dict
    cluster.update()


@app.command()
@catch_api_exception
def add_custom_php_modules(
    name: str, custom_php_modules_names: List[PHPExtension]
) -> None:
    """Add custom PHP modules."""
    cluster = get_object(get_support().clusters, name=name)

    cluster.custom_php_modules_names.extend(custom_php_modules_names)
    cluster.update()


@app.command(rich_help_panel=HELP_PANEL_UPDATE)
@catch_api_exception
def update_php_ioncube(
    name: str,
    state: bool = typer.Argument(default=..., help=BOOL_MESSAGE),
) -> None:
    """Update PHP ionCube."""
    cluster = get_object(get_support().clusters, name=name)

    cluster.php_ioncube_enabled = state
    cluster.update()


@app.command(rich_help_panel=HELP_PANEL_UPDATE)
@catch_api_exception
def update_php_session_spread(
    name: str,
    state: bool = typer.Argument(default=..., help=BOOL_MESSAGE),
) -> None:
    """Update PHP session spread."""
    cluster = get_object(get_support().clusters, name=name)

    cluster.php_sessions_spread_enabled = state
    cluster.update()


@app.command(rich_help_panel=HELP_PANEL_UPDATE)
@catch_api_exception
def update_nodejs_version(
    name: str,
    nodejs_version: int,
) -> None:
    """Update NodeJS version."""
    cluster = get_object(get_support().clusters, name=name)

    cluster.nodejs_version = nodejs_version
    cluster.update()


@app.command(rich_help_panel=HELP_PANEL_UPDATE)
@catch_api_exception
def add_nodejs_versions(name: str, nodejs_versions: List[str]) -> None:
    """Add NodeJS versions."""
    cluster = get_object(get_support().clusters, name=name)

    cluster.nodejs_versions.extend(nodejs_versions)
    cluster.update()


@app.command(rich_help_panel=HELP_PANEL_UPDATE)
@catch_api_exception
@exit_with_status
def remove_nodejs_versions(name: str, nodejs_versions: List[str]) -> int:
    """Remove NodeJS versions."""
    cluster = get_object(get_support().clusters, name=name)

    exit_code = 0
    success = False

    for nodejs_version in nodejs_versions:
        try:
            cluster.nodejs_versions.remove(nodejs_version)
            success = True
        except ValueError:
            print_warning(
                f"NodeJS version '{nodejs_version}' not found, skipping."
            )
            exit_code = 64

    if not success:
        handle_manual_error("No NodeJS versions have been removed")

    cluster.update()

    return exit_code


@app.command(rich_help_panel=HELP_PANEL_UPDATE)
@catch_api_exception
def update_malware_toolkit(
    name: str,
    state: bool = typer.Argument(default=..., help=BOOL_MESSAGE),
) -> None:
    """Update malware toolkit."""
    cluster = get_object(get_support().clusters, name=name)

    cluster.malware_toolkit_enabled = state
    cluster.update()


@app.command(rich_help_panel=HELP_PANEL_UPDATE)
@catch_api_exception
def update_malware_toolkit_scans(
    name: str,
    state: bool = typer.Argument(default=..., help=BOOL_MESSAGE),
) -> None:
    """Update malware toolkit scans."""
    cluster = get_object(get_support().clusters, name=name)

    cluster.malware_toolkit_scans_enabled = state
    cluster.update()


@app.command(rich_help_panel=HELP_PANEL_UPDATE)
@catch_api_exception
def update_wordpress_toolkit(
    name: str,
    state: bool = typer.Argument(default=..., help=BOOL_MESSAGE),
) -> None:
    """Update WordPress toolkit."""
    cluster = get_object(get_support().clusters, name=name)

    cluster.wordpress_toolkit_enabled = state
    cluster.update()


@app.command(rich_help_panel=HELP_PANEL_UPDATE)
@catch_api_exception
def update_automatic_borg_repositories_prune(
    name: str,
    state: bool = typer.Argument(default=..., help=BOOL_MESSAGE),
) -> None:
    """Update automatic Borg repositories prune."""
    cluster = get_object(get_support().clusters, name=name)

    cluster.automatic_borg_repositories_prune_enabled = state
    cluster.update()


@app.command(rich_help_panel=HELP_PANEL_UPDATE)
@catch_api_exception
def update_sync_toolkit(
    name: str,
    state: bool = typer.Argument(default=..., help=BOOL_MESSAGE),
) -> None:
    """Update sync toolkit."""
    cluster = get_object(get_support().clusters, name=name)

    cluster.sync_toolkit_enabled = state
    cluster.update()


@app.command(rich_help_panel=HELP_PANEL_UPDATE)
@catch_api_exception
def update_bubblewrap_toolkit(
    name: str,
    state: bool = typer.Argument(default=..., help=BOOL_MESSAGE),
) -> None:
    """Update Bubblewrap toolkit."""
    cluster = get_object(get_support().clusters, name=name)

    cluster.bubblewrap_toolkit_enabled = state
    cluster.update()


@app.command(rich_help_panel=HELP_PANEL_UPDATE)
@catch_api_exception
def update_mariadb_version(
    name: str,
    mariadb_version: str,
) -> None:
    """Update MariaDB version."""
    cluster = get_object(get_support().clusters, name=name)

    cluster.mariadb_version = mariadb_version
    cluster.update()


@app.command(rich_help_panel=HELP_PANEL_UPDATE)
@catch_api_exception
def update_mariadb_cluster_name(
    name: str,
    mariadb_cluster_name: Optional[str] = typer.Argument(
        default=..., help=EMTPY_TO_CLEAR_MESSAGE
    ),
) -> None:
    """Update MariaDB cluster name."""
    cluster = get_object(get_support().clusters, name=name)

    cluster.mariadb_cluster_name = mariadb_cluster_name
    cluster.update()


@app.command(rich_help_panel=HELP_PANEL_UPDATE)
@catch_api_exception
def update_mariadb_backup_interval(
    name: str,
    mariadb_backup_interval: int,
) -> None:
    """Update MariaDB backup interval."""
    cluster = get_object(get_support().clusters, name=name)

    cluster.mariadb_backup_interval = mariadb_backup_interval
    cluster.update()


@app.command(rich_help_panel=HELP_PANEL_UPDATE)
@catch_api_exception
def update_postgresql_version(
    name: str,
    postgresql_version: str,
) -> None:
    """Update PostgreSQL version."""
    cluster = get_object(get_support().clusters, name=name)

    cluster.postgresql_version = postgresql_version
    cluster.update()


@app.command(rich_help_panel=HELP_PANEL_UPDATE)
@catch_api_exception
def update_postgresql_backup_interval(
    name: str,
    postgresql_backup_interval: int,
) -> None:
    """Update PostgreSQL backup interval."""
    cluster = get_object(get_support().clusters, name=name)

    cluster.postgresql_backup_interval = postgresql_backup_interval
    cluster.update()


@app.command(rich_help_panel=HELP_PANEL_UPDATE)
@catch_api_exception
def update_redis_memory_limit(
    name: str,
    redis_memory_limit: int,
) -> None:
    """Update Redis memory limit."""
    cluster = get_object(get_support().clusters, name=name)

    cluster.redis_memory_limit = redis_memory_limit
    cluster.update()


@app.command(rich_help_panel=HELP_PANEL_UPDATE)
@catch_api_exception
def update_redis_password(
    name: str,
    password: str = typer.Option(
        default=generate_random_string,
        prompt=True,
        hide_input=True,
        show_default=False,
        help=RANDOM_PASSWORD_MESSAGE,
    ),
) -> None:
    """Update Redis password."""
    cluster = get_object(get_support().clusters, name=name)

    cluster.redis_password = password
    cluster.update()


@app.command(rich_help_panel=HELP_PANEL_UPDATE)
@catch_api_exception
def update_database_toolkit(
    name: str,
    state: bool = typer.Argument(default=..., help=BOOL_MESSAGE),
) -> None:
    """Update database toolkit."""
    cluster = get_object(get_support().clusters, name=name)

    cluster.database_toolkit_enabled = state
    cluster.update()


@app.command()
@catch_api_exception
def delete(
    name: str,
    confirm: bool = typer.Option(
        default=False,
        help=CONFIRM_MESSAGE,
    ),
) -> None:
    """Delete cluster."""
    cluster = get_object(get_support().clusters, name=name)

    delete_api_object(obj=cluster, confirm=confirm)


@app.command(rich_help_panel=HELP_PANEL_SHOW)
@catch_api_exception
def unix_users_home_directories_usages(
    name: str,
    hours_before: Optional[int] = None,
    days_before: Optional[int] = None,
    # Typer has a bug where show_default can't be a string in typer.Option
    # https://github.com/tiangolo/typer/issues/158
    amount: Optional[int] = typer.Option(default=None, show_default="All"),  # type: ignore[call-overload]
) -> None:
    """Show UNIX users home directory usages.

    Using --hours-before OR --days-before is required.
    """
    cluster = get_object(get_support().clusters, name=name)

    timestamp, time_unit = get_usages_timestamp(
        days_before=days_before, hours_before=hours_before
    )

    usages = get_support().unix_users_home_directory_usages(
        cluster_id=cluster.id, timestamp=timestamp, time_unit=time_unit
    )[:amount]

    typer.echo(get_usages_plot(usages=usages))


@app.command()
@catch_api_exception
def get_common_properties() -> None:
    """Get clusters common properties."""
    cluster = Cluster(get_support())

    groups = {
        "IMAP": {
            "imap_hostname": "Hostname",
            "imap_port": "Port",
            "imap_encryption": "Encryption",
        },
        "POP3": {
            "pop3_hostname": "Hostname",
            "pop3_port": "Port",
            "pop3_encryption": "Encryption",
        },
        "SMTP": {
            "smtp_hostname": "Hostname",
            "smtp_port": "Port",
            "smtp_encryption": "Encryption",
        },
        "Databases": {"phpmyadmin_url": "phpMyAdmin URL"},
    }

    properties = cluster.get_common_properties()
    matched_properties = []

    for group in groups:
        table = Table(
            expand=True,
            show_lines=False,
            show_edge=False,
            box=None,
            show_header=False,
        )

        for key in groups[group]:
            table.add_row(groups[group][key], str(properties[key]))
            matched_properties.append(key)

        console.print(Panel(table, title=group, title_align="left"))

    unmatched_properties = [
        k for k in properties.keys() if k not in matched_properties
    ]

    if len(unmatched_properties) > 0:
        table = Table(
            expand=True,
            show_lines=False,
            show_edge=False,
            box=None,
            show_header=False,
        )

        for key in unmatched_properties:
            table.add_row(key, str(properties[key]))

        console.print(Panel(table, title="Other", title_align="left"))
