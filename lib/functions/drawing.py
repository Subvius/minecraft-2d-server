import pygame
import lib.functions.ptext as ptext
from lib.models.npc import Npc


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


def draw_dialog_window(surface: pygame.Surface, screen, font: pygame.font.Font, player, _npc: list[Npc]):
    npc = list(filter(lambda x: x.name.lower() == screen.dialog_interlocutor.lower(), _npc))[0]
    window_size = (130, 115)
    window_pos = (965, 148)
    window_surf = pygame.Surface(window_size)
    mx = screen.mouse_pos[0]
    center_x = window_pos[0] + window_size[0] // 2
    if mx < center_x:
        diff = center_x - mx
        diff //= 10

        if diff > 15:
            diff = 15
        image_index = 15 - diff
    elif mx > center_x:
        diff = mx - center_x
        diff //= 10

        if diff > 15:
            diff = 15
        image_index = 15 + diff
    else:
        image_index = 15

    image_before = npc.images["dialog"][image_index]
    window_surf.blit(pygame.transform.scale(image_before, (window_size[0], window_size[1])), (0, 0))

    rect_image = pygame.Surface(window_size, pygame.SRCALPHA)
    pygame.draw.rect(rect_image, (255, 255, 255), (0, 0, *window_size), border_radius=47)

    image: pygame.Surface = window_surf.copy().convert_alpha()
    image.blit(rect_image, (0, 0), None, pygame.BLEND_RGBA_MIN)

    surface.blit(pygame.transform.scale(image, window_size), window_pos)

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


def draw_inventory(surface: pygame.Surface, player, images, blocks_data, screen):
    width, height = surface.get_size()
    selected_slot = player.selected_inventory_slot
    inventory = player.inventory
    color = (0, 10, 0)
    # selected_color = (145, 145, 145)
    selected_color = "white"
    draw_rect_alpha(surface, (0, 0, 0, 127), (width // 2 - 32 * 4.5, height - 32, 32 * 9, 32))
    for i in range(9):
        rect = pygame.Rect(width // 2 - 32 * 4.5 + i * 32, height - 32, 32, 32)
        pygame.draw.rect(surface, selected_color if i == selected_slot else color,
                         rect, width=2)
        if inventory[0][i]:
            block_data = blocks_data[inventory[0][i]['numerical_id']]

            search = block_data["item_id"] if screen.screen == 'lobby' else "abyss-" + block_data[
                "item_id"] if screen.screen == "abyss" else "stone"
            image = images.get(search, images.get(block_data['item_id']))

            surface.blit(pygame.transform.scale(image, (16, 16)), (rect.x + 8, rect.y + 8))
            count = inventory[0][i]['quantity']
            if count > 1:
                draw_text(f"{inventory[0][i]['quantity']}", (rect.x + 18, rect.y + 18), surface, player=player,
                          color="white", shadow=(1.0, 1.0), scolor="#404040", align="right", fontsize=17)

                # text_surface = font.render(f"{inventory[0][i]['quantity']}", False,
                #                            "white")
                #
                # screen.blit(text_surface, (rect.x + 16, rect.y + 16))
