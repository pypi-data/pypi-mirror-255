from unittest import mock

from modulos_client.services import users_services


@mock.patch("modulos_client.config.ModulosClient.from_conf_file")
def test_get_user(mock_client):
    # Prepare.
    exp_res = {"id": "my_id"}
    response = mock.MagicMock()
    response.ok = True
    response.json.return_value = exp_res
    mock_client.return_value.get.return_value = response

    # Test.
    result = users_services.get_user("my_id")

    # Check.
    assert result == exp_res


@mock.patch("modulos_client.config.ModulosClient.from_conf_file")
def test_get_user__negative(mock_client):
    # Prepare.
    response = mock.MagicMock()
    response.ok = False
    mock_client.return_value.get.return_value = response

    # Test.
    result = users_services.get_user("my_id")

    # Check.
    assert result is None


@mock.patch("modulos_client.config.ModulosClient.from_conf_file")
def test_update_user(mock_client):
    # Prepare.
    exp_res = {"id": "my_id"}
    response = mock.MagicMock()
    response.ok = True
    response.json.return_value = exp_res
    mock_client.return_value.patch.return_value = response

    # Test.
    result = users_services.update_user("my_org_id", "my_id", {})

    # Check.
    assert result == exp_res


@mock.patch("modulos_client.config.ModulosClient.from_conf_file")
def test_update_user__negative(mock_client):
    # Prepare.
    response = mock.MagicMock()
    response.ok = False
    mock_client.return_value.patch.return_value = response

    # Test.
    result = users_services.update_user("my_org_id", "my_id", {})

    # Check.
    assert result is None
