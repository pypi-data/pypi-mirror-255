from typing import Optional
import click
import tabulate

from modulos_client import config as config_utils


@click.group(
    help="Manage organizations.",
)
def orgs():
    pass


@orgs.command(
    "list",
    help="List all organizations.",
)
def list_orgs():
    client = config_utils.ModulosClient.from_conf_file()
    response = client.get("/organizations", {})
    if response.ok:
        click.echo(tabulate.tabulate(response.json().get("items"), headers="keys"))
    else:
        click.echo(f"Could not list organizations: {response.text}")


@orgs.command(
    "create",
    help="Create a new organization.",
)
@click.option(
    "--name",
    type=str,
    prompt=True,
)
@click.option(
    "--enable-monitoring",
    type=bool,
    prompt=True,
)
@click.option(
    "--enable-domain-signup",
    type=bool,
    prompt=True,
)
# add domain only if enable-domain-signup is true
@click.option(
    "--domain",
    type=str,
    prompt=True,
    default=None,
)
def create_orgs(
    name: str,
    enable_monitoring: bool,
    enable_domain_signup: bool,
    domain: Optional[str] = None,
):
    client = config_utils.ModulosClient.from_conf_file()
    data = {
        "name": name,
        "monitoring_enabled": enable_monitoring,
        "allow_signup_from_domain": enable_domain_signup,
        "domain": domain if enable_domain_signup else None,
    }
    response = client.post("/organizations", data=data)
    if response.ok:
        click.echo(f"Organization '{name}' created.")
    else:
        click.echo(f"Could not create organization: {response.json().get('detail')}")


# There is no delete org endpoint at the moment, should we introduce one?
# @orgs.command(
#     "delete",
#     help="Delete an organization.",
# )
# @click.option(
#     "--name",
#     type=str,
#     prompt=True,
# )
# def delete_orgs(name: str):
#     client = config_utils.ModulosClient.from_conf_file()
#     response = client.delete("/organizations", url_params={"organization_name": name})
#     if response.ok:
#         click.echo(f"Organization '{name}' deleted.")
#     else:
#         click.echo(f"Could not delete organization: {response.json().get('detail')}")
