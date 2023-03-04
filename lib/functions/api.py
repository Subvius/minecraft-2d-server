import json

import requests


def get_data(url, json_res=True) -> dict | requests.Response:
    res = requests.get(url)
    if json_res:
        return res.json()
    else:
        return res


def post_data(url, data: dict, params=None) -> dict:
    res = requests.post(url, data=json.dumps(data), params=params)
    print(res.json())
    return res.json()
