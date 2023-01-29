import pygame


class InputBox:

    def __init__(self, x: int, y: int, width, height, font: pygame.font.Font, active_color, inactive_color, hint: bool,
                 tip_font, show_tip,
                 min_length: int = 5,
                 hint_symbol: str = "*", text='', ):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = inactive_color
        self.text = text
        self.font = font
        self.hint = hint
        self.hint_symbol = hint_symbol
        self.txt_surface = self.font.render(text if not self.hint else "*" * len(text), True, self.color)
        self.active = False
        self.active_color = active_color
        self.inactive_color = inactive_color
        self.min_length = min_length
        self.display_tip = show_tip
        self.show_tip = False
        self.tip_pos = (0, 0)
        self.tip_font = tip_font

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION and self.display_tip:
            pos = event.pos
            if self.rect.collidepoint(*pos):
                self.show_tip = True
                self.tip_pos = pos
            else:
                self.show_tip = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            # If the user clicked on the input_box rect.
            if self.rect.collidepoint(event.pos):
                # Toggle the active variable.
                self.active = not self.active
            else:
                self.active = False
            # Change the current color of the input box.
            self.color = self.active_color if self.active else self.inactive_color
        if event.type == pygame.KEYDOWN:
            if self.active:
                if event.key == pygame.K_RETURN:
                    self.active = False
                    self.color = self.active_color if self.active else self.inactive_color
                elif event.key == pygame.K_BACKSPACE:
                    if pygame.key.get_pressed()[pygame.K_LCTRL]:
                        self.text = ''
                    else:
                        self.text = self.text[:-1]
                elif event.key not in [pygame.K_TAB]:
                    self.text += event.unicode
                # Re-render the text.
                self.txt_surface = self.font.render(self.text if not self.hint else "*" * len(self.text), True,
                                                    self.color)

    def update(self):
        # Resize the box if the text is too long.
        width = max(200, self.txt_surface.get_width() + 10)
        self.rect.w = width

    def draw(self, screen):
        # Blit the text.
        screen.blit(self.txt_surface, (self.rect.x + 5, self.rect.y + 5 if not self.hint else self.rect.y + 10))
        # Blit the rect.
        pygame.draw.rect(screen, self.color, self.rect, 2)

        if self.show_tip:
            tip_surf = self.tip_font.render(f"Min length - {self.min_length}", False, "white")
            pygame.draw.rect(screen, (56,56,56),
                             pygame.Rect(self.tip_pos[0] + 5, self.tip_pos[1] - 5, tip_surf.get_width() + 10,
                                         tip_surf.get_height() + 10,), border_radius=5)
            screen.blit(tip_surf, (self.tip_pos[0] + 10, self.tip_pos[1]))
