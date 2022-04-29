import requests
from requests import HTTPError

from xcube_hub import api, util
from xcube_hub.core import oauth
from xcube_hub.models.subscription import Subscription


def register(subscription: Subscription, raise_on_exist: bool = True):
    user = [{
        "user_name": f"geodb_{subscription.guid}",
        "start_date": f"{subscription.start_date}",
        "subscription": f"{subscription.plan}",
        "cells": int(subscription.units)
    }]

    client_id = util.maybe_raise_for_env("GEODB_ADMIN_CLIENT_ID")
    client_secret = util.maybe_raise_for_env("GEODB_ADMIN_CLIENT_SECRET")
    server_url = util.maybe_raise_for_env("GEODB_POSTGREST_REST_URL")

    oauth_token = dict(
        audience="https://xcube-gen.brockmann-consult.de/api/v2/",
        client_id=client_id,
        client_secret=client_secret,
        grant_type='client_secret'
    )
    token = oauth.get_token(oauth_token)
    headers = {'Authorization': f'Bearer {token}'}

    r = requests.post(f"{server_url}/geodb_user_info", json=user, headers=headers)

    try:
        r.raise_for_status()
    except HTTPError as e:
        if r.status_code == 409 and raise_on_exist is False:
            return r.status_code
        raise api.ApiError(r.status_code, str(e))

    return True
