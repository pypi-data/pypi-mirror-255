import click
import tabulate

from modulos_client import config as config_utils


@click.group(
    help="Manage profiles.",
)
def profiles():
    pass


@profiles.command(
    "list",
    help="List all profiles.",
)
def list_profiles():
    with config_utils.get_modulos_config() as config:
        if config.active_profile is None:
            click.echo("No profiles.")
        else:
            active_profile = config.active_profile
            profile_details = []
            for profile_name, profile in config.profiles.items():
                if profile_name == active_profile:
                    profile_name = f"{profile_name} (active)"

                profile_details.append([profile_name, profile.host])
            headers = ["Name", "Host"]
            click.echo(
                tabulate.tabulate(
                    profile_details, headers=headers, tablefmt="fancy_grid"
                )
            )


@profiles.command(
    "activate",
    help="Activate a profile.",
)
@click.option(
    "-p",
    "--profile-name",
    type=str,
    prompt=True,
    help=("The name of the profile to activate."),
)
def activate_profile(profile_name: str = "default"):
    with config_utils.get_modulos_config() as config:
        if config.profiles == {}:
            click.echo("No profiles.")
        elif profile_name not in config.profiles:
            click.echo(f"Profile '{profile_name}' does not exist.")
        else:
            config.active_profile = profile_name
            click.echo(f"Profile '{profile_name}' activated.")


@profiles.command(
    "deactivate",
    help="Remove a profile.",
)
@click.option(
    "-p",
    "--profile-name",
    type=str,
    prompt=True,
    help="The name of the profile to deactivate.",
)
def deactivate_profile(profile_name: str):
    with config_utils.get_modulos_config() as config:
        if config.profiles == {}:
            click.echo("No profiles.")
        elif profile_name not in config.profiles:
            click.echo(f"Profile '{profile_name}' does not exist.")
        else:
            config.remove_profile(profile_name)
            click.echo(f"Profile '{profile_name}' deactivated.")
            if config.active_profile is not None:
                click.echo(
                    f"Profile '{config.active_profile}' is now the active profile."
                )
            else:
                click.echo("No active profile anymore.")
