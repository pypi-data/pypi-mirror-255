from unittest import mock

from click.testing import CliRunner

from modulos_client.users import users


@mock.patch("modulos_client.config.ModulosClient.from_conf_file")
def test_list_users(mock_client):
    # Prepare.
    response = mock.MagicMock()
    response.ok = True
    response.json.return_value = {
        "items": [
            {
                "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                "firstname": "Test",
                "lastname": "User",
                "email": "user@example.com",
                "job_title": "tester",
                "created_at": "2024-01-22T10:24:35.320Z",
                "is_active": True,
                "is_org_admin": False,
                "is_super_admin": False,
                "last_access": "2024-01-22T10:24:35.320Z",
                "roles": [],
                "projects": [],
            }
        ]
    }
    mock_client.return_value.get.return_value = response
    runner = CliRunner()

    # Test.
    result = runner.invoke(users, ["list", "--organization-id", "my_org_id"])

    # Check.
    assert result.exit_code == 0
    assert result.output == (
        "id                                    firstname    lastname    email         "
        "    is_super_admin    is_org_admin    is_active\n----------------------------"
        "--------  -----------  ----------  ----------------  ----------------  ------"
        "--------  -----------\n3fa85f64-5717-4562-b3fc-2c963f66afa6  Test         Use"
        "r        user@example.com  False             False           True\n"
    )


@mock.patch("modulos_client.config.ModulosClient.from_conf_file")
def test_list_users__negative(mock_client):
    # Prepare.
    response = mock.MagicMock()
    response.ok = False
    response.json.return_value = {"organization": {"id": "my_org_id"}}
    response.text = "Something went wrong."
    mock_client.return_value.get.return_value = response
    runner = CliRunner()

    # Test.
    result = runner.invoke(users, ["list"])

    # Check.
    assert result.exit_code == 0
    assert result.output == "Could not list users: Something went wrong.\n"


@mock.patch("modulos_client.config.ModulosClient.from_conf_file")
def test_create_users(mock_client):
    # Prepare.
    response = mock.MagicMock()
    response.ok = True
    get_response = mock.MagicMock()
    get_response.json.return_value = {"organization": {"id": "my_org_id"}}
    mock_client.return_value.post.return_value = response
    mock_client.return_value.get.return_value = get_response
    runner = CliRunner()

    # Test.
    result = runner.invoke(
        users,
        [
            "create",
            "--firstname",
            "Test",
            "--lastname",
            "User",
            "--email",
            "user@example.com",
            "--is-active",
            "true",
            "--is-org-admin",
            "false",
        ],
    )

    # Check.
    assert result.exit_code == 0
    assert result.output == "User 'user@example.com' created.\n"


@mock.patch("modulos_client.config.ModulosClient.from_conf_file")
def test_create_users__negative(mock_client):
    # Prepare.
    post_response = mock.MagicMock()
    post_response.ok = False
    post_response.json.return_value = {"detail": "Something went wrong."}
    get_response = mock.MagicMock()
    get_response.json.return_value = {"organization": {"id": "my_org_id"}}
    mock_client.return_value.post.return_value = post_response
    mock_client.return_value.get.return_value = get_response
    runner = CliRunner()

    # Test.
    result = runner.invoke(
        users,
        [
            "create",
            "--organization-id",
            "my_org_id",
            "--firstname",
            "Test",
            "--lastname",
            "User",
            "--email",
            "user@example.com",
            "--is-active",
            "true",
            "--is-org-admin",
            "false",
        ],
    )

    # Check.
    assert result.exit_code == 0
    assert result.output == "Could not create user: Something went wrong.\n"


@mock.patch("modulos_client.config.ModulosClient.from_conf_file")
def test_add_users_role(mock_client):
    # Prepare.
    response = mock.MagicMock()
    response.ok = True
    mock_client.return_value.post.return_value = response
    runner = CliRunner()

    # Test.
    result = runner.invoke(
        users,
        [
            "add-role",
            "--user-id",
            "my_user_id",
            "--project-id",
            "my_project_id",
            "--role",
            "my_role",
        ],
    )

    # Check.
    assert result.exit_code == 0
    assert result.output == "Role 'my_role' added to user 'my_user_id'.\n"


