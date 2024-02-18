"""Command line interface for the Cyberfusion Cluster API."""

import configparser
import json
import os
import subprocess
from typing import List, Optional

import typer

from cyberfusion.ClusterApiCli import METHOD_DELETE
from cyberfusion.ClusterCli import (
    api_users,
    basic_authentication_realms,
    borg,
    certificate_managers,
    certificates,
    clusters,
    cmses,
    crons,
    custom_config_snippets,
    databases,
    domain_routers,
    firewall_groups,
    fpm_pools,
    ftp_users,
    haproxy_listens,
    htpasswd,
    logs,
    mail,
    malwares,
    nodes,
    passenger_apps,
    redis_instances,
    security_txt_policies,
    ssh_keys,
    unix_users,
    url_redirects,
    virtual_hosts,
)
from cyberfusion.ClusterCli._utilities import (
    DETAILED_MESSAGE,
    PATH_CONFIG_LOCAL,
    PATH_DIRECTORY_CONFIG_CLI,
    PATH_DIRECTORY_CONFIG_GENERIC,
    HttpMethod,
    catch_api_exception,
    console,
    get_package_version,
    get_support,
    state,
    wait_for_task,
)

NAME_COMMAND_API_USERS = "api-users"
NAME_COMMAND_BASIC_AUTHENTICATION_REALMS = "basic-authentication-realms"
NAME_COMMAND_BORG = "borg"
NAME_COMMAND_CERTIFICATES = "certificates"
NAME_COMMAND_CERTIFICATE_MANAGERS = "certificate-managers"
NAME_COMMAND_CLUSTERS = "clusters"
NAME_COMMAND_CMSES = "cmses"
NAME_COMMAND_CRONS = "crons"
NAME_COMMAND_SECURITY_TXT_POLICIES = "security-txt-policies"
NAME_COMMAND_CUSTOM_CONFIG_SNIPPETS = "custom-config-snippets"
NAME_COMMAND_DATABASES = "databases"
NAME_COMMAND_DOMAIN_ROUTERS = "domain-routers"
NAME_COMMAND_FIREWALL_GROUPS = "firewall-groups"
NAME_COMMAND_FPM_POOLS = "fpm-pools"
NAME_COMMAND_FTP_USERS = "ftp-users"
NAME_COMMAND_HAPROXY_LISTENS = "haproxy-listens"
NAME_COMMAND_HTPASSWD = "htpasswd"
NAME_COMMAND_LOGS = "logs"
NAME_COMMAND_MAIL = "mail"
NAME_COMMAND_MALWARES = "malwares"
NAME_COMMAND_NODES = "nodes"
NAME_COMMAND_PASSENGER_APPS = "passenger-apps"
NAME_COMMAND_REDIS_INSTANCES = "redis-instances"
NAME_COMMAND_SSH_KEYS = "ssh-keys"
NAME_COMMAND_UNIX_USERS = "unix-users"
NAME_COMMAND_URL_REDIRECTS = "url-redirects"
NAME_COMMAND_VIRTUAL_HOSTS = "virtual-hosts"

app = typer.Typer(context_settings={"help_option_names": ["-h", "--help"]})


@app.callback()
def callback(
    clusters_names: List[str] = typer.Option(
        [],
        "--clusters-names",
        "-c",
        help="Names of clusters to operate on (do not set to operate on all clusters)",
    ),
) -> None:
    """Cyberfusion Cluster API CLI."""
    state["clusters_names"] = clusters_names


