import tempfile
from unittest import mock

from click.testing import CliRunner

from modulos_client.templates import templates


@mock.patch("modulos_client.config.ModulosClient.from_conf_file")
def test_list_templates(mock_client):
    # Prepare.
    response = mock.MagicMock()
    response.ok = True
    response.json.return_value = [
        {
            "project_type": "ai_application",
            "framework_label": "label",
            "framework_code": "MCF_999",
            "framework_name": "my_framework",
            "framework_description": "my_framework_description",
            "framework_icon": "eu",
            "framework_icon_type": "flag",
            "framework_mapped_requirement_codes": [
                "MCR_001",
            ],
            "number_of_requirements": 1,
            "number_of_controls": 3,
        }
    ]
    mock_client.return_value.get.return_value = response
    runner = CliRunner()

    # Test.
    result = runner.invoke(templates, ["list", "--organization-id", "my_org_id"])

    # Check.
    assert result.exit_code == 0
    assert result.output == (
        "framework_code    framework_name    framework_description     framework_icon"
        "      number_of_requirements    number_of_controls\n----------------  ------"
        "----------  ------------------------  ----------------  --------------------"
        "----  --------------------\nMCF_999           my_framework      "
        "my_framework_description  eu                                       1        "
        "             3\n"
    )


@mock.patch("modulos_client.config.ModulosClient.from_conf_file")
def test_list_templates__negative(mock_client):
    # Prepare.
    response = mock.MagicMock()
    response.ok = False
    response.json.return_value = {"organization": {"id": "my_org_id"}}
    response.text = "error"
    mock_client.return_value.get.return_value = response
    runner = CliRunner()

    # Test.
    result = runner.invoke(templates, ["list"])

    # Check.
    assert result.exit_code == 0
    assert result.output == "Could not list templates: error\n"


@mock.patch("modulos_client.config.ModulosClient.from_conf_file")
def test_upload_templates(mock_client):
    # Prepare.
    response = mock.MagicMock()
    response.ok = True
    mock_client.return_value.post.return_value = response
    runner = CliRunner()
    with tempfile.NamedTemporaryFile() as f:
        # Test.
        result = runner.invoke(
            templates,
            [
                "upload",
                "--organization-id",
                "my_org_id",
                "--file",
                f.name,
            ],
        )

    # Check.
    assert result.exit_code == 0
    assert result.output == "Templates uploaded.\n"


@mock.patch("modulos_client.config.ModulosClient.from_conf_file")
def test_upload_templates__negative(mock_client):
    # Prepare.
    post_response = mock.MagicMock()
    post_response.ok = False
    post_response.text = "error"
    get_response = mock.MagicMock()
    get_response.json.return_value = {"organization": {"id": "my_org_id"}}
    mock_client.return_value.post.return_value = post_response
    mock_client.return_value.get.return_value = get_response
    runner = CliRunner()
    with tempfile.NamedTemporaryFile() as f:
        # Test.
        result = runner.invoke(
            templates,
            [
                "upload",
                "--file",
                f.name,
            ],
        )

    # Check.
    assert result.exit_code == 0
    assert result.output == "Could not upload templates: error\n"
