from lib.models.entity import Entity


class Player(Entity):
    def __init__(self, size: tuple[int, int], pos: tuple[int, int], hp: int, max_hp: int, damage: int, nickname: str,
                 images_path: str = "", ):
        super().__init__(size, pos, hp, max_hp, damage, images_path, "player")
        self.nickname = self.id = nickname

    def server_data(self):
        return Player(self.rect.size, (self.rect.x, self.rect.y), self.hp, self.max_hp, self.damage, self.nickname,
                      self.images_path)
