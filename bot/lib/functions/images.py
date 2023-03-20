"""
functions for creating player stats images

"""
import datetime
import os.path

from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw
import lib.functions.api as api


def make_image_transparent(img, color):
    datas = img.getdata()

    newData = []
    for item in datas:
        if list(item[0:3]) == list(color):
            newData.append((255, 255, 255, 0))
        else:
            newData.append(item)

    img.putdata(newData)
    return img


def make_image_for_general(nickname: str, data: dict):
    """
    Makes image based on player stats

    :param nickname: IGN
    :param data: Response from API
    :return: Path to new image
    """
    save_path = f'lib/temp/{nickname}-general.png'
    img = Image.open("lib/assets/statsschema.png")
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype("lib/assets/fonts/Panton-BlackCaps.ttf", 18)
    params = {
        "first_login": data.get("first_login"),
        "last_login": data.get("last_login"),
        "last_logout": data.get("last_logout"),
        "reputation": data.get("reputation", {}),
        "play_time": data.get("stats").get("play_time"),
        "completed_tasks": data.get("completed_tasks", 0),
        "total_purchases": data.get("cosmetics", []),
        "nickname": nickname,
    }
    positions = [
        (34, 141),
        (484, 141),
        (34, 207),
        (158, 315),
        (485, 301),
        (521, 509),
        (521, 405),
        (330, 20),
    ]
    for i, param in enumerate(params.items()):
        key, value = param
        coord = positions[i]
        if isinstance(value, dict):
            if key == "reputation":
                sorted_rep = {"magician": 0, "killer": 0, "robber": 0, "smuggler": 0, "spice": 0}
                for key in list(sorted_rep.keys()):
                    sorted_rep.update({
                        key: value.get(key, 0)
                    })
                for v_index, v in enumerate(list(sorted_rep.values())):
                    y = coord[1] + 49 * v_index
                    x = coord[0]
                    draw.text((x, y), f"{v}/500", (255, 255, 255), font=font)
            elif key == 'total_purchases':
                amount = 0
                for el in list(value.values()):
                    amount += len(el)
                draw.text(coord, str(amount), (255, 255, 255), font=font, align="center")
        else:
            if "login" in key:
                text = datetime.datetime.fromtimestamp(value).strftime("%d/%m/%Y, %H:%M")
                draw.text(coord, text, "#dcad38fc", font=font)
            elif "logout" in key:
                text = "online" if value == 0 else "offline"
                draw.text(coord, text, "#d73f3ffc" if text == "offline" else "#00aa00fc", font=font)
            elif key == "play_time":
                text = f"{round(value / 60 / 60)} hours" if value / 60 / 60 > 1 else f"{round(value / 60)} minutes"
                x, y = coord
                if value / 60 / 60 < 1:
                    x -= 10
                draw.text((x, y), text, (255, 255, 255), font=font, align="center")
            else:
                draw.text(coord, str(value), (255, 255, 255), font=font, align="center")

    try:
        if os.path.exists(f"lib/temp/{nickname}-front.png"):
            front_img = Image.open(f"lib/temp/{nickname}-front.png")
        elif data.get('skin_uuid', None) is not None:
            res = api.get_data(f"https://skins.mcstats.com/body/front/{data.get('skin_uuid', None)}",
                               json_res=False)
            with open(f"lib/temp/{nickname}-front.png", "wb") as f:
                f.write(res.content)

            front_img = Image.open(f"lib/temp/{nickname}-front.png")
        else:
            raise ValueError()

    except Exception:
        front_img = Image.open("lib/assets/steve_front.png")
    skin_image = front_img.crop((0, 0, front_img.width, 300)).resize((143, 142))

    text_img = Image.new('RGBA', img.size, (0, 0, 0, 0))
    text_img.paste(img, (0, 0))
    text_img.paste(skin_image, (291, 108), mask=skin_image)

    text_img.save(save_path)

    return save_path


