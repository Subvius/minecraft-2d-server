import pygame
import lib.functions.ptext as ptext


def draw_rect_alpha(surface, color, rect):
    shape_surf = pygame.Surface(pygame.Rect(rect).size, pygame.SRCALPHA)
    pygame.draw.rect(shape_surf, color, shape_surf.get_rect())
    surface.blit(shape_surf, rect)


def text_placeholders(text: str, player) -> str:
    text = text.replace("<username>", player.nickname)
    return text


def draw_text(text: str, pos, surf: pygame.Surface, player, **kwargs):
    ptext.DEFAULT_COLOR_TAG = {
        "&0": "black",
        "&1": (0, 0, 170),
        "&2": "#39aa01",
        "&3": (5, 105, 107),
        "&4": "#aa0600",
        "&5": "#aa00aa",
        "&6": "#f9aa01",
        "&7": "#aaaaaa",
        "&8": "#555555",
        "&9": "blue",
        "&a": "green",
        "&b": "aqua",
        "&c": "red",
        "&d": "#FF55FF",
        "&e": "yellow",
        "&f": "white",
    }
    ptext.draw(text_placeholders(text, player), pos, surf=surf, **kwargs)


def draw_dialog_window(surface: pygame.Surface, screen, font: pygame.font.Font, player):
    dialog = screen.current_dialog
    ptext.DEFAULT_COLOR_TAG = {
        "&0": "black",
        "&1": (0, 0, 170),
        "&2": "#39aa01",
        "&3": (5, 105, 107),
        "&4": "#aa0600",
        "&5": "#aa00aa",
        "&6": "#f9aa01",
        "&7": "#aaaaaa",
        "&8": "#555555",
        "&9": "blue",
        "&a": "green",
        "&b": "aqua",
        "&c": "red",
        "&d": "#FF55FF",
        "&e": "yellow",
        "&f": "white",
    }

    has_rects = len(screen.dialog_rects) != 0
    for i, key in enumerate(list(dialog['choices'].keys())):
        choice = dialog['choices'][key]
        text = text_placeholders(choice["answer"], player)
        choice_s = font.render("> " + text, False, "black")
        draw_text("> " + text, (330, 350 + i * (font.get_height() * 1.5)), surf=surface, player=player, color='black',
                  underline=screen.high_lighted_choice is not None and screen.high_lighted_choice == i, fontsize=30,
                  width=600)
        if not has_rects:
            rect = pygame.Rect(*(330, 350 + i * (font.get_height() * 1.5)), choice_s.get_width(), choice_s.get_height())
            screen.add_dialog_rect(rect)

    draw_text(text_placeholders(dialog["text"], player), (330, 200), surf=surface, player=player, color='black',
              fontsize=30, width=495)
