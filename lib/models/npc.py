import json
import os

import pygame.image

from lib.models.entity import Entity
from lib.models.screen import Screen


class Npc(Entity):
    def __init__(self, size: tuple[int, int], pos: tuple[int, int], hp: int, max_hp: int, damage: int, name: str,
                 images_path: str = "", ):
        super().__init__(size, pos, hp, max_hp, damage, images_path, f"npc-{name}")
        self.name = name
        if images_path == "":
            if name == "greeter":
                name = 'mira'
            self.images_path = f"lib/assets/animations/Entities/npc/{name}"
        self.skin_name = name
        self._init_images()

    def _init_images(self):
        for file in sorted(os.listdir(self.images_path)):
            if file.endswith(".png"):
                animation_type = file.split("-")[0]
                if not list(self.images.keys()).count(animation_type):
                    self.images.update({animation_type: []})

                self.images[animation_type].append(pygame.image.load(f"{self.images_path}/{file}"))
        self.image = self.images['idle'][0]

    def on_click(self, pos: tuple[int, int], button, screen: Screen, player, scroll):
        if pos[0] - (self.rect.x - scroll[0]) < self.rect.width and pos[1] - (
                self.rect.y - scroll[1]) < self.rect.height and self.dimension == screen.screen:
            # if self.rect.collidepoint(*pos) and self.dimension == screen.screen:
            if button == 3:
                if not screen.show_dialog and self.is_close(pos[0] + scroll[0], pos[1] + scroll[1], player.rect.x,
                                                            player.rect.y, 4):
                    with open("lib/storage/story_characters.json", "r") as f:
                        data: dict = json.load(f)

                    if data[self.name].get("interact", {}).get("can", False):
                        screen.dialog_interlocutor = self.name
                        screen.start_dialog()
                        return True

        return False
