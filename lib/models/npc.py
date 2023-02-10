import json
import os

import natsort as natsort
import pygame.image
from natsort import natsorted

from lib.models.entity import Entity


class Npc(Entity):
    def __init__(self, size: tuple[int, int], pos: tuple[int, int], hp: int, max_hp: int, damage: int, name: str,
                 images_path: str = "", speed=1, jump_height=1.75):
        super().__init__(size, pos, hp, max_hp, damage, images_path, f"npc-{name}", speed=speed,
                         jump_height=jump_height)
        self.name = name
        if images_path == "":
            self.images_path = f"lib/assets/animations/Entities/npc/{name}"
        self.skin_name = name
        self._init_images()
        self.hide = False

    def _init_images(self):
        files = list(filter(lambda x: x.endswith(".png"), os.listdir(self.images_path)))
        sorted_files = natsorted(files)
        for file in sorted_files:
            if file.endswith(".png"):
                animation_type = file.split("-")[0]
                if not list(self.images.keys()).count(animation_type):
                    self.images.update({animation_type: []})

                self.images[animation_type].append(pygame.image.load(f"{self.images_path}/{file}"))
        self.image = self.images['idle'][0]

    def on_click(self, pos: tuple[int, int], button, screen, player, scroll):
        if self.rect.collidepoint(pos[0] + scroll[0], pos[1] + scroll[1]) and self.dimension == screen.screen:
            if button == 3:
                if not screen.show_dialog and self.is_close(pos[0] + scroll[0], pos[1] + scroll[1], player.rect.x,
                                                            player.rect.y, 4):
                    with open("lib/storage/story_characters.json", "r", encoding="utf-8") as f:
                        data: dict = json.load(f)

                    if data[self.name].get("interact", {}).get("can", False):
                        screen.dialog_interlocutor = self.name
                        screen.start_dialog()
                        return True

        return False

    def on_update(self, field: str, value):
        if list(self.__dict__.keys()).count(field):
            exec(f"self.{field}={value}")
        elif list(pygame.Rect.__dict__.keys()).count(field):
            exec(f"self.rect.{field}={value}")
