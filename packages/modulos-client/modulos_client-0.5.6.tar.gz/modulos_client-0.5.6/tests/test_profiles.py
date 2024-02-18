from unittest import mock

from click.testing import CliRunner

from modulos_client import config
from modulos_client.profiles import profiles


@mock.patch("modulos_client.config.get_modulos_config")
def test_list_profiles(mock_config):
    # Prepare.
    config_mock = mock.MagicMock()
    config_mock.active_profile = "Peter"
    config_mock.profiles = {
        "Peter": config.ModulosProfile(name="Peter", host="my_host", token="my_token")
    }
    mock_config.return_value.__enter__.return_value = config_mock
    runner = CliRunner()

    # Test.
    result = runner.invoke(profiles, ["list"])

    # Check.
    assert result.exit_code == 0
    assert result.output == (
        "╒════════════════╤═════════╕\n│ Name           │ Host    "
        "│\n╞════════════════╪═════════╡\n│ Peter (active) │ my_host │"
        "\n╘════════════════╧═════════╛\n"
    )


@mock.patch("modulos_client.config.get_modulos_config")
def test_list_profiles__no_profiles(mock_config):
    # Prepare.
    config_mock = mock.MagicMock()
    config_mock.active_profile = None
    mock_config.return_value.__enter__.return_value = config_mock
    runner = CliRunner()

    # Test.
    result = runner.invoke(profiles, ["list"])

    # Check.
    assert result.exit_code == 0
    assert result.output == "No profiles.\n"


@mock.patch("modulos_client.config.get_modulos_config")
def test_activate_profile(mock_config):
    # Prepare.
    config_mock = mock.MagicMock()
    config_mock.profiles = {
        "Peter": config.ModulosProfile(name="Peter", host="my_host", token="my_token"),
        "Pan": config.ModulosProfile(name="Pan", host="other", token="other_token"),
    }
    mock_config.return_value.__enter__.return_value = config_mock
    runner = CliRunner()

    # Test.
    result = runner.invoke(profiles, ["activate", "--profile-name", "Pan"])

    # Check.
    assert result.exit_code == 0
    assert result.output == "Profile 'Pan' activated.\n"


@mock.patch("modulos_client.config.get_modulos_config")
def test_activate_profile__negative_not_in_profiles(mock_config):
    # Prepare.
    config_mock = mock.MagicMock()
    config_mock.profiles = {
        "Peter": config.ModulosProfile(name="Peter", host="my_host", token="my_token"),
        "Pan": config.ModulosProfile(name="Pan", host="other", token="other_token"),
    }
    mock_config.return_value.__enter__.return_value = config_mock
    runner = CliRunner()

    # Test.
    result = runner.invoke(profiles, ["activate", "--profile-name", "not_existing"])

    # Check.
    assert result.exit_code == 0
    assert result.output == "Profile 'not_existing' does not exist.\n"


@mock.patch("modulos_client.config.get_modulos_config")
def test_activate_profile__negative_no_profiles(mock_config):
    # Prepare.
    config_mock = mock.MagicMock()
    config_mock.profiles = {}
    mock_config.return_value.__enter__.return_value = config_mock
    runner = CliRunner()

    # Test.
    result = runner.invoke(profiles, ["activate", "--profile-name", "Peter"])

    # Check.
    assert result.exit_code == 0
    assert result.output == "No profiles.\n"


@mock.patch("modulos_client.config.get_modulos_config")
def test_deactivate_profile(mock_config):
    # Prepare.
    config_mock = mock.MagicMock()
    config_mock.profiles = {
        "Peter": config.ModulosProfile(name="Peter", host="my_host", token="my_token"),
        "Pan": config.ModulosProfile(name="Pan", host="other", token="other_token"),
    }
    config_mock.remove_profile.return_value = None
    config_mock.active_profile = "Pan"
    mock_config.return_value.__enter__.return_value = config_mock
    runner = CliRunner()

    # Test.
    result = runner.invoke(profiles, ["deactivate", "--profile-name", "Peter"])

    # Check.
    assert result.exit_code == 0
    assert result.output == (
        "Profile 'Peter' deactivated.\nProfile 'Pan' is now the active profile.\n"
    )


@mock.patch("modulos_client.config.get_modulos_config")
def test_deactivate_profile__no_active_profiles(mock_config):
    # Prepare.
    config_mock = mock.MagicMock()
    config_mock.profiles = {
        "Peter": config.ModulosProfile(name="Peter", host="my_host", token="my_token"),
    }
    config_mock.remove_profile.return_value = None
    config_mock.active_profile = None
    mock_config.return_value.__enter__.return_value = config_mock
    runner = CliRunner()

    # Test.
    result = runner.invoke(profiles, ["deactivate", "--profile-name", "Peter"])

    # Check.
    assert result.exit_code == 0
    assert result.output == (
        "Profile 'Peter' deactivated.\nNo active profile anymore.\n"
    )


@mock.patch("modulos_client.config.get_modulos_config")
def test_deactivate_profile__negative_no_profiles(mock_config):
    # Prepare.
    config_mock = mock.MagicMock()
    config_mock.profiles = {}
    mock_config.return_value.__enter__.return_value = config_mock
    runner = CliRunner()

    # Test.
    result = runner.invoke(profiles, ["deactivate", "--profile-name", "Peter"])

    # Check.
    assert result.exit_code == 0
    assert result.output == "No profiles.\n"


@mock.patch("modulos_client.config.get_modulos_config")
def test_deactivate_profile__negative_not_in_profiles(mock_config):
    # Prepare.
    config_mock = mock.MagicMock()
    config_mock.profiles = {
        "Peter": config.ModulosProfile(name="Peter", host="my_host", token="my_token"),
        "Pan": config.ModulosProfile(name="Pan", host="other", token="other_token"),
    }
    mock_config.return_value.__enter__.return_value = config_mock
    runner = CliRunner()

    # Test.
    result = runner.invoke(profiles, ["deactivate", "--profile-name", "not_existing"])

    # Check.
    assert result.exit_code == 0
    assert result.output == ("Profile 'not_existing' does not exist.\n")
