import os

from xcube_hub import api


def geodb_auth_login_app():
    try:
        client_id = os.environ.get("XCUBE_GEODB_AUTH_CLIENT_ID", None)
    except ValueError:
        raise api.ApiError(400, "Error: XCUBE_GEODB_AUTH_CLIENT_ID must be set")

    try:
        client_secret = os.environ.get("XCUBE_GEODB_AUTH_CLIENT_SECRET", None)
    except ValueError:
        raise api.ApiError(400, "Error: XCUBE_GEODB_AUTH_CLIENT_SECRET must be set.")

    return {"client_id": client_id, "client-secret": client_secret}
