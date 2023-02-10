import pygame


def cut_sheet(sheet, columns, rows, animation_type, frame_width, step, path):
    images: list[pygame.Surface] = []
    for j in range(rows):
        for i in range(columns):
            frame_location = (frame_width * i + step * i, 0)
            image = sheet.subsurface(pygame.Rect(
                frame_location, (frame_width, sheet.get_height() // rows)))

            images.append(image)

    for i, image in enumerate(images):
        pygame.image.save(image, f"{path}/{animation_type}-{i}.jpg")


cut_sheet(pygame.image.load("../assets/animations/Entities/npc/cebk/punch.jpg"), 6, 1, "punch", 90, 72,
          '../assets/animations/Entities/npc/cebk')
