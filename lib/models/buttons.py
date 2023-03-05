import pygame


class Button:
    def __init__(self, label: str = "Button Label", width: int = 100, height: int = 20, background_color="black",
                 text_color="white", x: int = 0, y: int = 0, hover_color="gray", uniq_id: int = 1,
                 lighting: bool = False, font=None, high_light_color=(10, 10, 225), border_radius=0
                 ):
        self.label = label
        self.width = width
        self.height = height
        self.background_color = background_color
        self.text_color = text_color
        self.rect = pygame.Rect(x, y, self.width, self.height)
        self.is_hovered = False
        self.hover_color = hover_color
        self.id = uniq_id
        self.high_lighted = False
        self.font = font
        self.high_light_color = high_light_color
        self.border_radius = border_radius

    def render(self, surface, font: pygame.font.Font):
        if self.font is not None:
            text_surface = self.font.render(self.label, False, self.text_color)

        else:
            text_surface = font.render(self.label, False, self.text_color)
        pygame.draw.rect(surface, self.background_color if not self.is_hovered else self.hover_color, self.rect,
                         border_radius=self.border_radius)

        if self.high_lighted:
            pygame.draw.rect(surface, self.high_light_color, self.rect, width=2, border_radius=self.border_radius)

        surface.blit(text_surface,
                     (
                         self.rect.midtop[0] - text_surface.get_width() // 2,
                         self.rect.midtop[1] + (self.height - text_surface.get_height()) // 2))

    def on_mouse_motion(self, x, y):
        rect = pygame.Rect(x, y, 1, 1)
        if self.rect.colliderect(rect):
            self.is_hovered = True
        else:
            self.is_hovered = False

    def on_mouse_click(self, x, y) -> bool:
        rect = pygame.Rect(x, y, 1, 1)
        if self.rect.colliderect(rect):
            return True
        return False

    def toggle_high_light(self):
        self.high_lighted = not self.high_lighted