@mock.patch("modulos_client.config.ModulosClient.from_conf_file")
def test_add_users_role__negative(mock_client):
    # Prepare.
    response = mock.MagicMock()
    response.ok = False
    response.json.return_value = {"detail": "Something went wrong."}
    mock_client.return_value.post.return_value = response
    runner = CliRunner()

    # Test.
    result = runner.invoke(
        users,
        [
            "add-role",
            "--user-id",
            "my_user_id",
            "--project-id",
            "my_project_id",
            "--role",
            "my_role",
        ],
    )

    # Check.
    assert result.exit_code == 0
    assert result.output == "Could not add role to user: Something went wrong.\n"


@mock.patch("modulos_client.config.ModulosClient.from_conf_file")
def test_remove_users_role(mock_config):
    # Prepare.
    response = mock.MagicMock()
    response.ok = True
    mock_config.return_value.delete.return_value = response
    runner = CliRunner()

    # Test.
    result = runner.invoke(
        users,
        [
            "remove-role",
            "--user-id",
            "my_user_id",
            "--project-id",
            "my_project_id",
            "--role",
            "my_role",
        ],
    )

    # Check.
    assert result.exit_code == 0
    assert result.output == "Role 'my_role' removed from user 'my_user_id'.\n"


@mock.patch("modulos_client.config.ModulosClient.from_conf_file")
def test_remove_users_role__negative(mock_config):
    # Prepare.
    response = mock.MagicMock()
    response.ok = False
    response.json.return_value = {"detail": "Something went wrong."}
    mock_config.return_value.delete.return_value = response
    runner = CliRunner()

    # Test.
    result = runner.invoke(
        users,
        [
            "remove-role",
            "--user-id",
            "my_user_id",
            "--project-id",
            "my_project_id",
            "--role",
            "my_role",
        ],
    )

    # Check.
    assert result.exit_code == 0
    assert result.output == "Could not remove role from user: Something went wrong.\n"


@mock.patch("modulos_client.config.ModulosClient.from_conf_file")
def test_activate_user(mock_config):
    # Prepare.
    get_response = mock.MagicMock()
    get_response.ok = True
    get_response.json.return_value = {"organization": {"id": "my_org_id"}}
    patch_response = mock.MagicMock()
    patch_response.ok = True
    mock_config.return_value.get.return_value = get_response
    mock_config.return_value.patch.return_value = patch_response
    runner = CliRunner()

    # Test.
    result = runner.invoke(
        users,
        [
            "activate",
            "--user-id",
            "my_user_id",
        ],
    )

    # Check.
    assert result.exit_code == 0
    assert result.output == "User 'my_user_id' activated.\n"


@mock.patch("modulos_client.config.ModulosClient.from_conf_file")
def test_activate_user__negative_no_user(mock_config):
    # Prepare.
    get_response = mock.MagicMock()
    get_response.ok = False
    mock_config.return_value.get.return_value = get_response
    runner = CliRunner()

    # Test.
    result = runner.invoke(
        users,
        [
            "activate",
            "--user-id",
            "my_user_id",
        ],
    )

    # Check.
    assert result.exit_code == 0
    assert result.output == "User 'my_user_id' not found.\n"


@mock.patch("modulos_client.config.ModulosClient.from_conf_file")
def test_activate_user__negative_error(mock_config):
    # Prepare.
    get_response = mock.MagicMock()
    get_response.ok = True
    get_response.json.return_value = {"organization": {"id": "my_org_id"}}
    patch_response = mock.MagicMock()
    patch_response.ok = False
    patch_response.json.return_value = {"detail": "Something went wrong."}
    mock_config.return_value.get.return_value = get_response
    mock_config.return_value.patch.return_value = patch_response
    runner = CliRunner()

    # Test.
    result = runner.invoke(
        users,
        [
            "activate",
            "--user-id",
            "my_user_id",
        ],
    )

    # Check.
    assert result.exit_code == 0
    assert result.output == "Could not activate user: Something went wrong.\n"


@mock.patch("modulos_client.config.ModulosClient.from_conf_file")
def test_deactivate_user(mock_config):
    # Prepare.
    get_response = mock.MagicMock()
    get_response.ok = True
    get_response.json.return_value = {"organization": {"id": "my_org_id"}}
    patch_response = mock.MagicMock()
    patch_response.ok = True
    mock_config.return_value.get.return_value = get_response
    mock_config.return_value.patch.return_value = patch_response
    runner = CliRunner()

    # Test.
    result = runner.invoke(
        users,
        [
            "deactivate",
            "--user-id",
            "my_user_id",
        ],
    )

    # Check.
    assert result.exit_code == 0
    assert result.output == "User 'my_user_id' deactivated.\n"


