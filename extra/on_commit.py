import json

import lib.functions.api as api
from lib.storage.constants import Constants

consts = Constants()
res = api.post_data(consts.api_url + "game/?update=true", data={"build_number": 1})

with open("../manifest.json", "r", encoding="utf-8") as f:
    manifest: dict = json.load(f)

manifest.update({"build_number": manifest.get("build_number", 0) + 1})

with open("../manifest.json", "w") as f:
    json.dump(manifest, f)
