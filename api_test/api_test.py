import json

import requests

# link = 'http://minecraft2d.pythonanywhere.com/player/?player=Subvius'
#
link = 'http://127.0.0.1:7777/player?player=Subvius'

res = requests.post(url=link, data=json.dumps({"nickname": "Subvius", "id": 1}))

print(res.json())
