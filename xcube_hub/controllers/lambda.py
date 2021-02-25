import json
import time
from typing import Dict

import boto3


def test_lambda(body, token_info: Dict):
    payload = bytes(body)
    user_id = token_info['user_id']

    client = boto3.client('lambda')

    for x in range(0, 5):
        response = client.invoke(
            FunctionName="loadSpotsAroundPoint",
            InvocationType='Event',
            Payload=payload
        )
        time.sleep(15)
        print(json.loads(response['Payload'].read()))
        print("\n")
