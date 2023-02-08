import pygame


class Entity:
    def __init__(self, size: tuple[int, int], pos: tuple[int, int], hp: int, max_hp: int, damage: int,
                 images_path: str = "",
                 entity_type: str = "player", dimension='stormhold'):
        self.rect: pygame.Rect = pygame.Rect(*pos, *size)
        self.hp = hp
        self.max_hp = max_hp
        self.damage = damage
        self.image = None
        self.images_path = images_path
        self.type = entity_type
        self.frame = 0
        self.condition = 'idle'
        self.moving_left = self.moving_right = False
        self.moving_direction = "right"
        self.images = dict()
        self.width, self.height = size
        self.dead = False
        self.vertical_momentum = 0
        self.air_timer = 0
        self.dimension = dimension
        if self.images_path != "":
            self.prepare_images()

    def cut_sheet(self, sheet, columns, rows, animation_type, frame_width, step):
        for j in range(rows):
            for i in range(columns):
                frame_location = (frame_width * i + step * i, 0)
                image = sheet.subsurface(pygame.Rect(
                    frame_location, (frame_width, sheet.get_height() // rows)))
                if animation_type not in list(self.images.keys()):
                    self.images.update({animation_type: []})
                self.images[animation_type].append(image)

    def update_frame(self, images=None):
        if images is None:
            images = self.images
        self.frame = (self.frame + 1) % len(images[self.condition])
        self.image = images[self.condition][self.frame]

    def change_condition(self, condition='idle'):
        self.condition = condition
        self.frame = 0

    def set_size(self, w, h):
        self.rect.width, self.rect.height = w, h

    def prepare_images(self):
        pass

    def move(self, possible_colliders: list[pygame.Rect]):
        pass

    def set_dimension(self, dimension):
        self.dimension = dimension

    @staticmethod
    def is_close(x, y, x0, y0, radius) -> bool:
        return ((x - x0) ** 2 + (y - y0) ** 2) <= (radius * 32) ** 2

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

    def draw(self, surface: pygame.Surface, scroll: tuple[int, int], images=None):
        if images is None:
            images = self.images
        try:
            image = images[self.condition][self.frame]
        except KeyError:

            image = pygame.Surface((self.rect.w, self.rect.h))
            pygame.draw.rect(image, "white", self.rect)
        surface.blit(
            pygame.transform.flip(pygame.transform.scale(image, self.rect.size), self.moving_direction == 'left',
                                  False),
            (self.rect.x - scroll[0], self.rect.y - scroll[1]))

    def server_data(self):
        return Entity(self.rect.size, (self.rect.x, self.rect.y), self.hp, self.max_hp, self.damage, self.images_path,
                      self.type)
