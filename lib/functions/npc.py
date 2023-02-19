import random

import pygame

from lib.models.npc import Npc
from copy import deepcopy


def move_npc(npcs: list[Npc], colliding_objects, move, player, screen, block_size, possible_x, possible_y, castle_area):
    for npc in npcs:
        if player.dimension == npc.dimension and npc.rect.x // block_size in possible_x and \
                npc.rect.y // block_size in possible_y:
            movement = [0, 0]
            destination = npc.destination
            rect_before = deepcopy(npc.rect)
            if npc.space_filler and destination is None and pygame.time.get_ticks() - npc.arrived_at > 1000 * 10:
                npc.destination = (random.randint(castle_area[0][0], castle_area[1][0]), castle_area[1][1])

            if npc.moving_right or npc.moving_left:
                if npc.condition != 'run':
                    npc.change_condition('run')

            else:
                if npc.condition != 'idle':
                    npc.change_condition()

            if destination is not None:
                if npc.rect.x < destination[0]:
                    movement[0] += 1 * npc.speed
                    npc.moving_direction = 'right'
                    npc.moving_right = False
                    npc.moving_left = True
                elif npc.rect.x > destination[0]:
                    movement[0] -= 1 * npc.speed
                    npc.moving_direction = 'left'
                    npc.moving_right = True
                    npc.moving_left = False
            else:
                npc.moving_left = npc.moving_right = False

            movement[1] += npc.vertical_momentum
            npc.vertical_momentum = npc.vertical_momentum + 0.5 if npc.vertical_momentum + 0.5 <= 3 else 3
            if npc.hide and npc.rect.y < 0:
                npc.vertical_momentum = movement[1] = movement[0] = 0
                npc.rect.y = -300
            npc.rect, collisions = move(npc.rect, movement, colliding_objects)
            if destination is not None:
                if npc.rect.x // 32 == destination[0] // 32 and npc.rect.y // 32 == destination[1] // 32:
                    npc.destination = None
                    npc.arrived_at = pygame.time.get_ticks()

            if not npc.space_filler:
                if rect_before.x // block_size != npc.rect.x // block_size:
                    screen.edit_characters(npc.name, "x", npc.rect.x)
                if rect_before.y // block_size != npc.rect.y // block_size:
                    screen.edit_characters(npc.name, "y", npc.rect.y)

            if not collisions['bottom']:
                npc.air_timer += 1
            else:
                npc.air_timer = 0
                npc.vertical_momentum = 0

            if movement[0] > 0 and collisions['bottom'] and collisions['right'] and npc.vertical_momentum == 0:
                npc.vertical_momentum -= npc.jump_height * 4.5

            elif movement[0] < 0 and collisions['bottom'] and collisions['left'] and npc.vertical_momentum == 0:
                npc.vertical_momentum -= npc.jump_height * 4.5
