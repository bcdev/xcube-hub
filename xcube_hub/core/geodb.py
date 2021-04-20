from typing import Dict

import requests
from requests import HTTPError

from xcube_hub import api
from xcube_hub.models.subscription import Subscription


def register_user(user_id: str, subscription: Subscription, headers: Dict, raising: bool = True):
    user = [{
        "user_name": f"geodb_{subscription.guid}",
        "start_date": f"{subscription.start_date}",
        "subscription": f"{subscription.plan}",
        "cells": int(subscription.units)
    }]

    r = requests.post("https://xcube-geodb.brockmann-consult.de/geodb_user_info", json=user, headers=headers)

    try:
        r.raise_for_status()
    except HTTPError as e:
        if raising:
            raise api.ApiError(r.status_code, str(e))
        return r.status_code

    return True
