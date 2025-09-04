import pygame

class SpriteSheet():
    def __init__(self, image):
        self.sheet = image

    def get_image(self, frame_index, width, height, scale, colorkey):
     rect = pygame.Rect(frame_index * width, 0, width, height)  # Crop area for frame_index
     image = pygame.Surface(rect.size, pygame.SRCALPHA).convert_alpha()
     image.blit(self.sheet, (0, 0), rect)
     if colorkey is not None:
        image.set_colorkey(colorkey)
     if scale != 1:
        image = pygame.transform.scale(image, (int(width * scale), int(height * scale)))
     return image