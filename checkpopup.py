import pygame

class CheckPopup:
    def __init__(self):
        try:
            self.check_image = pygame.image.load("assets/images/check.png").convert_alpha()
        except pygame.error as e:
            print(f"Error loading check image: {e}")
            self.check_image = pygame.Surface((32, 32), pygame.SRCALPHA)
            pygame.draw.circle(self.check_image, (0, 255, 0), (16, 16), 16)
        self.positions = {
            "door1": (207, 470),
            "door2": (370, 470),
            "door3": (1082, 470),
            "door4": (1243, 470)
        }
        self.visible_checks = set()  # doors where check is visible
        self.active = False  # True if checks are currently shown
        self.clicked_door = None  # The door that was clicked

    def show_checks(self, available_doors):
        """Show check icons for available (unlocked) doors."""
        self.visible_checks = set(available_doors)
        self.active = bool(self.visible_checks)
        self.clicked_door = None

    def hide_checks(self):
        self.visible_checks.clear()
        self.active = False
        self.clicked_door = None

    def draw(self, surface):
        for door in self.visible_checks:
            pos = self.positions[door]
            surface.blit(self.check_image, pos)

    def check_click(self, mouse_pos):
        """Returns the door name if a check icon was clicked, else None."""
        if not self.active:
            return None
        for door in self.visible_checks:
            x, y = self.positions[door]
            # Increased clickable area - 120px radius around check icon
            click_radius = 120
            check_center_x = x + self.check_image.get_width() // 2
            check_center_y = y + self.check_image.get_height() // 2
            
            distance_x = mouse_pos[0] - check_center_x
            distance_y = mouse_pos[1] - check_center_y
            if abs(distance_x) <= click_radius and abs(distance_y) <= click_radius:
                self.clicked_door = door
                self.hide_checks()
                return door
        return None