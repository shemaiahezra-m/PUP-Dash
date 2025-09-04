import pygame

class CautionManager:
    def __init__(self, caution_image_path, size=(40, 40)):
        # Load and scale the caution image
        self.caution_image = pygame.image.load('assets/images/caution.png').convert_alpha()
        self.caution_image = pygame.transform.scale(self.caution_image, size)
        # Set to track which doors should show caution
        self.caution_doors = set()

    def add_caution(self, door_name):
        """Mark a door to show the caution sign."""
        self.caution_doors.add(door_name)

    def remove_caution(self, door_name):
        if door_name in self.caution_doors:
            self.caution_doors.remove(door_name)

    def clear_all(self):
        self.caution_doors.clear()

    def draw(self, surface, door_click_areas, paused=False, cleaning_start_time=None, cleaning_duration=5000):
        """
        Draw the caution sign on all doors that need it.
        If paused, freeze the caution sign's appearance (e.g., could gray out or add overlay if desired).
        :param surface: The surface to draw on.
        :param door_click_areas: Dict of door_name: pygame.Rect
        :param paused: If True, game is paused.
        :param cleaning_start_time: The time cleaning started (for progress bar, optional).
        :param cleaning_duration: Duration of cleaning (ms), default 5000.
        """
        for door_name, rect in door_click_areas.items():
            if door_name in self.caution_doors:
                offset_x = 10  
                offset_y = 45  
                caution_rect = self.caution_image.get_rect(center=(rect.centerx + offset_x, rect.centery + offset_y))
                surface.blit(self.caution_image, caution_rect)
                if paused:
                    # Draw a semi-transparent overlay to indicate frozen state
                    overlay = pygame.Surface(self.caution_image.get_size(), pygame.SRCALPHA)
                    overlay.fill((128, 128, 128, 120))  
                    surface.blit(overlay, caution_rect.topleft)

    def check_click(self, mouse_pos, door_click_areas):
        """Returns the door name if a caution sign was clicked, else None."""
        for door_name in self.caution_doors:
            rect = door_click_areas[door_name]
            offset_x = 10
            offset_y = 45
            caution_center_x = rect.centerx + offset_x
            caution_center_y = rect.centery + offset_y
            
            # Increased clickable area - 120px radius around the caution sign
            click_radius = 120
            distance_x = mouse_pos[0] - caution_center_x
            distance_y = mouse_pos[1] - caution_center_y
            if abs(distance_x) <= click_radius and abs(distance_y) <= click_radius:
                return door_name
        return None