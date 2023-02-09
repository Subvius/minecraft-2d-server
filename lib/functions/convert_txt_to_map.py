import json


def convert_txt_to_map(txt_file, json_file, map_height):
    with open(txt_file, "r") as txt:
        text = txt.read()
    res = [[] for _ in range(map_height)]
    for line_index, line in enumerate(text.split("\n")):
        for char in line:
            res[line_index].append({
                "block_id": char,
            })

    with open(json_file, "w") as f:
        data = {
            "map": res
        }
        json.dump(data, f)


convert_txt_to_map("../storage/lobby_map.txt", "../storage/lobby_map.json", 24)
