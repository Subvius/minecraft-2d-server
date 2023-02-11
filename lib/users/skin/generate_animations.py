import asyncio
import os.path

from minepi import Skin
from PIL import Image


async def generate_animations(sheet_path: str, save_directory: str = './'):
    raw_skin = Image.open(sheet_path)
    s = Skin(raw_skin=raw_skin)

    async def run():
        for i in range(3):
            await s.render_skin(hr=-75, vr=0, vrll=(15 + i * 5), vrra=(15 + i * 5), vrrl=-(15 + i * 5),
                                vrla=-(15 + i * 5),
                                hrh=0)
            s.skin.save(os.path.join(save_directory, f"run-{i}.png"))

        for i in range(3):
            await s.render_skin(hr=-75, vr=0, vrll=(25 - i * 5), vrra=(25 - i * 5), vrrl=-(25 - i * 5),
                                vrla=-(25 - i * 5),
                                hrh=0)
            s.skin.save(os.path.join(save_directory, f"run-{i + 3}.png"))

        for i in range(3):
            await s.render_skin(hr=-75, vr=0, vrll=-(15 + i * 5), vrra=-(15 + i * 5), vrrl=(15 + i * 5),
                                vrla=(15 + i * 5),
                                hrh=0)
            s.skin.save(os.path.join(save_directory, f"run-{i + 6}.png"))

        for i in range(3):
            await s.render_skin(hr=-75, vr=0, vrll=-(25 - i * 5), vrra=-(25 - i * 5), vrrl=(25 - i * 5),
                                vrla=(25 - i * 5),
                                hrh=0)
            s.skin.save(os.path.join(save_directory, f"run-{i + 9}.png"))

    async def sit():
        i = 0
        for a in range(3):
            await s.render_skin(hr=-75, vr=0, vrll=82, vrrl=82, hrh=0, vrra=5,
                                vrla=5)
            s.skin.save(os.path.join(save_directory, f"sit-{i + a}.png"))
        i = 3
        for a in range(3):
            await s.render_skin(hr=-75, vr=0, vrll=82, vrrl=82, hrh=0, vrra=6,
                                vrla=8)
            s.skin.save(os.path.join(save_directory, f"sit-{i + a}.png"))
        i = 6
        for a in range(3):
            await s.render_skin(hr=-75, vr=0, vrll=82, vrrl=82, hrh=0, vrra=8,
                                vrla=6)
            s.skin.save(os.path.join(save_directory, f"sit-{i + a}.png"))

    async def idle():
        i = 0
        for a in range(3):
            await s.render_skin(hr=-75, vr=0, vrll=0, vrrl=0, hrh=0, vrra=5,
                                vrla=5)
            s.skin.save(os.path.join(save_directory, f"idle-{i + a}.png"))
        i = 3
        for a in range(3):
            await s.render_skin(hr=-75, vr=0, vrll=0, vrrl=0, hrh=1, vrra=3,
                                vrla=8)
            s.skin.save(os.path.join(save_directory, f"idle-{i + a}.png"))
        i = 6
        for a in range(3):
            await s.render_skin(hr=-75, vr=0, vrll=0, vrrl=0, hrh=0, vrra=8,
                                vrla=3)
            s.skin.save(os.path.join(save_directory, f"idle-{i + a}.png"))

    async def dialog():
        for i in range(-15, 16, 1):
            await s.render_skin(hr=0, vr=0, hrh=i * 2)
            s.skin.save(os.path.join(save_directory, f"dialog-{15 + i}.png"))
            img = Image.open(os.path.join(save_directory, f"dialog-{15 + i}.png"))
            cropped = img.crop((0, 0, img.width, 158))
            cropped.save(os.path.join(save_directory, f"dialog-{15 + i}.png"))

    # tasks = [
    #     asyncio.create_task(idle()),
    #     asyncio.create_task(sit()),
    #     asyncio.create_task(run()),
    #     asyncio.create_task(dialog())
    # ]
    #
    # await asyncio.gather(*tasks)
    await idle()
    await sit()
    await run()
    await dialog()


#
for file in os.listdir("../../assets/animations/Entities/npc/"):
    if file.endswith(".png"):
        name = file.split(".png")[0]
        os.mkdir(f"../../assets/animations/Entities/npc/{name}/")
        asyncio.run(generate_animations(f"../../assets/animations/Entities/npc/{file}",
                                        f"../../assets/animations/Entities/npc/{name}/"))