@mock.patch("modulos_client.config.ModulosClient.from_conf_file")
def test_deactivate_user__negative_no_user(mock_config):
    # Prepare.
    get_response = mock.MagicMock()
    get_response.ok = False
    mock_config.return_value.get.return_value = get_response
    runner = CliRunner()

    # Test.
    result = runner.invoke(
        users,
        [
            "deactivate",
            "--user-id",
            "my_user_id",
        ],
    )

    # Check.
    assert result.exit_code == 0
    assert result.output == "User 'my_user_id' not found.\n"


@mock.patch("modulos_client.config.ModulosClient.from_conf_file")
def test_deactivate_user__negative_error(mock_config):
    # Prepare.
    get_response = mock.MagicMock()
    get_response.ok = True
    get_response.json.return_value = {"organization": {"id": "my_org_id"}}
    patch_response = mock.MagicMock()
    patch_response.ok = False
    patch_response.json.return_value = {"detail": "Something went wrong."}
    mock_config.return_value.get.return_value = get_response
    mock_config.return_value.patch.return_value = patch_response
    runner = CliRunner()

    # Test.
    result = runner.invoke(
        users,
        [
            "deactivate",
            "--user-id",
            "my_user_id",
        ],
    )

    # Check.
    assert result.exit_code == 0
    assert result.output == "Could not deactivate user: Something went wrong.\n"


@mock.patch("modulos_client.services.users_services.get_user")
@mock.patch("modulos_client.services.users_services.update_user")
def test_add_org_admin(mock_update_user, mock_get_user):
    # Prepare.
    mock_get_user.return_value = {
        "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
        "firstname": "Test",
        "lastname": "User",
        "email": "user@example.com",
        "job_title": "tester",
        "created_at": "2024-01-22T10:24:35.320Z",
        "is_active": True,
        "is_org_admin": False,
        "is_super_admin": False,
        "last_access": "2024-01-22T10:24:35.320Z",
        "roles": [],
        "projects": [],
        "organization": {
            "id": "my_org_id",
            "name": "My Org",
        },
    }
    mock_update_user.return_value = "success"
    runner = CliRunner()

    # Test.
    result = runner.invoke(
        users,
        [
            "add-org-admin",
            "--user-id",
            "my_user_id",
        ],
        input="y\n",
    )

    # Check.
    assert result.exit_code == 0
    assert result.output == (
        "User: \nid                                    firstname    lastname    email  "
        "           is_super_admin    is_org_admin    is_active\n----------------------"
        "--------------  -----------  ----------  ----------------  ----------------  -"
        "-------------  -----------\n3fa85f64-5717-4562-b3fc-2c963f66afa6  Test        "
        " User        user@example.com  False             False           True\n\nOrgan"
        "ization: \nid         name\n---------  ------\nmy_org_id  My Org\n\nContinue? "
        "[y/N]: y\nUser 'my_user_id' is now an organization admin.\n"
    )


@mock.patch("modulos_client.services.users_services.get_user")
@mock.patch("modulos_client.services.users_services.update_user")
def test_add_org_admin__fail_to_update(mock_update_user, mock_get_user):
    # Prepare.
    mock_get_user.return_value = {
        "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
        "firstname": "Test",
        "lastname": "User",
        "email": "user@example.com",
        "job_title": "tester",
        "created_at": "2024-01-22T10:24:35.320Z",
        "is_active": True,
        "is_org_admin": False,
        "is_super_admin": False,
        "last_access": "2024-01-22T10:24:35.320Z",
        "roles": [],
        "projects": [],
        "organization": {
            "id": "my_org_id",
            "name": "My Org",
        },
    }
    mock_update_user.return_value = None
    runner = CliRunner()

    # Test.
    result = runner.invoke(
        users,
        [
            "add-org-admin",
            "--user-id",
            "my_user_id",
        ],
        input="y\n",
    )

    # Check.
    assert result.exit_code == 0
    assert result.output == (
        "User: \nid                                    firstname    lastname    email  "
        "           is_super_admin    is_org_admin    is_active\n----------------------"
        "--------------  -----------  ----------  ----------------  ----------------  -"
        "-------------  -----------\n3fa85f64-5717-4562-b3fc-2c963f66afa6  Test        "
        " User        user@example.com  False             False           True\n\nOrgan"
        "ization: \nid         name\n---------  ------\nmy_org_id  My Org\n\nContinue? "
        "[y/N]: y\nCould not add org admin privileges to user.\n"
    )


