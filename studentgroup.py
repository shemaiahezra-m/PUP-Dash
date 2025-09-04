import pygame
import random
from key import Key
from settings import Settings
from music import play_door_closed_sfx

class StudentGroup:
    def __init__(self, spawn_time, group_type, stop_position, group_sprites, load_group_frames, VIRTUAL_WIDTH, group_frame_height, key_image, key_mask, key_width, key_height):
        self.spawn_time = spawn_time
        self.group_type = group_type
        self.right_frames, self.left_frames = load_group_frames(group_sprites[group_type])
        self.state = "waiting"
        self.x = VIRTUAL_WIDTH
        self.y = min(755, VIRTUAL_WIDTH - group_frame_height)
        self.frame = 0
        self.last_update = pygame.time.get_ticks()
        self.direction = "left"
        self.speed = 10
        self.stop_time = None
        self.stop_position = stop_position
        self.key = Key(self.x + 53.65, self.y - 50, key_image, key_mask, key_width, key_height)
        self.target_door = None
        self.target_door_name = None
        self.follow_path = []
        self.follow_path_index = 0
        self.room_stay_time = None
        self.room_stay_duration = None
        self.exit_path = []
        self.exit_path_index = 0
        self.score_added = False  # <-- Add this flag
        self.penalty_applied = False  # Track if penalty was applied for this group
        self.had_key_available = False  # Track if student ever had a clickable key

    def update(self, current_time, front_group=None, door_manager=None):
        if self.state == "waiting" and current_time >= self.spawn_time:
            self.state = "entering"

        # Prevent movement if waiting for check
        if self.state == "waiting_for_check":
            return

        if front_group and front_group.state in ["entering", "stopped", "waiting_for_check"]:
            if front_group.x > front_group.stop_position:
                return
            if self.x - front_group.x < Settings.GROUP_SPACING:
                return

        if self.state == "entering":
            self.x -= self.speed
            if self.x <= self.stop_position and self.state != "stopped":
                self.x = self.stop_position
                self.state = "stopped"
                self.stop_time = current_time
                self.key.set_position(self.x + 53.65, self.y - 50)

        elif self.state == "stopped" and current_time - self.stop_time >= 10000:
            self.state = "exiting"
            self.direction = "right"

        elif self.state == "exiting":
            self.y = 755
            self.direction = "right"
            self.x += self.speed
            if self.x > Settings.VIRTUAL_WIDTH:
                self.state = "done"

        elif self.state == "following":
            self.update_following()
            if self.target_door and abs(self.x - self.target_door[0]) < 5 and abs(self.y - self.target_door[1]) < 5:
                if door_manager and self.target_door_name:
                    door_manager.confirm_lock(self.target_door_name)  # Lock only now!
                self.state = "in_room"
                play_door_closed_sfx()  # Play door closing sound when student enters room
                self.room_stay_time = current_time
                self.room_stay_duration = random.randint(10000, 15000)

        elif self.state == "in_room":
            if current_time - self.room_stay_time >= self.room_stay_duration:
                self.prepare_exit_path()
                self.state = "exiting_room"
                self.exit_path_index = 0

        elif self.state == "exiting_room":
            self.update_exit_path()
            if self.exit_path_index >= len(self.exit_path):
                self.state = "leaving"
                self.direction = "right"

        elif self.state == "leaving":
            self.y = 755
            self.direction = "right"
            self.x += self.speed
            if self.x > Settings.VIRTUAL_WIDTH:
                self.state = "done"

        if self.state in ["entering", "exiting", "following", "exiting_room", "leaving"]:
            if current_time - self.last_update > Settings.GROUP_ANIMATION_COOLDOWN:
                self.frame = (self.frame + 1) % Settings.GROUP_ANIMATION_STEPS
                self.last_update = current_time

        self.key.update(current_time)

    def draw(self, surface):
        # Draw the group if NOT inside the room
        if self.state in ["entering", "stopped", "waiting_for_check", "exiting", "following", "ready_to_follow", "exiting_room", "leaving"]:
            frames = self.right_frames if self.direction == "right" else self.left_frames
            # Normal group drawing - always draw as a horizontal block
            surface.blit(frames[self.frame], (self.x, self.y))
            
            if self.state in ["stopped", "waiting_for_check"]:
                self.key.draw(surface)
            if self.state == "ready_to_follow":
                pygame.draw.circle(surface, (0, 255, 0), (int(self.x + 50), int(self.y - 30)), 10)
        # Do NOT draw anything if self.state == "in_room"

    def is_done(self):
        return self.state == "done"

    def start_following(self, target_door_pos, door_name=None):
        self.state = "following"
        self.target_door = target_door_pos
        self.target_door_name = door_name
        self.follow_path = self.get_path_to_door(target_door_pos, door_name)
        self.follow_path_index = 0

    def update_following(self):
        if not self.follow_path or self.follow_path_index >= len(self.follow_path):
            return
        target = self.follow_path[self.follow_path_index]
        dx = target[0] - self.x
        dy = target[1] - self.y
        distance = (dx**2 + dy**2)**0.5
        follow_speed = self.speed
        
        if distance < follow_speed:
            self.x = target[0]
            self.y = target[1]
            self.follow_path_index += 1
        else:
            if distance > 0:
                self.x += (dx / distance) * follow_speed
                self.y += (dy / distance) * follow_speed
                if dx > 0:
                    self.direction = "right"
                elif dx < 0:
                    self.direction = "left"

    def prepare_exit_path(self):
        if self.target_door_name in ["door1", "door2"]:
            self.exit_path = [
                (self.x, Settings.SECOND_FLOOR_CURVE_STUD_Y),
                (Settings.STAIRS_LEFT_SECOND_FLOOR_X, Settings.SECOND_FLOOR_Y),
                (Settings.STAIRS_LEFT_GROUND_X, Settings.GROUND_Y),
            ]
            self.direction = "left"
        else:
            self.exit_path = [
                (self.x, Settings.SECOND_FLOOR_CURVE_STUD_Y),
                (Settings.STAIRS_RIGHT_SECOND_FLOOR_RSTUD_X, Settings.SECOND_FLOOR_Y),
                (Settings.STAIRS_RIGHT_GROUND_RSTUD_X, Settings.GROUND_Y),
            ]
            self.direction = "right"

    def update_exit_path(self):
        if not self.exit_path or self.exit_path_index >= len(self.exit_path):
            return
        target = self.exit_path[self.exit_path_index]
        dx = target[0] - self.x
        dy = target[1] - self.y
        distance = (dx**2 + dy**2)**0.5
        exit_speed = self.speed
        
        if distance < exit_speed:
            self.x = target[0]
            self.y = target[1]
            self.exit_path_index += 1
            self.y = min(self.y, 755)
            if self.exit_path_index == len(self.exit_path):
                self.y = 755
                self.direction = "right"
        else:
            if distance > 0:
                self.x += (dx / distance) * exit_speed
                self.y += (dy / distance) * exit_speed
                self.y = min(self.y, 755)
                if dx > 0:
                    self.direction = "right"
                elif dx < 0:
                    self.direction = "left"

    def get_path_to_door(self, target_door_pos, door_name):
        path = []
        path.append((self.x, self.y))
        if door_name in ["door1", "door2"]:
            path.append((Settings.STAIRS_LEFT_GROUND_X, Settings.GROUND_Y))
            path.append((Settings.STAIRS_LEFT_SECOND_FLOOR_X, Settings.SECOND_FLOOR_Y))
        else:
            path.append((Settings.STAIRS_RIGHT_GROUND_RSTUD_X, Settings.GROUND_Y))
            path.append((Settings.STAIRS_RIGHT_SECOND_FLOOR_RSTUD_X, Settings.SECOND_FLOOR_Y))
        path.append((target_door_pos[0], Settings.SECOND_FLOOR_CURVE_Y))
        path.append((target_door_pos[0], target_door_pos[1]))
        return path
    
    def check_student_click(self, mouse_pos):
        """Check if the student group itself was clicked (larger clickable area than just the key)"""
        if self.state == "stopped":
            # Large clickable area around the entire student group
            click_radius = 150
            student_center_x = self.x + 75  # Approximate center of student group
            student_center_y = self.y + 38
            
            distance_x = mouse_pos[0] - student_center_x
            distance_y = mouse_pos[1] - student_center_y
            if abs(distance_x) <= click_radius and abs(distance_y) <= click_radius:
                return True
        return False

