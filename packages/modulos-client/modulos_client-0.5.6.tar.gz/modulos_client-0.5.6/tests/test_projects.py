from unittest import mock

from click.testing import CliRunner

from modulos_client.projects import projects


@mock.patch("modulos_client.config.ModulosClient.from_conf_file")
def test_list_projects(mock_client):
    # Prepare.
    org_response = mock.MagicMock()
    org_response.json.return_value = {"organization": {"id": "my_org_id"}}
    project_response = mock.MagicMock()
    project_response.ok = True
    project_response.json.return_value = {
        "items": [
            {
                "id": "my_project_id",
                "name": "My Project",
                "organization": {"id": "my_org_id", "name": "My Org"},
                "description": "My description",
            },
        ],
        "page": 1,
    }
    mock_client.return_value.get.side_effect = [org_response, project_response]
    runner = CliRunner()

    # Test.
    result = runner.invoke(projects, ["list"])

    # Check.
    assert result.exit_code == 0
    assert result.output == (
        "\n\nPage: 1\nid             organization    name        description\n---------"
        "----  --------------  ----------  --------------\nmy_project_id  My Org       "
        "   My Project  My description\n"
    )


@mock.patch("modulos_client.config.ModulosClient.from_conf_file")
def test_list_projects__negative(mock_client):
    # Prepare.
    org_response = mock.MagicMock()
    org_response.json.return_value = {"organization": {"id": "my_org_id"}}
    project_response = mock.MagicMock()
    project_response.ok = False
    project_response.text = "Error message"
    mock_client.return_value.get.side_effect = [org_response, project_response]
    runner = CliRunner()

    # Test.
    result = runner.invoke(projects, ["list"])

    # Check.
    assert result.exit_code == 0
    assert result.output == "Could not list projects: Error message\n"


@mock.patch("modulos_client.config.ModulosClient.from_conf_file")
def test_delete_projects(mock_client):
    # Prepare.
    response = mock.MagicMock()
    response.ok = True
    mock_client.return_value.delete.return_value = response
    runner = CliRunner()

    # Test.
    result = runner.invoke(projects, ["delete", "--id", "my_project_id"])

    # Check.
    assert result.exit_code == 0
    assert result.output == "Project 'my_project_id' deleted.\n"


@mock.patch("modulos_client.config.ModulosClient.from_conf_file")
def test_delete_projects__negative(mock_client):
    # Prepare.
    response = mock.MagicMock()
    response.ok = False
    response.json.return_value = {"detail": "Error message"}
    mock_client.return_value.delete.return_value = response
    runner = CliRunner()

    # Test.
    result = runner.invoke(projects, ["delete", "--id", "my_project_id"])

    # Check.
    assert result.exit_code == 0
    assert result.output == "Could not delete project: Error message\n"
