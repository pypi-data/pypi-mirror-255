from modulos_client import config as config_utils


def get_user(user_id: str):
    client = config_utils.ModulosClient.from_conf_file()
    user_response = client.get(f"/users/{user_id}")
    if not user_response.ok:
        return None
    user = user_response.json()

    return user


def update_user(organization_id: str, user_id: str, user_dict: dict):
    client = config_utils.ModulosClient.from_conf_file()
    response = client.patch(
        f"/organizations/{organization_id}/users/{user_id}",
        user_dict,
    )
    if response.ok:
        return response.json()
    return None