@mock.patch("modulos_client.services.users_services.get_user")
def test_add_org_admin__aborted(mock_get_user):
    # Prepare.
    mock_get_user.return_value = {
        "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
        "firstname": "Test",
        "lastname": "User",
        "email": "user@example.com",
        "job_title": "tester",
        "created_at": "2024-01-22T10:24:35.320Z",
        "is_active": True,
        "is_org_admin": False,
        "is_super_admin": False,
        "last_access": "2024-01-22T10:24:35.320Z",
        "roles": [],
        "projects": [],
        "organization": {
            "id": "my_org_id",
            "name": "My Org",
        },
    }
    runner = CliRunner()

    # Test.
    result = runner.invoke(
        users,
        [
            "add-org-admin",
            "--user-id",
            "my_user_id",
        ],
        input="n\n",
    )

    # Check.
    assert result.exit_code == 0
    assert result.output == (
        "User: \nid                                    firstname    lastname    email  "
        "           is_super_admin    is_org_admin    is_active\n----------------------"
        "--------------  -----------  ----------  ----------------  ----------------  -"
        "-------------  -----------\n3fa85f64-5717-4562-b3fc-2c963f66afa6  Test        "
        " User        user@example.com  False             False           True\n\nOrgan"
        "ization: \nid         name\n---------  ------\nmy_org_id  My Org\n\nContinue? "
        "[y/N]: n\n"
    )


@mock.patch("modulos_client.services.users_services.get_user")
def test_add_org_admin___no_user_org(mock_get_user):
    # Prepare.
    mock_get_user.return_value = {
        "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
        "firstname": "Test",
        "lastname": "User",
        "email": "user@example.com",
        "job_title": "tester",
        "created_at": "2024-01-22T10:24:35.320Z",
        "is_active": True,
        "is_org_admin": False,
        "is_super_admin": False,
        "last_access": "2024-01-22T10:24:35.320Z",
        "roles": [],
        "projects": [],
        "organization": {},
    }
    runner = CliRunner()

    # Test.
    result = runner.invoke(
        users,
        [
            "add-org-admin",
            "--user-id",
            "my_user_id",
        ],
    )

    # Check.
    assert result.exit_code == 0
    assert result.output == "The user does not have an associated organization\n"


@mock.patch("modulos_client.services.users_services.get_user")
def test_add_org_admin___no_user(mock_get_user):
    # Prepare.
    mock_get_user.return_value = None
    runner = CliRunner()

    # Test.
    result = runner.invoke(
        users,
        [
            "add-org-admin",
            "--user-id",
            "my_user_id",
        ],
    )

    # Check.
    assert result.exit_code == 0
    assert result.output == "User 'my_user_id' not found.\n"


@mock.patch("modulos_client.services.users_services.get_user")
@mock.patch("modulos_client.services.users_services.update_user")
def test_remove_org_admin(mock_update_user, mock_get_user):
    # Prepare.
    mock_get_user.return_value = {
        "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
        "firstname": "Test",
        "lastname": "User",
        "email": "user@example.com",
        "job_title": "tester",
        "created_at": "2024-01-22T10:24:35.320Z",
        "is_active": True,
        "is_org_admin": False,
        "is_super_admin": False,
        "last_access": "2024-01-22T10:24:35.320Z",
        "roles": [],
        "projects": [],
        "organization": {
            "id": "my_org_id",
            "name": "My Org",
        },
    }
    mock_update_user.return_value = "success"
    runner = CliRunner()

    # Test.
    result = runner.invoke(
        users,
        [
            "remove-org-admin",
            "--user-id",
            "my_user_id",
        ],
        input="y\n",
    )

    # Check.
    assert result.exit_code == 0
    assert result.output == (
        "User: \nid                                    firstname    lastname    email  "
        "           is_super_admin    is_org_admin    is_active\n----------------------"
        "--------------  -----------  ----------  ----------------  ----------------  -"
        "-------------  -----------\n3fa85f64-5717-4562-b3fc-2c963f66afa6  Test        "
        " User        user@example.com  False             False           True\n\nOrgan"
        "ization: \nid         name\n---------  ------\nmy_org_id  My Org\n\nContinue? "
        "[y/N]: y\nUser 'my_user_id' is no longer an organization admin.\n"
    )


