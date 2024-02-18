import filecmp
import os
import tempfile
from unittest import mock

import pytest

from modulos_client import config


@mock.patch("modulos_client.config.ModulosClient.get")
@mock.patch("modulos_client.config.get_modulos_config")
def test_from_conf_file(mock_config, mock_get):
    # Prepare.
    config_mock = mock.MagicMock()
    config_mock.active_profile = "Peter"
    profile = config.ModulosProfile(
        name="Peter",
        host="http://localhost",
        token="my_token",
    )
    config_mock.get_active_profile.return_value = profile
    mock_config.return_value.__enter__.return_value = config_mock
    mock_get.return_value.status_code = 200

    # Test.
    client = config.ModulosClient.from_conf_file()

    # Check.
    assert client.host == "http://localhost/api"
    assert client.token == "my_token"


@mock.patch("modulos_client.config.get_modulos_config")
def test_from_conf_file__negative_no_active_profile(mock_config):
    # Prepare.
    config_mock = mock.MagicMock()
    config_mock.active_profile = None
    mock_config.return_value.__enter__.return_value = config_mock

    # Test.
    with pytest.raises(ValueError) as excinfo:
        config.ModulosClient.from_conf_file()

    # Check.
    assert excinfo.value.args[0] == "No active profile."


@mock.patch("modulos_client.config.ModulosClient.get")
@mock.patch("modulos_client.config.get_modulos_config")
def test_from_conf_file__no_valid_token(mock_config, mock_get, capsys):
    # Prepare.
    config_mock = mock.MagicMock()
    config_mock.active_profile = "Peter"
    profile = config.ModulosProfile(
        name="Peter",
        host="http://localhost",
        token="my_token",
    )
    config_mock.get_active_profile.return_value = profile
    mock_config.return_value.__enter__.return_value = config_mock
    mock_get.return_value.status_code = 401

    # Test.
    with pytest.raises(SystemExit):
        config.ModulosClient.from_conf_file()
    captured = capsys.readouterr()

    # Check.
    assert captured.out == "Token is not valid anymore. Please login again.\n"


@mock.patch("requests.post")
def test_post(mock_post):
    # Prepare.
    mock_post.return_value = "my_response"
    client = config.ModulosClient(host="http://localhost", token="my_token")

    # Test.
    response = client.post("auth/token/status", url_params={"a": "b"})

    # Check.
    assert response == "my_response"


@mock.patch("requests.get")
def test_get(mock_get):
    # Prepare.
    mock_get.return_value = "my_response"
    client = config.ModulosClient(host="http://localhost", token="my_token")

    # Test.
    response = client.get("auth/token/status")

    # Check.
    assert response == "my_response"


@mock.patch("requests.delete")
def test_delete(mock_delete):
    # Prepare.
    mock_delete.return_value = "my_response"
    client = config.ModulosClient(host="http://localhost", token="my_token")

    # Test.
    response = client.delete("auth/token/status", url_params={"a": "b"})

    # Check.
    assert response == "my_response"


@mock.patch("requests.patch")
def test_patch(mock_patch):
    # Prepare.
    mock_patch.return_value = "my_response"
    client = config.ModulosClient(host="http://localhost", token="my_token")

    # Test.
    response = client.patch("auth/token/status", data={"a": "b"})

    # Check.
    assert response == "my_response"


def test_modulos_config_from_file(config_file):
    # Test.
    config_obj = config.ModulosConfig.from_file(config_file)

    # Check.
    assert config_obj.active_profile == "Peter"
    assert config_obj.profiles == {
        "Peter": config.ModulosProfile(
            name="Peter",
            host="http://localhost",
            token="my_token",
        )
    }


def test_modulos_config_save_to_file(config_file):
    # Prepare.
    with tempfile.NamedTemporaryFile() as f:
        config_obj = config.ModulosConfig.from_file(config_file)

        # Test.
        config_obj.save_to_file(f.name)

        # Check.
        assert filecmp.cmp(config_file, f.name)


def test_modulos_config_get_active_profile(config_file):
    # Prepare.
    config_obj = config.ModulosConfig.from_file(config_file)

    # Test.
    profile = config_obj.get_active_profile()

    # Check.
    assert profile == config.ModulosProfile(
        name="Peter",
        host="http://localhost",
        token="my_token",
    )


def test_modulos_config_get_active_profile__negative_no_active_profile():
    # Prepare.
    config_obj = config.ModulosConfig(active_profile=None, profiles={})

    # Test.
    with pytest.raises(ValueError) as excinfo:
        config_obj.get_active_profile()

    # Check.
    assert excinfo.value.args[0] == "No active profile. Please Login first."


