## Modulos Client Tool

This tool provides a command-line interface to interact with the Modulos platform.

### Prerequisites

- Python 3.x
- Setuptools and wheels:

```
pip install --upgrade pip setuptools wheel
```

- Install dependencies:

```
pip install modulos-client
```

### Usage

#### Logging In

To login to the Modulos platform:

```bash
modulos login --host [HOST_URL] --token [TOKEN] --profile-name [PROFILE_NAME]
```

- `[HOST]` is the address of the platform. For local use, this would typically be `http://localhost`.
- `[TOKEN]` is your authentication token.
- `[PROFILE_NAME]` is the name of the profile. It is used to reference the profile in the future. If you want to use multiple profiles, you can specify a different name for each profile.

#### Logging Out

To logout from the Modulos platform:

```bash
modulos logout
```

This will remove all profiles and locally stored data.

#### List profiles

List all profiles:

```bash
modulos profiles list
```

#### Profile activation

Activate a profile:

```bash
modulos profiles activate --profile-name [PROFILE_NAME]
```

This is useful if you have multiple profiles and want to switch between them.
Listing them will show you the currently active profile.

#### Deactivate a profile

With

```bash
modulos profiles deactivate --profile-name [PROFILE_NAME]
```

you can remove a profile.
The last currently used profile will be activated automatically.

#### Managing Organizations

In order to use the `modulos orgs` commands, you need to have superadmin permissions.

List all organizations:

```bash
modulos orgs list
```

Create a new organization:

```bash
modulos orgs create --name [ORG_NAME]
```

#### Managing Users

List all users:

```bash
modulos users list
```

Create a new user:

```bash
modulos users create --firstname [FIRST_NAME] --lastname [LAST_NAME] --email [EMAIL] --is-active [IS_ACTIVE] --is-org-admin [IS_ORG_ADMIN]
```

There is an optional `--organization-id` parameter to specify the organization the user should be created for.
If you don't specify it, the user will be created for the organization you are currently logged in to.
If the user should be created for a different organization, you need to have superadmin permissions.
For a user in the same organization, you need to have org admin permissions.

Add organization admin privileges to a user:

```bash
modulos users add-org-admin --user-id [USER_ID]
```

Remove organization administrator privileges from a user:

```bash
modulos users remove-org-admin --user-id [USER_ID]
```

#### Managing Projects

List all projects:

```bash
modulos projects list --page [PAGE_NUMBER]
```

Delete a project:

```bash
modulos projects delete --id [PROJECT_ID]
```

You need to have the `project.delete` permission for the project.

#### Managing Templates

List all templates:

```bash
modulos templates list
```

Upload templates for your organization:

```bash
modulos templates upload --file [FILE_PATH]
```

There is an optional `--organization-id` parameter to specify the organization the template should be uploaded for.
If you don't specify it, the template will be uploaded for the organization you are currently logged in to.
If the template should be uploaded for a different organization, you need to have superadmin permissions.

---

For a detailed list of available commands and their options, run:

```bash
modulos --help
```

This will provide a comprehensive list of commands and their descriptions.

---

© 2023 Modulos AG. All rights reserved.
