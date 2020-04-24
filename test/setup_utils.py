import http.client
import json
import os


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
    conn.close()

    return json.loads(data.decode("utf-8"))


def set_env():
    os.environ["XCUBE_SH_DOCKER_IMG"] = 'quay.io/bcdev/xcube-sh'
    os.environ["SH_CLIENT_ID"] = 'b3da42b1-eef1-4e8d-bf29-dd391ef04518'
    os.environ["SH_CLIENT_SECRET"] = 'ba%k,jsQn:Y<ph:m,j+C/jiG_k$KFlpZ}yAz*E]{'
    os.environ["SH_INSTANCE_ID"] = 'c5828fc7-aa47-4f1d-b684-ae596521ef25'
