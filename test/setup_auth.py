import http.client
import json


def setup_auth():
    conn = http.client.HTTPSConnection("edc.eu.auth0.com")
    payload = "{\"client_id\":\"13eBlDZ6a4pQr5oY9gm26YZ1coRZTs3J\"," \
              "\"client_secret\":\"iiXKa3zmyMnmj0fyeC_93Gf9bDKe4Pf-Q-D5naljNSfQ7q8t_iLVE9vQinCQZUv5\"," \
              "\"audience\":\"https://xcube-gen.brockmann-consult.de/api/v1/\"," \
              "\"grant_type\":\"client_credentials\"}"

    headers = {'content-type': "application/json"}

    conn.request("POST", "/oauth/token", payload, headers)

    res = conn.getresponse()
    data = res.read()

    return json.loads(data.decode("utf-8"))
