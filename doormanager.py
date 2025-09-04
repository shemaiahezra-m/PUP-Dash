import pygame
from music import play_door_closed_sfx, play_door_open_sfx

class DoorManager:
    def __init__(self):
        self.door_click_areas = {
            "door1": pygame.Rect(232, 550, 50, 50),
            "door2": pygame.Rect(395, 550, 50, 50),
            "door3": pygame.Rect(1117, 550, 50, 50),
            "door4": pygame.Rect(1278, 550, 50, 50)
        }
        self.door_target_positions = {
            "door1": (207, 573),
            "door2": (370, 573),
            "door3": (1082, 573),
            "door4": (1243, 573)
        }
        self.left_doors = ["door1", "door2"]
        self.right_doors = ["door3", "door4"]
        self.is_left_door = lambda name: name in self.left_doors
        self.is_right_door = lambda name: name in self.right_doors
        self.locked_doors = set()
        self.pending_lock = set()
        self.door_sprites = self.load_door_sprites()
        self.door_sprite_positions = {
            "door1": (233, 535.5),
            "door2": (395, 535.5),
            "door3": (1108, 535.5),
            "door4": (1269, 535.5)
        }

    def load_door_sprites(self):
        sprites = {}
        try:
            sprites['unlocked'] = pygame.image.load("assets/images/door_unlocked.png").convert_alpha()
            sprites['locked'] = pygame.image.load("assets/images/door_locked.png").convert_alpha()
            door_size = (63, 107)
            sprites['unlocked'] = pygame.transform.scale(sprites['unlocked'], door_size)
            sprites['locked'] = pygame.transform.scale(sprites['locked'], door_size)
        except pygame.error:
            print("Door sprite images not found, using colored rectangles as placeholders")
            door_size = (63, 107)
            sprites['unlocked'] = pygame.Surface(door_size, pygame.SRCALPHA)
            sprites['unlocked'].fill((0, 150, 0))
            sprites['locked'] = pygame.Surface(door_size, pygame.SRCALPHA)
            sprites['locked'].fill((150, 0, 0))
            pygame.draw.rect(sprites['locked'], (255, 255, 0), (20, 25, 10, 15), 2)
            pygame.draw.arc(sprites['locked'], (255, 255, 0), (18, 15, 14, 14), 0, 3.14, 2)
        return sprites

    def lock_door(self, door_name):
        self.pending_lock.add(door_name)
        print(f"{door_name} is now locked! (calling play_door_closed_sfx)")
        play_door_closed_sfx()  # Play SFX when door is locked

    def confirm_lock(self, door_name):
        self.locked_doors.add(door_name)
        self.pending_lock.discard(door_name)
        print(f"{door_name} is now confirmed locked!")

    def unlock_door(self, door_name):
        self.locked_doors.discard(door_name)
        print(f"{door_name} is now unlocked!")
        play_door_open_sfx()  # Play SFX when door is unlocked    

    def unlock_all(self):
        self.locked_doors.clear()
        self.pending_lock.clear()

    def is_door_locked(self, door_name):
        return door_name in self.locked_doors

    def is_door_pending(self, door_name):
        """Return True if the door is pending lock (group is on the way but not yet inside)."""
        return door_name in self.pending_lock

    def check_click(self, mouse_pos):
        for door_name, rect in self.door_click_areas.items():
            # Increase clickable area around doors for easier clicking
            expanded_rect = rect.inflate(150, 150)  # Expand by 150px in all directions
            if expanded_rect.collidepoint(mouse_pos):
                if self.is_door_locked(door_name):
                    print(f"{door_name} is locked! Cannot enter.")
                    return None
                return door_name
        return None

    def draw_door_states(self, surface):
        for door_name in self.door_click_areas:
            sprite = self.door_sprites['locked'] if self.is_door_locked(door_name) else self.door_sprites['unlocked']
            draw_x, draw_y = self.door_sprite_positions.get(door_name, (0, 0))
            surface.blit(sprite, (draw_x, draw_y))