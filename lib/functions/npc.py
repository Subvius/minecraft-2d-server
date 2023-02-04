import pygame

from lib.models.npc import Npc


def move_npc(npcs: list[Npc], colliding_objects, move):
    for npc in npcs:
        movement = [0, 0]
        if npc.moving_right or npc.moving_left:
            if npc.condition != 'walk':
                npc.change_condition('walk')
        else:
            if npc.condition != 'idle':
                npc.change_condition()
        if npc.moving_right:
            movement[0] += 2
            npc.moving_direction = 'right'
        if npc.moving_left:
            movement[0] -= 2
            npc.moving_direction = 'left'

        movement[1] += npc.vertical_momentum
        npc.vertical_momentum = npc.vertical_momentum + 0.5 if npc.vertical_momentum + 0.5 <= 3 else 3

        npc.rect, collisions = move(npc.rect, movement, colliding_objects)

        if not collisions['bottom']:
            npc.air_timer += 1
        else:
            npc.air_timer = 0