def test_remove_profile(config_file):
    # Prepare.
    config_obj = config.ModulosConfig.from_file(config_file)

    # Test.
    config_obj.remove_profile("Peter")

    # Check.
    assert config_obj.profiles == {}
    assert config_obj.active_profile is None


def test_remove_profile__two_profiles(config_file_two_profiles):
    # Prepare.
    config_obj = config.ModulosConfig.from_file(config_file_two_profiles)

    # Test.
    config_obj.remove_profile("Peter")

    # Check.
    assert config_obj.profiles == {
        "Pan": config.ModulosProfile(
            name="Pan",
            host="http://localhost",
            token="other_token",
        )
    }
    assert config_obj.active_profile == "Pan"


def test_remove_profile__negative_not_existing(config_file):
    # Prepare.
    config_obj = config.ModulosConfig.from_file(config_file)

    # Test.
    with pytest.raises(ValueError) as excinfo:
        config_obj.remove_profile("not_existing")

    # Check.
    assert excinfo.value.args[0] == "Profile 'not_existing' does not exist."


def test_add_profile(config_file):
    # Prepare.
    config_obj = config.ModulosConfig.from_file(config_file)

    # Test.
    config_obj.add_profile("Pan", "http://localhost", "other_token")

    # Check.
    assert config_obj.profiles == {
        "Peter": config.ModulosProfile(
            name="Peter",
            host="http://localhost",
            token="my_token",
        ),
        "Pan": config.ModulosProfile(
            name="Pan",
            host="http://localhost",
            token="other_token",
        ),
    }
    assert config_obj.active_profile == "Pan"


@mock.patch("click.confirm")
def test_add_profile__overwrite(mock_confirm, config_file):
    # Prepare.
    config_obj = config.ModulosConfig.from_file(config_file)
    mock_confirm.return_value = True

    # Test.
    config_obj.add_profile("Peter", "http://localhost", "other_token")

    # Check.
    assert config_obj.profiles == {
        "Peter": config.ModulosProfile(
            name="Peter",
            host="http://localhost",
            token="other_token",
        ),
    }
    assert config_obj.active_profile == "Peter"


@mock.patch("click.confirm")
def test_add_profile__overwrite_not_confirmed(mock_confirm, config_file, capsys):
    # Prepare.
    config_obj = config.ModulosConfig.from_file(config_file)
    mock_confirm.return_value = False

    # Test.
    config_obj.add_profile("Peter", "http://localhost", "other_token")
    captured = capsys.readouterr()

    # Check.
    assert config_obj.profiles == {
        "Peter": config.ModulosProfile(
            name="Peter",
            host="http://localhost",
            token="my_token",
        ),
    }
    assert config_obj.active_profile == "Peter"
    assert captured.out == (
        "Profile 'Peter' already exists. Do you want to overwrite it?\n"
    )


def test_add_profile__no_http(config_file, capsys):
    # Prepare.
    config_obj = config.ModulosConfig.from_file(config_file)

    # Test.
    config_obj.add_profile("Pan", "localhost", "other_token")
    captured = capsys.readouterr()

    # Check.
    assert config_obj.profiles == {
        "Peter": config.ModulosProfile(
            name="Peter",
            host="http://localhost",
            token="my_token",
        )
    }
    assert config_obj.active_profile == "Peter"
    assert captured.out == "Host must start with 'http' or 'https'.\n"


def test_get_modulos_config(config_file):
    # Prepare.
    with mock.patch("modulos_client.config.MODULOS_CONFIG_FILE", config_file):
        with config.get_modulos_config() as config_obj:
            # Check.
            assert config_obj.active_profile == "Peter"
            assert config_obj.profiles == {
                "Peter": config.ModulosProfile(
                    name="Peter",
                    host="http://localhost",
                    token="my_token",
                )
            }


def test_get_modulos_config__not_existing():
    # Prepare.
    with tempfile.TemporaryDirectory() as tmpdirname:
        with mock.patch(
            "modulos_client.config.MODULOS_CONFIG_FILE",
            os.path.join(tmpdirname, "some_dir", "config.yml"),
        ):
            with config.get_modulos_config() as config_obj:
                # Check.
                assert config_obj.active_profile is None
                assert config_obj.profiles == {}


def test_get_modulos_config__error_raised(config_file):
    # Prepare.
    with mock.patch("modulos_client.config.MODULOS_CONFIG_FILE", config_file):
        with pytest.raises(ValueError) as excinfo:
            with config.get_modulos_config() as config_obj:
                # Test.
                config_obj.remove_profile("not_existing")

    # Check.
    assert excinfo.value.args[0] == "Profile 'not_existing' does not exist."
