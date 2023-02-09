import pygame

from lib.models.npc import Npc
from copy import deepcopy


def move_npc(npcs: list[Npc], colliding_objects, move, player, screen, block_size):
    for npc in npcs:
        if player.dimension == npc.dimension:
            movement = [0, 0]
            destination = npc.destination
            rect_before = deepcopy(npc.rect)

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