app.add_typer(clusters.app, name=NAME_COMMAND_CLUSTERS, help="Manage Clusters")
app.add_typer(
    virtual_hosts.app,
    name=NAME_COMMAND_VIRTUAL_HOSTS,
    help="Manage Virtual Hosts",
)
app.add_typer(
    fpm_pools.app, name=NAME_COMMAND_FPM_POOLS, help="Manage FPM Pools"
)
app.add_typer(
    unix_users.app, name=NAME_COMMAND_UNIX_USERS, help="Manage UNIX Users"
)
app.add_typer(logs.app, name=NAME_COMMAND_LOGS, help="View Logs")
app.add_typer(
    certificates.app,
    name=NAME_COMMAND_CERTIFICATES,
    help="Manage Certificates",
)
app.add_typer(
    certificate_managers.app,
    name=NAME_COMMAND_CERTIFICATE_MANAGERS,
    help="Manage Certificate Managers",
)
app.add_typer(
    url_redirects.app,
    name=NAME_COMMAND_URL_REDIRECTS,
    help="Manage URL Redirects",
)
app.add_typer(
    crons.app,
    name=NAME_COMMAND_CRONS,
    help="Manage Crons",
)
app.add_typer(
    security_txt_policies.app,
    name=NAME_COMMAND_SECURITY_TXT_POLICIES,
    help="Manage Security TXT Policies",
)
app.add_typer(
    databases.app, name=NAME_COMMAND_DATABASES, help="Manage Databases"
)
app.add_typer(cmses.app, name=NAME_COMMAND_CMSES, help="Manage CMSes")
app.add_typer(
    passenger_apps.app,
    name=NAME_COMMAND_PASSENGER_APPS,
    help="Manage Passenger Apps",
)
app.add_typer(nodes.app, name=NAME_COMMAND_NODES, help="Manage Nodes")
app.add_typer(malwares.app, name=NAME_COMMAND_MALWARES, help="Manage Malwares")
app.add_typer(ssh_keys.app, name=NAME_COMMAND_SSH_KEYS, help="Manage SSH Keys")
app.add_typer(mail.app, name=NAME_COMMAND_MAIL, help="Manage Mail")
app.add_typer(borg.app, name=NAME_COMMAND_BORG, help="Manage Borg")
app.add_typer(
    redis_instances.app,
    name=NAME_COMMAND_REDIS_INSTANCES,
    help="Manage Redis Instances",
)
app.add_typer(htpasswd.app, name=NAME_COMMAND_HTPASSWD, help="Manage Htpasswd")
app.add_typer(
    basic_authentication_realms.app,
    name=NAME_COMMAND_BASIC_AUTHENTICATION_REALMS,
    help="Manage Basic Authentication Realms",
)
app.add_typer(
    firewall_groups.app,
    name=NAME_COMMAND_FIREWALL_GROUPS,
    help="Manage Firewall Groups",
)
app.add_typer(
    ftp_users.app, name=NAME_COMMAND_FTP_USERS, help="Manage FTP Users"
)
app.add_typer(
    domain_routers.app,
    name=NAME_COMMAND_DOMAIN_ROUTERS,
    help="Manage Domain Routers",
)
app.add_typer(
    custom_config_snippets.app,
    name=NAME_COMMAND_CUSTOM_CONFIG_SNIPPETS,
    help="Manage Custom Config Snippets",
)
app.add_typer(
    haproxy_listens.app,
    name=NAME_COMMAND_HAPROXY_LISTENS,
    help="Manage HAProxy Listens",
)
app.add_typer(
    api_users.app,
    name=NAME_COMMAND_API_USERS,
    help="Manage API Users",
    hidden=True,
)


@app.command()
@catch_api_exception
def tasks(
    task_collection_uuid: str,
) -> None:
    """Show Task Collection Results"""
    wait_for_task(
        task_collection_uuid=task_collection_uuid,
    )


@app.command()
@catch_api_exception
def tombstones(
    detailed: bool = typer.Option(default=False, help=DETAILED_MESSAGE)
) -> None:
    """Show Tombstones"""
    console.print(
        get_support().get_table(
            objs=get_support().tombstones,
            detailed=detailed,
        )
    )


@app.command(rich_help_panel="Special")
@catch_api_exception
def update() -> None:
    """Update CLI"""
    original_version = get_package_version()

    output = subprocess.run(
        ["pipx", "upgrade", "python3-cyberfusion-cluster-cli"],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=True,
    )

    new_version = get_package_version()

    if output.stdout.startswith("upgraded package"):
        console.print(
            f"CLI updated from version {original_version} to {new_version}."
        )
    elif "is already at latest version" in output.stdout:
        console.print(f"CLI already up to date (version {original_version}).")


@app.command(rich_help_panel="Special")
def setup(
    api_user_username: str = typer.Option(
        ...,
        "--username",
        "-u",
        prompt="API username",
    ),
    api_user_password: str = typer.Option(
        ...,
        "--password",
        "-p",
        prompt="API password",
        hide_input=True,
    ),
) -> None:
    """Set Up CLI with API Credentials"""
    exists = os.path.exists(PATH_CONFIG_LOCAL)

    # Create directories which contain config file

    for directory in [
        PATH_DIRECTORY_CONFIG_GENERIC,
        PATH_DIRECTORY_CONFIG_CLI,
    ]:
        if os.path.exists(directory):
            continue

        os.mkdir(directory)
        os.chmod(directory, 0o700)

    # Create and set permissions on config file before writing to it

    with open(PATH_CONFIG_LOCAL, "w") as file:
        pass

    os.chmod(PATH_CONFIG_LOCAL, 0o600)

    # Write credentials to config file

    config = configparser.ConfigParser()

    config["clusterapi"] = {}
    config["clusterapi"]["serverurl"] = "https://cluster-api.cyberfusion.nl"
    config["clusterapi"]["username"] = api_user_username
    config["clusterapi"]["password"] = api_user_password

    with open(PATH_CONFIG_LOCAL, "w") as file:
        config.write(file)

    # Show message

    message = "Config file created. You can now use the CLI."

    if exists:
        message += " (Overwrote existing config file)"

    console.print(message)


@app.command()
@catch_api_exception
def request(
    method: HttpMethod,
    path: str,
    data: Optional[str] = typer.Option(default=None),
) -> None:
    """Manually Call API Endpoint"""
    parsed_data = {}

    if data:
        parsed_data = json.loads(data)

    if not path.startswith("/"):
        path = "/" + path

    func = getattr(get_support().request, method)

    if method == METHOD_DELETE:
        func(path)
    else:
        func(path, parsed_data)

    response = get_support().request.execute()

    console.print(response)


# Run when running this outside of setup.py console_scripts

if __name__ == "__main__":
    app()
