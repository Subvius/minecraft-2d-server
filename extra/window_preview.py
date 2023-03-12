import os

import pygame
from pygame.locals import *
from lib.functions.drawing import draw_text

pygame.init()
SIZE = WIDTH, HEIGHT = (1360, 768)

screen = pygame.display.set_mode(SIZE)

running = True
images = {}
path = "../lib/assets/icons"
for file in os.listdir(path):
    if file.endswith(".png"):
        images.update({file.split(".")[0]: pygame.image.load(os.path.join(path, file))})

images.update({
    "reputation": pygame.image.load("../lib/assets/windows/reputation.png")
})
images.update({
    "reputation_details": pygame.image.load("../lib/assets/windows/reputation_details.png")
})


def draw(surface: pygame.Surface, reputation: dict):
    mouse_pos = pygame.mouse.get_pos()
    possible_colliders = []

    global images
    sorted_rep = {"magician": 0, "killer": 0, "robber": 0, "smuggler": 0, "spice": 0}
    sorted_rep_translated = [
        "Magicians",
        "Killers",
        "Robbers",
        "Smugglers",
        "Spice merchants",
    ]

    for key in list(sorted_rep.keys()):
        sorted_rep.update({
            key: reputation.get(key, 0)
        })

    center_x, center_y = surface.get_width() // 2, surface.get_height() // 2
    image = images['reputation']

    for index, item in enumerate(list(sorted_rep.items())):

        key, value = item
        top = 187
        left = 192
        line_height = 52
        space = 50

        possible_colliders.append(
            pygame.Rect(
                322, 238 + 78 * index, 717, 38
            )
        )

        y = top + (line_height + space) * index
        x = left
        empty_bar = images.get("empty_bar")
        empty_divider = images.get("empty_divider")

        bar = images.get(f"{key}_bar")
        divider = images.get(f"{key}_divider")

        for i in range(5):
            if (value <= 100 or (value - i * 100) <= 100) and ((value - i * 100) * bar.get_width() // 100) >= 0:
                bar = bar.subsurface((0, 0, (value - i * 100) * bar.get_width() // 100, bar.get_height()))

            if i <= value // 100:
                image.blit(bar, (x + (empty_bar.get_width() + empty_divider.get_width()) * i, y))
            if i != 4 and i + 1 <= value // 100:
                image.blit(divider,
                           (x + (empty_bar.get_width() + empty_divider.get_width()) * i + empty_bar.get_width(), y))

    window = pygame.transform.smoothscale(image, (WIDTH * 0.675, HEIGHT * 0.75))

    surface.blit(window, (center_x - window.get_width() // 2, center_y - window.get_height() // 2))

    img = pygame.image.load("../lib/assets/windows/reputation_details.png")
    for i, line in enumerate(possible_colliders):
        if line.collidepoint(*mouse_pos):
            draw_text(sorted_rep_translated[i], (img.get_width() // 2, 20), img, None, color="#595157",
                      centerx=img.get_width() // 2)

            surface.blit(img, (mouse_pos[0] + 25, mouse_pos[1] - 25))
            break


while running:
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            exit(0)

        if event.type == MOUSEBUTTONDOWN:
            print(event.pos)

    screen.fill("black")

    draw(screen, {"magician": 150, "killer": 175, "smuggler": 110, "robber": 200, "spice": 350})

    pygame.display.flip()
