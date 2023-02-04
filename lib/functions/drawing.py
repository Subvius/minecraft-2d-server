import pygame
from lib.models.screen import Screen
import lib.functions.ptext as ptext


def draw_rect_alpha(surface, color, rect):
    shape_surf = pygame.Surface(pygame.Rect(rect).size, pygame.SRCALPHA)
    pygame.draw.rect(shape_surf, color, shape_surf.get_rect())
    surface.blit(shape_surf, rect)


def draw_black_screen(surface: pygame.Surface):
    pygame.draw.rect(surface, "black", pygame.Rect(0, 0, surface.get_width(), surface.get_height()))


def draw_title(surface: pygame.Surface, text, font: pygame.font.Font, black_screen=False):
    if black_screen:
        draw_black_screen(surface)
    text_surf = font.render(text, False, "white")
    surface.blit(text_surf, (
        surface.get_width() // 2 - text_surf.get_width() // 2, surface.get_height() // 2 - text_surf.get_height() // 2))


def text_placeholders(text: str, player) -> str:
    text = text.replace("<username>", player.nickname)
    return text


def draw_dialog_window(surface: pygame.Surface, screen: Screen, font: pygame.font.Font, player):
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
        ptext.draw("> " + text, (430, 450 + i * (font.get_height() * 2)), surf=surface, color='black',
                   underline=screen.high_lighted_choice is not None and screen.high_lighted_choice == i, fontsize=30,
                   width=800)
        if not has_rects:
            rect = pygame.Rect(*(430, 450 + i * (font.get_height() * 2)), choice_s.get_width(), choice_s.get_height())
            screen.add_dialog_rect(rect)

    ptext.draw(text_placeholders(dialog["text"], player), (430, 275), surf=surface, color='black',
               fontsize=35, width=740)
