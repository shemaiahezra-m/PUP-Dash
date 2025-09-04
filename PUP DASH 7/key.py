import pygame
from music import play_keys_sfx

class Key:
    def __init__(self, x, y, key_image, key_mask, key_width, key_height):
        self.x = x
        self.y = y
        self.visible = True
        self.key_image = key_image
        self.key_mask = key_mask
        self.key_width = key_width
        self.key_height = key_height
        self.clickable = True  # NEW: Only clickable if there are available check icons

    def set_position(self, x, y):
        self.x = x
        self.y = y
        self.visible = True

    def update(self, current_time):
        pass

    def draw(self, surface):
        if self.visible:
            surface.blit(self.key_image, (self.x, self.y))

    def check_click(self, mouse_pos):
        if self.visible and self.clickable:
            # Increased clickable area - 100px radius around the key
            click_radius = 100
            key_center_x = self.x + self.key_width // 2
            key_center_y = self.y + self.key_height // 2
            
            # Check if click is within radius
            distance_x = mouse_pos[0] - key_center_x
            distance_y = mouse_pos[1] - key_center_y
            if abs(distance_x) <= click_radius and abs(distance_y) <= click_radius:
                self.visible = False
                return True
        return False