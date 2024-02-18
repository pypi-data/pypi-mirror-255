from unittest import mock

from click.testing import CliRunner

from modulos_client.organizations import orgs


@mock.patch("modulos_client.config.ModulosClient.from_conf_file")
def test_organization_list(mock_client):
    # Prepare.
    response = mock.MagicMock()
    response.ok = True
    response.json.return_value = {"items": [{"name": "Peter"}, {"name": "John"}]}
    mock_client.return_value.get.return_value = response
    runner = CliRunner()

    # Test.
    result = runner.invoke(orgs, ["list"])

    # Check.
    assert result.exit_code == 0
    assert result.output == "name\n------\nPeter\nJohn\n"


@mock.patch("modulos_client.config.ModulosClient.from_conf_file")
def test_organization_list__negative(mock_client):
    # Prepare.
    response = mock.MagicMock()
    response.ok = False
    response.text = "Error"
    mock_client.return_value.get.return_value = response
    runner = CliRunner()

    # Test.
    result = runner.invoke(orgs, ["list"])

    # Check.
    assert result.exit_code == 0
    assert result.output == "Could not list organizations: Error\n"


@mock.patch("modulos_client.config.ModulosClient.from_conf_file")
def test_organization_create(mock_client):
    # Prepare.
    response = mock.MagicMock()
    response.ok = True
    mock_client.return_value.post.return_value = response
    runner = CliRunner()

    # Test.
    result = runner.invoke(
        orgs,
        [
            "create",
            "--name",
            "my_org",
            "--enable-monitoring",
            "true",
            "--enable-domain-signup",
            "true",
            "--domain",
            "my_domain",
        ],
    )

    # Check.
    assert result.exit_code == 0
    assert result.output == "Organization 'my_org' created.\n"


@mock.patch("modulos_client.config.ModulosClient.from_conf_file")
def test_organization_create__negative(mock_client):
    # Prepare.
    response = mock.MagicMock()
    response.ok = False
    response.json.return_value = {"detail": "Error"}
    mock_client.return_value.post.return_value = response
    runner = CliRunner()

    # Test.
    result = runner.invoke(
        orgs,
        [
            "create",
            "--name",
            "my_org",
            "--enable-monitoring",
            "true",
            "--enable-domain-signup",
            "true",
            "--domain",
            "my_domain",
        ],
    )

    # Check.
    assert result.exit_code == 0
    assert result.output == "Could not create organization: Error\n"
