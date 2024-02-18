from unittest import mock

from click.testing import CliRunner

from modulos_client.cli import main


@mock.patch("modulos_client.cli.config_utils.get_modulos_config")
def test_login(mock_config):
    # Prepare.
    config_mock = mock.MagicMock()
    config_mock.add_profile.return_value = None
    mock_config.return_value.__enter__.return_value = config_mock
    runner = CliRunner()

    # Test.
    result = runner.invoke(
        main, ["login"], input="http://localhost\nmy_token\nmy_profile\n"
    )

    # Check.
    assert result.exit_code == 0
    assert config_mock.add_profile.call_count == 1


@mock.patch("modulos_client.cli.config_utils.get_modulos_config")
def test_logout(mock_config):
    # Prepare.
    config_mock = mock.MagicMock()
    config_mock.profiles = {"Peter": "Pan", "John": "Doe"}
    config_mock.remove_profile.return_value = None
    mock_config.return_value.__enter__.return_value = config_mock
    runner = CliRunner()

    # Test.
    result = runner.invoke(main, ["logout", "-f"])

    # Check.
    assert result.exit_code == 0
    assert result.output == (
        "This will remove all profiles. Do you want to continue?\nLogout successful.\n"
    )
    assert config_mock.remove_profile.call_count == 2


@mock.patch("modulos_client.cli.config_utils.get_modulos_config")
def test_logout__no_confirmation(mock_config):
    # Prepare.
    mock_config.return_value.__enter__.return_value = None
    runner = CliRunner()

    # Test.
    result = runner.invoke(main, ["logout"], input="n\n")

    # Check.
    assert result.exit_code == 0
    assert result.output == (
        "This will remove all profiles. Do you want to continue?\nContinue? [y/N]: n\n"
    )
