import json

import requests


def get_data(url) -> dict:
    res = requests.get(url)

    return res.json()


def post_data(url, data: dict) -> dict:
    res = requests.post(url, data=json.dumps(data))
    print(res.json())
    return res.json()
