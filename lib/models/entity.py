import pygame


class Entity:
    def __init__(self, size: tuple[int, int], pos: tuple[int, int], hp: int, max_hp: int, damage: int,
                 images_path: str = "",
                 entity_type: str = "Player"):
        self.rect = pygame.Rect(*pos, *size)
        self.hp = hp
        self.max_hp = max_hp
        self.damage = damage
        self.images_path = images_path
        self.type = entity_type
        self.frame = 0
        self.condition = 'idle'
        self.images = dict()
        self.width, self.height = size
        self.dead = False
        self.vertical_momentum = 0
        self.air_timer = 0
        if self.images_path != "":
            self.prepare_images()

    def cut_sheet(self, sheet, columns, rows, animation_type):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.width * i + 29 * i, (self.width - 2) * j)
                image = sheet.subsurface(pygame.Rect(
                    frame_location, (self.width, 70)))
                self.images[animation_type].append(image)

    def prepare_images(self):
        pass

    def move(self, possible_colliders: list[pygame.Rect]):
        pass

    def set_coord(self, x: int, y: int):
        self.rect.x, self.rect.y = x, y

    def get_damage(self, damage: int = 0) -> bool:
        self.hp -= damage
        if self.hp <= 0:
            self.dead = True
            return True
        return False

    def heal(self, hp: int = 1):
        self.hp += hp
        if self.hp > self.max_hp:
            self.hp = self.max_hp

    def draw(self, surface: pygame.Surface, scroll: tuple[int, int]):
        pass