def make_image_for_leaderboard(data: list[dict], leaderboard_type: str, first: int = None, ):
    """
    Makes image based on all player's stats
    :param leaderboard_type: Type of leaderboard
    :param first: First player on a leaderboard. Lists from them to next 10 players if they exist.
    :param data: List of players
    :return: Image path
    """
    if first is None:
        first = 1

    if leaderboard_type == "reputation":
        return rep_leaderboard(data, first)
    elif leaderboard_type == "play_time":
        return playtime_leaderboard(data, first)


def rep_leaderboard(data: list[dict], first: int):
    save_path = f"lib/temp/leaderboard-reputation-{first}.png"
    img = Image.open("lib/assets/reputationschema.png")
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype("lib/assets/fonts/Panton-BlackCaps.ttf", 18)
    colors = (
        "#fddd00",
        "#c7c7c7",
        "#ce8b2b",
        "#ffffff"
    )

    for index, el in enumerate(data[first - 1: first + 9]):
        reputation_obj = el.get("reputation", {})
        reputation = sum([num for num in reputation_obj.values()])
        username = el.get("nickname", "")
        skin_uuid = el.get("skin_uuid")

        position = first + index

        position_color = colors[first - 1 + index] if position <= 3 else colors[-1]
        head_image_path = f"lib/temp/{username}-face.png"
        try:
            if os.path.exists(head_image_path):
                head_image = Image.open(head_image_path)
            elif skin_uuid is not None:
                res = api.get_data(f"https://skins.mcstats.com/face/{skin_uuid}", json_res=False)
                with open(head_image_path, "wb") as f:
                    f.write(res.content)

                head_image = Image.open(head_image_path)
            else:
                raise ValueError()

        except Exception:
            head_image = Image.open("lib/assets/steve_face.png")

        draw.text((60, 142 + 51 * index), f"#{position}", position_color, font=font, align="center")
        draw.text((180, 142 + 51 * index), username, (255, 255, 255), font=font, align="center")
        draw.text((628 - len(str(reputation)) * 3.5 if len(str(reputation)) > 1 else 628, 142 + 51 * index),
                  str(reputation), (255, 255, 255), font=font,
                  align="center")

        img.paste(head_image.resize((26, 26)), (124, 139 + 51 * index), mask=head_image.resize((26, 26)))

    img.save(save_path)
    return save_path


def playtime_leaderboard(data: list[dict], first: int):
    save_path = f"lib/temp/leaderboard-playtime-{first}.png"
    img = Image.open("lib/assets/playtimeschema.png")
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype("lib/assets/fonts/Panton-BlackCaps.ttf", 18)
    colors = (
        "#fddd00",
        "#c7c7c7",
        "#ce8b2b",
        "#ffffff"
    )

    for index, el in enumerate(data[first - 1: first + 9]):
        playtime = el.get("stats").get("play_time", 0)
        if playtime / 60 / 60 < 1:
            playtime = f"{round(playtime / 60, 1)}M"
        else:
            playtime = f"{round(playtime / 60 / 60, 1)}H"
        username = el.get("nickname", "")
        skin_uuid = el.get("skin_uuid")

        position = first + index

        position_color = colors[first - 1 + index] if position <= 3 else colors[-1]
        head_image_path = f"lib/temp/{username}-face.png"
        try:
            if os.path.exists(head_image_path):
                head_image = Image.open(head_image_path)
            elif skin_uuid is not None:
                res = api.get_data(f"https://skins.mcstats.com/face/{skin_uuid}", json_res=False)
                with open(head_image_path, "wb") as f:
                    f.write(res.content)

                head_image = Image.open(head_image_path)
            else:
                raise ValueError()

        except Exception as e:
            print(e.__str__())
            head_image = Image.open("lib/assets/steve_face.png")

        draw.text((60, 142 + 51 * index), f"#{position}", position_color, font=font, align="center")
        draw.text((180, 142 + 51 * index), username, (255, 255, 255), font=font, align="center")
        draw.text((628 - len(str(playtime)) * 3.5 if len(str(playtime)) > 1 else 628, 142 + 51 * index),
                  str(playtime), (255, 255, 255), font=font,
                  align="center")

        img.paste(head_image.resize((26, 26)), (124, 139 + 51 * index), mask=head_image.resize((26, 26)))

    img.save(save_path)
    return save_path