@mock.patch("modulos_client.services.users_services.get_user")
@mock.patch("modulos_client.services.users_services.update_user")
def test_remove_org_admin__fail_to_update(mock_update_user, mock_get_user):
    # Prepare.
    mock_get_user.return_value = {
        "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
        "firstname": "Test",
        "lastname": "User",
        "email": "user@example.com",
        "job_title": "tester",
        "created_at": "2024-01-22T10:24:35.320Z",
        "is_active": True,
        "is_org_admin": False,
        "is_super_admin": False,
        "last_access": "2024-01-22T10:24:35.320Z",
        "roles": [],
        "projects": [],
        "organization": {
            "id": "my_org_id",
            "name": "My Org",
        },
    }
    mock_update_user.return_value = None
    runner = CliRunner()

    # Test.
    result = runner.invoke(
        users,
        [
            "remove-org-admin",
            "--user-id",
            "my_user_id",
        ],
        input="y\n",
    )

    # Check.
    assert result.exit_code == 0
    assert result.output == (
        "User: \nid                                    firstname    lastname    email  "
        "           is_super_admin    is_org_admin    is_active\n----------------------"
        "--------------  -----------  ----------  ----------------  ----------------  -"
        "-------------  -----------\n3fa85f64-5717-4562-b3fc-2c963f66afa6  Test        "
        " User        user@example.com  False             False           True\n\nOrgan"
        "ization: \nid         name\n---------  ------\nmy_org_id  My Org\n\nContinue? "
        "[y/N]: y\nCould not remove org admin privileges from user.\n"
    )


@mock.patch("modulos_client.services.users_services.get_user")
def test_remove_org_admin__aborted(mock_get_user):
    # Prepare.
    mock_get_user.return_value = {
        "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
        "firstname": "Test",
        "lastname": "User",
        "email": "user@example.com",
        "job_title": "tester",
        "created_at": "2024-01-22T10:24:35.320Z",
        "is_active": True,
        "is_org_admin": False,
        "is_super_admin": False,
        "last_access": "2024-01-22T10:24:35.320Z",
        "roles": [],
        "projects": [],
        "organization": {
            "id": "my_org_id",
            "name": "My Org",
        },
    }
    runner = CliRunner()

    # Test.
    result = runner.invoke(
        users,
        [
            "remove-org-admin",
            "--user-id",
            "my_user_id",
        ],
        input="n\n",
    )

    # Check.
    assert result.exit_code == 0
    assert result.output == (
        "User: \nid                                    firstname    lastname    email  "
        "           is_super_admin    is_org_admin    is_active\n----------------------"
        "--------------  -----------  ----------  ----------------  ----------------  -"
        "-------------  -----------\n3fa85f64-5717-4562-b3fc-2c963f66afa6  Test        "
        " User        user@example.com  False             False           True\n\nOrgan"
        "ization: \nid         name\n---------  ------\nmy_org_id  My Org\n\nContinue? "
        "[y/N]: n\n"
    )


@mock.patch("modulos_client.services.users_services.get_user")
def test_remove_org_admin___no_user_org(mock_get_user):
    # Prepare.
    mock_get_user.return_value = {
        "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
        "firstname": "Test",
        "lastname": "User",
        "email": "user@example.com",
        "job_title": "tester",
        "created_at": "2024-01-22T10:24:35.320Z",
        "is_active": True,
        "is_org_admin": False,
        "is_super_admin": False,
        "last_access": "2024-01-22T10:24:35.320Z",
        "roles": [],
        "projects": [],
        "organization": {},
    }
    runner = CliRunner()

    # Test.
    result = runner.invoke(
        users,
        [
            "remove-org-admin",
            "--user-id",
            "my_user_id",
        ],
        input="n\n",
    )

    # Check.
    assert result.exit_code == 0
    assert result.output == "The user does not have an associated organization\n"


@mock.patch("modulos_client.services.users_services.get_user")
def test_remove_org_admin___no_user(mock_get_user):
    # Prepare.
    mock_get_user.return_value = None
    runner = CliRunner()

    # Test.
    result = runner.invoke(
        users,
        [
            "remove-org-admin",
            "--user-id",
            "my_user_id",
        ],
    )

    # Check.
    assert result.exit_code == 0
    assert result.output == "User 'my_user_id' not found.\n"
