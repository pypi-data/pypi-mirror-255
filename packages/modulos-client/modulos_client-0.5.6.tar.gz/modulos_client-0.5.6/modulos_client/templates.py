import mimetypes
from typing import Optional

import click
import tabulate

from modulos_client import config as config_utils


@click.group(
    help="Manage templates.",
)
def templates():
    pass


@templates.command(
    "list",
    help="List all templates.",
)
@click.option(
    "-o",
    "--organization-id",
    type=str,
    default=None,
)
def list_templates(organization_id: Optional[str] = None):
    client = config_utils.ModulosClient.from_conf_file()
    if organization_id is None:
        org_id = client.get("/users/me", {}).json().get("organization")["id"]
    else:
        org_id = organization_id
    response = client.get(f"/organizations/{org_id}/templates", {})
    if response.ok:
        results = [
            {
                "framework_code": result["framework_code"],
                "framework_name": result["framework_name"],
                "framework_description": result["framework_description"],
                "framework_icon": result["framework_icon"],
                "number_of_requirements": result["number_of_requirements"],
                "number_of_controls": result["number_of_controls"],
            }
            for result in response.json()
        ]
        click.echo(tabulate.tabulate(results, headers="keys"))
    else:
        click.echo(f"Could not list templates: {response.text}")


@templates.command(
    "upload",
    help="Upload templates for your organization.",
)
@click.option(
    "--file",
    type=str,
    prompt=True,
)
@click.option(
    "-o",
    "--organization-id",
    type=str,
    default=None,
)
def upload_templates(file: str, organization_id: Optional[str] = None):
    client = config_utils.ModulosClient.from_conf_file()
    if organization_id is None:
        org_id = client.get("/users/me", {}).json().get("organization")["id"]
    else:
        org_id = organization_id
    with open(file, "rb") as f:
        files = {"file": (file, f, mimetypes.guess_type(file)[0])}
        response = client.post(
            f"/organizations/{org_id}/templates",
            files=files,
        )
    if response.ok:
        click.echo("Templates uploaded.")
    else:
        click.echo(f"Could not upload templates: {response.text}")
