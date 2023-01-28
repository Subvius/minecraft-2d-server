def collision_test(rect, tiles):
    hit_list = []
    for tile_elem in tiles:
        if rect.colliderect(tile_elem):
            hit_list.append(tile_elem)
    return hit_list


def move(rect, movement, tiles):
    collision_types = {'top': False, 'bottom': False, 'right': False, 'left': False}
    rect.x += movement[0]
    hit_list = collision_test(rect, tiles)
    for tile_elem in hit_list:
        if movement[0] > 0:
            rect.right = tile_elem.left
            collision_types['right'] = True
        elif movement[0] < 0:
            rect.left = tile_elem.right
            collision_types['left'] = True
    rect.y += movement[1]
    hit_list = collision_test(rect, tiles)
    for tile_elem in hit_list:
        if movement[1] > 0:
            rect.bottom = tile_elem.top
            collision_types['bottom'] = True
        elif movement[1] < 0:
            rect.top = tile_elem.bottom
            collision_types['top'] = True
    return rect, collision_types
