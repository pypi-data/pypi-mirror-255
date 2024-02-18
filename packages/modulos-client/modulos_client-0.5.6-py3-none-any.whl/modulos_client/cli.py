# --------------------------------------------------- #
# Copyright (C) 2023 Modulos AG. All rights reserved. #
# --------------------------------------------------- #
import click

from modulos_client import config as config_utils
from modulos_client import organizations, profiles, projects, users, templates


@click.group()
def main():
    pass


main.add_command(profiles.profiles)
main.add_command(organizations.orgs)
main.add_command(users.users)
main.add_command(projects.projects)
main.add_command(templates.templates)


@main.command(
    help=(
        "Login to the Modulos platform. HOST is the address of the platform. "
        "For local use, this is http://localhost."
    ),
)
@click.option(
    "-h",
    "--host",
    type=str,
    prompt=True,
)
@click.option(
    "-t",
    "--token",
    prompt=True,
    hide_input=True,
)
@click.option(
    "-p",
    "--profile-name",
    type=str,
    prompt=True,
    help=(
        "The name of the profile. It is used to reference the profile in the "
        "future. If you want to use multiple profiles, you can specify a "
        "different name for each profile."
    ),
)
def login(host: str, token: str, profile_name: str):
    """Login to the Modulos platform. HOST is the address of the platform.
    For local use, this is http://localhost.

    Args:
        host (str): The address of the platform.
        token (str): The token.
        profile_name (str): The name of the profile. If you want to use multiple
            profiles, you can specify a different name for each profile.
    """
    host = host.rstrip("/")
    with config_utils.get_modulos_config() as config:
        config.add_profile(profile_name, host, token)
    return None


@main.command(
    help="Logout from the Modulos platform on all profiles.",
)
@click.option(
    "-f",
    "--force",
    default=False,
    is_flag=True,
    help="Force logout without confirmation.",
)
def logout(force: bool = False):
    with config_utils.get_modulos_config() as config:
        click.echo("This will remove all profiles. Do you want to continue?")
        if not force and not click.confirm("Continue?", abort=False):
            return None
        all_profile_names = list(config.profiles.keys())
        for profile_name in all_profile_names:
            config.remove_profile(profile_name)
    click.echo("Logout successful.")


if __name__ == "__main__":
    main()
