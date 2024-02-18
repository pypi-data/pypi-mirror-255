from typing import Optional

import click
import tabulate

from modulos_client import config as config_utils
from modulos_client.services import users_services


@click.group(
    help="Manage users.",
)
def users():
    pass


@users.command(
    "list",
    help="List all users.",
)
@click.option(
    "-o",
    "--organization-id",
    type=str,
    default=None,
)
def list_users(organization_id: Optional[str] = None):
    client = config_utils.ModulosClient.from_conf_file()
    if organization_id is None:
        org_id = client.get("/users/me", {}).json().get("organization")["id"]
    else:
        org_id = organization_id
    response = client.get(f"/organizations/{org_id}/users", {})
    if response.ok:
        results = response.json().get("items")
        results = [
            {
                "id": result["id"],
                "firstname": result["firstname"],
                "lastname": result["lastname"],
                "email": result["email"],
                "is_super_admin": result["is_super_admin"],
                "is_org_admin": result["is_org_admin"],
                "is_active": result["is_active"],
            }
            for result in results
        ]
        click.echo(tabulate.tabulate(results, headers="keys"))
    else:
        click.echo(f"Could not list users: {response.text}")


@users.command(
    "create",
    help="Create a new user.",
)
@click.option(
    "--organization-id",
    type=str,
    default=None,
)
@click.option(
    "--firstname",
    type=str,
    prompt=True,
)
@click.option(
    "--lastname",
    type=str,
    prompt=True,
)
@click.option(
    "--email",
    type=str,
    prompt=True,
)
@click.option(
    "--is-active",
    type=bool,
    prompt=True,
)
@click.option(
    "--is-org-admin",
    type=bool,
    default=False,
)
def create_users(
    firstname: str,
    lastname: str,
    email: str,
    is_active: bool,
    organization_id: Optional[str] = None,
    is_org_admin: bool = False,
):
    client = config_utils.ModulosClient.from_conf_file()
    if organization_id is None:
        current_user = client.get("/users/me", {}).json()
        org_id = current_user.get("organization")["id"]
    else:
        org_id = organization_id

    response = client.post(
        f"/organizations/{org_id}/users",
        data={
            "firstname": firstname,
            "lastname": lastname,
            "email": email,
            "is_active": is_active,
            "is_org_admin": is_org_admin,
        },
    )
    if response.ok:
        click.echo(f"User '{email}' created.")
    else:
        click.echo(f"Could not create user: {response.json().get('detail')}")


@users.command(
    "add-role",
    help="Add a role to a user.",
)
@click.option(
    "--user-id",
    type=str,
    prompt=True,
    help="The user ID. You can look it up with 'modulos users list'.",
)
@click.option(
    "--role",
    type=str,
    help="The role to add. Can be 'owner', 'editor', 'viewer' and 'auditor'.",
    prompt=True,
)
@click.option(
    "--project-id",
    type=str,
    prompt=True,
)
def add_users_role(user_id: str, role: str, project_id: str):
    client = config_utils.ModulosClient.from_conf_file()
    response = client.post(
        f"/users/{user_id}/roles",
        url_params={
            "role": role,
            "project_id": project_id,
        },
    )
    if response.ok:
        click.echo(f"Role '{role}' added to user '{user_id}'.")
    else:
        click.echo(f"Could not add role to user: {response.json().get('detail')}")


@users.command(
    "remove-role",
    help="Remove a role from a user.",
)
@click.option(
    "--user-id",
    type=str,
    prompt=True,
    help="The user ID. You can look it up with 'modulos users list'.",
)
@click.option(
    "--role",
    type=str,
    help="The role to remove. Can be 'owner', 'editor', 'viewer' and 'auditor'.",
    prompt=True,
)
@click.option(
    "--project-id",
    type=str,
    prompt=True,
)
def remove_users_role(user_id: str, role: str, project_id: str):
    client = config_utils.ModulosClient.from_conf_file()
    response = client.delete(
        f"/users/{user_id}/roles",
        url_params={
            "role": role,
            "project_id": project_id,
        },
    )
    if response.ok:
        click.echo(f"Role '{role}' removed from user '{user_id}'.")
    else:
        click.echo(f"Could not remove role from user: {response.json().get('detail')}")


