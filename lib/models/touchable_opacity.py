import pygame


class TouchableOpacity:
    def __init__(self, surface: pygame.Surface, position, id, scale_on_hover: bool = False, hover_scale: int = 1.025):
        self.surface = surface
        self.scale_on_hover = scale_on_hover
        self.hover_scale = hover_scale
        self.hovered = False
        self.position = position
        self.id = id

    def render(self, screen: pygame.Surface):
        if self.hovered:
            new_width = self.surface.get_width() * self.hover_scale
            new_height = self.surface.get_height() * self.hover_scale
            screen.blit(pygame.transform.scale(self.surface, (new_width, new_height)),
                        (self.position[0] - (new_width - self.surface.get_width()) // 2,
                         self.position[1] - (new_height - self.surface.get_height()) // 2))
        else:
            screen.blit(self.surface, self.position)

    def on_mouse_motion(self, pos):
        if self.scale_on_hover:
            rect = pygame.Rect(*self.position, *self.surface.get_size())
            if rect.collidepoint(*pos):
                self.hovered = True
            else:
                self.hovered = False

    def on_click(self, pos):
        rect = pygame.Rect(*self.position, *self.surface.get_size())
        return rect.collidepoint(*pos)
