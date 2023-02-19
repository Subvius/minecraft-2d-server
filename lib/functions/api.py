import json

import requests


def get_data(url, json_res=True) -> dict:
    res = requests.get(url)
    if json_res:
        return res.json()
    else:
        return res


def post_data(url, data: dict) -> dict:
    res = requests.post(url, data=json.dumps(data))
    print(res.json())
    return res.json()