@users.command(
    "activate",
    help="Activate a user.",
)
@click.option(
    "--user-id",
    type=str,
    prompt=True,
    help="The user ID. You can look it up with 'modulos users list'.",
)
def activate_user(user_id: str):
    client = config_utils.ModulosClient.from_conf_file()
    user_response = client.get(f"/users/{user_id}")
    if not user_response.ok:
        click.echo(f"User '{user_id}' not found.")
        return None
    user = user_response.json()
    user_org = user["organization"]["id"]
    response = client.patch(
        f"/organizations/{user_org}/users/{user_id}",
        {"is_active": True},
    )
    if response.ok:
        click.echo(f"User '{user_id}' activated.")
    else:
        click.echo(f"Could not activate user: {response.json().get('detail')}")


@users.command(
    "deactivate",
    help="Deactivate a user.",
)
@click.option(
    "--user-id",
    type=str,
    prompt=True,
    help="The user ID. You can look it up with 'modulos users list'.",
)
def deactivate_user(user_id: str):
    client = config_utils.ModulosClient.from_conf_file()
    user_response = client.get(f"/users/{user_id}")
    if not user_response.ok:
        click.echo(f"User '{user_id}' not found.")
        return None
    user = user_response.json()
    user_org = user["organization"]["id"]
    response = client.patch(
        f"/organizations/{user_org}/users/{user_id}",
        {"is_active": False},
    )
    if response.ok:
        click.echo(f"User '{user_id}' deactivated.")
    else:
        click.echo(f"Could not deactivate user: {response.json().get('detail')}")


@users.command(
    "add-org-admin",
    help="Add organization admin privileges to a user.",
)
@click.option(
    "--user-id",
    type=str,
    prompt=True,
    help="The user ID. You can look it up with 'modulos users list'.",
)
def add_org_admin(user_id: str):
    user = users_services.get_user(user_id)
    if not user:
        click.echo(f"User '{user_id}' not found.")
        return None
    user_org = user["organization"]

    if not user_org:
        click.echo("The user does not have an associated organization")
        return None
    user_display = [
        {
            "id": user["id"],
            "firstname": user["firstname"],
            "lastname": user["lastname"],
            "email": user["email"],
            "is_super_admin": user["is_super_admin"],
            "is_org_admin": user["is_org_admin"],
            "is_active": user["is_active"],
        }
    ]

    organization_display = [
        {
            "id": user_org["id"],
            "name": user_org["name"],
        }
    ]
    click.echo("User: ")
    click.echo(tabulate.tabulate(user_display, headers="keys"))
    click.echo("")
    click.echo("Organization: ")
    click.echo(tabulate.tabulate(organization_display, headers="keys"))
    click.echo("")
    if not click.confirm("Continue?", abort=False):
        return None

    user_dict = {
        "is_org_admin": True,
    }
    updated_user = users_services.update_user(user_org["id"], user["id"], user_dict)
    if not updated_user:
        click.echo("Could not add org admin privileges to user.")
        return None
    click.echo(f"User '{user_id}' is now an organization admin.")


@users.command(
    "remove-org-admin",
    help="Remove organization administrator privileges from a user.",
)
@click.option(
    "--user-id",
    type=str,
    prompt=True,
    help="The user ID. You can look it up with 'modulos users list'.",
)
def remove_org_admin(user_id: str):
    user = users_services.get_user(user_id)
    if not user:
        click.echo(f"User '{user_id}' not found.")
        return None
    user_org = user["organization"]

    if not user_org:
        click.echo("The user does not have an associated organization")
        return None
    user_display = [
        {
            "id": user["id"],
            "firstname": user["firstname"],
            "lastname": user["lastname"],
            "email": user["email"],
            "is_super_admin": user["is_super_admin"],
            "is_org_admin": user["is_org_admin"],
            "is_active": user["is_active"],
        }
    ]

    organization_display = [
        {
            "id": user_org["id"],
            "name": user_org["name"],
        }
    ]
    click.echo("User: ")
    click.echo(tabulate.tabulate(user_display, headers="keys"))
    click.echo("")
    click.echo("Organization: ")
    click.echo(tabulate.tabulate(organization_display, headers="keys"))
    click.echo("")
    if not click.confirm("Continue?", abort=False):
        return None

    user_dict = {
        "is_org_admin": False,
    }
    updated_user = users_services.update_user(user_org["id"], user["id"], user_dict)
    if not updated_user:
        click.echo("Could not remove org admin privileges from user.")
        return None
    click.echo(f"User '{user_id}' is no longer an organization admin.")
