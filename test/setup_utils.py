import http.client
import json
import os
from dotenv import load_dotenv

from dotenv import load_dotenv


def setup_auth():
    load_dotenv()
    conn = http.client.HTTPSConnection("edc.eu.auth0.com")

    load_dotenv()

    client_id = os.getenv('AUTH0_CLIENT_ID')
    client_secret = os.getenv('AUTH0_CLIENT_SECRET')

    payload = "{\"client_id\":\"" + client_id + "\"," \
              "\"client_secret\":\"" + client_secret + "\"," \
              "\"audience\":\"https://xcube-gen.brockmann-consult.de/api/v1/\"," \
              "\"grant_type\":\"client_credentials\"}"

    headers = {'content-type': "application/json"}

    conn.request("POST", "/oauth/token", payload, headers)

    res = conn.getresponse()
    data = res.read()
    conn.close()

    return json.loads(data.decode("utf-8"))


def set_env():
    from dotenv import load_dotenv

    load_dotenv()
