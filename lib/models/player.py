import pygame

from lib.models.entity import Entity


class Player(Entity):
    def __init__(self, size: tuple[int, int], pos: tuple[int, int], hp: int, max_hp: int, damage: int, nickname: str,
                 images_path: str = "", frame=0, condition='idle', moving_direction='right', dimension='lobby'):
        super().__init__(size, pos, hp, max_hp, damage, images_path, "player")
        self.nickname = self.id = nickname
        self.frame = frame
        self.moving_direction = moving_direction
        self.dimension = dimension
        self.condition = condition
        blocks = [["stone", "3"], ["stone_bricks", "98"], ["stone_bricks", "98"], ["stone_bricks", "98"],
                  ["oak_door", "324"], ["cobblestone", "4"], ["grass_block", "1"], ["oak_planks", "5"],
                  ["cracked_stone_bricks", "982"], ]
        self.inventory = [[{
            "type": "block",
            'item_id': "bed" if i + 1 > len(blocks) else blocks[i][0],
            'numerical_id': "365" if i + 1 > len(blocks) else blocks[i][1],
            'quantity': 64
        } for i in range(9)] for __ in range(4)]
        self.selected_inventory_slot = 0

    def server_data(self):
        return Player(self.rect.size, (self.rect.x, self.rect.y), self.hp, self.max_hp, self.damage, self.nickname,
                      self.images_path, self.frame, self.condition, self.moving_direction, self.dimension)

    def set_selected_slot(self, slot: int):
        if not self.is_dead:
            self.selected_inventory_slot = slot
            if not 0 <= self.selected_inventory_slot <= 8:
                self.selected_inventory_slot = 8 if self.selected_inventory_slot < 0 else 0

    def remove_from_inventory(self, slot: int, quantity: int, row: int = 0):
        if not self.is_dead:
            self.inventory[row][slot]["quantity"] -= quantity
            if self.inventory[row][slot]["quantity"] <= 0:
                self.inventory[row][slot] = None

    def draw(self, surface: pygame.Surface, scroll: list[int, int], images=None):
        if images is None:
            images = self.images
        try:
            image = images[self.condition][self.frame]
        except KeyError:

            image = pygame.Surface((self.rect.w, self.rect.h))
            pygame.draw.rect(image, "white", self.rect)
        surface.blit(
            pygame.transform.flip(pygame.transform.scale(image, (
                self.rect.width if self.condition != "idle" else self.rect.width - 5, self.rect.height)),
                                  self.moving_direction != 'left',
                                  False),
            (self.rect.x - scroll[0], self.rect.y - scroll[1]))
