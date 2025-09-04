import pygame
import sys
import random
import spritesheet
import time

from title_screen import show_title_screen
from welcoming_screen import show_welcoming_screen
from guardlayer import GuardLayer
from doormanager import DoorManager
from studentgroup import StudentGroup
from settings import Settings
from checkpopup import CheckPopup
from caution import CautionManager
from scoreboard import Scoreboard
from timer import GameTimer
from gameover import show_gameover_screen
from pausemenu import PauseMenu
from help_system import HelpSystem
from hourglass_timer import HourglassTimer
from cleaning_progress_bar import CleaningProgressBar
from item_request_manager import ItemRequestManager
from score_manager import ScoreManager
from music import (play_game_music, play_home_music, stop_music,
                   play_button_sfx, play_game_complete_sfx,
                   play_game_over_sfx, play_caution_cleaning_sfx,
                   play_door_closed_sfx, play_door_open_sfx, play_keys_sfx,
                   play_trash_sfx, play_item_dropped_sfx, play_item_picked_sfx,
                   play_life_lose_sfx, pause_all_sfx, unpause_all_sfx)

pygame.init()
play_home_music()

# --- Screen setup ---
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
screen_width, screen_height = screen.get_size()
print("3. Screen setup complete")

while True:
    show_title_screen(screen)
    print("4. Title screen done")
    result = show_welcoming_screen(screen)
    print(f"Welcoming screen returned: {result}")
    if result == "back":
        continue 
    else:
        break    
print("Continuing to main game...")

stop_music()
play_game_music()

# --- Virtual resolution (fixed) ---
VIRTUAL_WIDTH = Settings.VIRTUAL_WIDTH
VIRTUAL_HEIGHT = Settings.VIRTUAL_HEIGHT
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
screen_width, screen_height = screen.get_size()
virtual_surface = pygame.Surface((VIRTUAL_WIDTH, VIRTUAL_HEIGHT))

# --- Load assets ---
background_image = pygame.image.load("assets/images/background.png")
background_image = pygame.transform.scale(background_image, (VIRTUAL_WIDTH, VIRTUAL_HEIGHT))
building_image = pygame.image.load("assets/images/pup-building.png")
building_image = pygame.transform.scale(building_image, (1400, 840))
building_position = (82, 117)

pio_sprite_image = pygame.image.load("assets/images/pio-pi.png").convert_alpha()
pio_sprite_sheet = spritesheet.SpriteSheet(pio_sprite_image)
pio_frame_width = Settings.PIO_FRAME_WIDTH
pio_frame_height = Settings.PIO_FRAME_HEIGHT
pio_scale = Settings.PIO_SCALE
pio_animation_steps = Settings.PIO_ANIMATION_STEPS
pio_animation_cooldown = Settings.PIO_ANIMATION_COOLDOWN
pio_right_frames = []
pio_left_frames = []
for i in range(pio_animation_steps):
    image = pio_sprite_sheet.get_image(i, pio_frame_width, pio_frame_height, pio_scale, None)
    pio_right_frames.append(image)
    pio_left_frames.append(pygame.transform.flip(image, True, False))
pio_x = VIRTUAL_WIDTH - pio_frame_width * pio_scale - 50
pio_y = Settings.GROUND_Y
pio_speed = Settings.PIO_SPEED
pio_facing_right = False
pio_frame = 0
pio_last_update = pygame.time.get_ticks()
pio_target_x, pio_target_y = pio_x, pio_y
pio_path = []
PIO_STATE_IDLE = 0
PIO_STATE_MOVING_TO_POINT = 1
PIO_STATE_FOLLOWING_PATH = 2
pio_state = PIO_STATE_IDLE
pio_target_storage = None  

group_frame_width = Settings.GROUP_FRAME_WIDTH
group_frame_height = Settings.GROUP_FRAME_HEIGHT
group_scale = Settings.GROUP_SCALE
group_animation_cooldown = Settings.GROUP_ANIMATION_COOLDOWN
group_animation_steps = Settings.GROUP_ANIMATION_STEPS
group_sprites = {
    "normal": pygame.image.load("assets/images/normal_stud.png").convert_alpha(),
    "ie": pygame.image.load("assets/images/ie_stud.png").convert_alpha(),
    "comsoc": pygame.image.load("assets/images/comsoc_stud.png").convert_alpha(),
    "psych": pygame.image.load("assets/images/psych_stud.png").convert_alpha(),
    "ptso": pygame.image.load("assets/images/ptso_stud.png").convert_alpha(),
}
def load_group_frames(sprite_image):
    sheet = spritesheet.SpriteSheet(sprite_image)
    right_frames, left_frames = [], []
    for i in range(group_animation_steps):
        frame = sheet.get_image(i, group_frame_width, group_frame_height, group_scale, None)
        right_frames.append(frame)
        left_frames.append(pygame.transform.flip(frame, True, False))
    return right_frames, left_frames

key_image = pygame.image.load("assets/images/key.png").convert_alpha()
key_mask = pygame.mask.from_surface(key_image)
key_width, key_height = key_image.get_width(), key_image.get_height()

room_image = pygame.image.load("assets/images/keyroom.png").convert_alpha()
room_image = pygame.transform.scale(room_image, (1300, 740))
room_position = (88, 202)
border_image = pygame.image.load("assets/images/keyborder.png").convert_alpha()
border_image = pygame.transform.scale(border_image, (1300, 740))
border_position = (88, 202)

guard_image = pygame.image.load("assets/images/guard.png").convert_alpha()
guard_sheet = spritesheet.SpriteSheet(guard_image)
guard_frame_width, guard_frame_height = 50, 97
guard_animation_steps = 2
guard_scale = 1
guard_animation_cooldown = 300
sheet = GuardLayer(292, 717, guard_sheet, guard_frame_width, guard_frame_height, guard_scale, guard_animation_steps, guard_animation_cooldown)

check_popup = CheckPopup()
door_manager = DoorManager()
caution_manager = CautionManager('assets/images/caution.png')

clock = pygame.time.Clock()
FPS = 60
running = True

groups = []
first_group_time = pygame.time.get_ticks() + 4000
next_group_time = first_group_time
BASE_SPAWN_INTERVAL = 8000  # Start with 8 seconds between spawns
MIN_SPAWN_INTERVAL = 2500   # Minimum 2.5 seconds between spawns
GROUP_SPACING = Settings.GROUP_SPACING
game_start_time = pygame.time.get_ticks()
next_group_time = pygame.time.get_ticks() + 4000
group_types = list(group_sprites.keys())

def calculate_spawn_interval(game_time_elapsed):
    """
    Calculate spawn interval based on game progression.
    Starts slow and gradually increases difficulty over time.
    """
    # Convert to seconds for easier calculation
    time_elapsed_seconds = game_time_elapsed / 1000.0
    progress = min(time_elapsed_seconds / 120.0, 1.0)  # Cap at 100% after 2 minutes
    
    # Linear interpolation from BASE to MIN
    interval = BASE_SPAWN_INTERVAL - (BASE_SPAWN_INTERVAL - MIN_SPAWN_INTERVAL) * progress
    
    return int(interval)

# --- Game Timer ---

TIMER_DURATION_MS = 2 * 60 * 1000  # 2 minutes

timer = GameTimer(
    duration_ms=TIMER_DURATION_MS,
    font_path="assets/Space_Mono/SpaceMono-Bold.ttf",
    font_size=32,
    timer_bg_path="assets/images/timer-bg.png",
    pos=(40, 30)
)

# --- Lives System ---
lives_image = pygame.image.load("assets/images/lives.png").convert_alpha()

# Define desired height for the stars display
desired_height = 32  # Height for the stars/lives display

original_width = lives_image.get_width()
original_height = lives_image.get_height()
scale_factor = desired_height / original_height
new_width = int(original_width * scale_factor)
lives_image = pygame.transform.scale(lives_image, (new_width, desired_height))


if original_width > original_height:
    estimated_frame_width = original_height  # Assume frames are roughly square
    star_frames = max(1, original_width // estimated_frame_width)
else:
    # Vertical or single frame
    star_frames = 1

star_width = new_width // star_frames
star_height = desired_height

print(f"Detected {star_frames} frames in star sprite sheet, each {star_width}x{star_height} pixels")

max_lives = 10
current_lives = max_lives
lives_start_x = 50
lives_y = 120

# --- Define common pathing coordinates ---
GROUND_Y = Settings.GROUND_Y
SECOND_FLOOR_Y = Settings.SECOND_FLOOR_Y
SECOND_FLOOR_CURVE_Y = Settings.SECOND_FLOOR_CURVE_Y
STAIRS_LEFT_GROUND_X = Settings.STAIRS_LEFT_GROUND_X
STAIRS_LEFT_SECOND_FLOOR_X = Settings.STAIRS_LEFT_SECOND_FLOOR_X
STAIRS_RIGHT_GROUND_X = Settings.STAIRS_RIGHT_GROUND_X
STAIRS_RIGHT_SECOND_FLOOR_X = Settings.STAIRS_RIGHT_SECOND_FLOOR_X
STAIRS_HORIZONTAL_MID_X = Settings.STAIRS_HORIZONTAL_MID_X
PATH_2F_LEFT_CURVE_X = Settings.PATH_2F_LEFT_CURVE_X
PATH_2F_MIDDLE_X = Settings.PATH_2F_MIDDLE_X
PATH_2F_RIGHT_CURVE_X = Settings.PATH_2F_RIGHT_CURVE_X

group_waiting_for_check = None

# --- Caution logic state ---
doors_with_caution = set()
pio_cleaning = False
pio_cleaning_start_time = 0
pio_cleaning_door = None

# --- Pause menu setup ---
virtual_surface = pygame.Surface((VIRTUAL_WIDTH, VIRTUAL_HEIGHT))
pause_menu = PauseMenu(VIRTUAL_WIDTH, VIRTUAL_HEIGHT)

# --- Help system setup ---
help_system = HelpSystem(VIRTUAL_WIDTH, VIRTUAL_HEIGHT)

# --- Hourglass timer setup (for students in rooms) ---
hourglass_timer = HourglassTimer()

# --- Cleaning progress bar setup (for Pio's cleaning) ---
cleaning_progress_bar = CleaningProgressBar()

# --- Item request system setup ---
item_request_manager = ItemRequestManager()

# --- Pio's carrying state ---
pio_carrying_item = None 
pio_carrying_for_group = None

# --- Scoreboard setup ---
class DummyStats:
    def __init__(self):
        self.score = 0
stats = DummyStats()
scoreboard = Scoreboard(type('Game', (), {
    'screen': virtual_surface,
    'settings': Settings,
    'stats': stats
})())

# --- Score Manager setup ---
score_manager = ScoreManager(scoreboard)

def is_any_key_frozen():
    for group in groups:
        if hasattr(group, "state") and group.state == "stopped" and group.key.visible and not group.key.clickable:
            return True
    return False

# --- Track which groups have already triggered points ---
groups_with_points = set()

# --- High score tracking ---
high_score = 0

# --- Pause system variables ---
game_paused = False
pause_start_time = 0
total_pause_duration = 0

# --- Timer pause support ---
while running:
    dt = clock.tick(FPS)
    real_time = pygame.time.get_ticks()
    
    # Calculate game time (real time minus total pause duration)
    if game_paused:
        # While paused, don't update current_time
        current_time = real_time - total_pause_duration - (real_time - pause_start_time)
    else:
        current_time = real_time - total_pause_duration

    for event in pygame.event.get():
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = pygame.mouse.get_pos()
            scale_x = VIRTUAL_WIDTH / screen_width
            scale_y = VIRTUAL_HEIGHT / screen_height
            mouse_x = int(mx * scale_x)
            mouse_y = int(my * scale_y)

            # --- Cancel cleaning only for specific interrupting actions (not student management) ---
            clicked_caution = caution_manager.check_click((mouse_x, mouse_y), door_manager.door_click_areas)
            
            # Only cancel cleaning if:
            # 1. Clicking a different caution sign
            # 2. Clicking ground for movement (handled later in ground movement section)
            # 3. Clicking storage rooms or trash bin (item management)
            # DO NOT cancel for: keys, check popup, doors for student assignment
            should_cancel_cleaning = False
            
            if pio_cleaning and clicked_caution and pio_cleaning_door != clicked_caution:
                # Clicked a different caution sign - cancel current cleaning
                should_cancel_cleaning = True
            elif pio_cleaning and not clicked_caution:
                # Check if it's an item management click (storage/trash)
                if not pio_carrying_item:
                    clicked_storage = item_request_manager.check_storage_room_click((mouse_x, mouse_y))
                    if clicked_storage:
                        should_cancel_cleaning = True
                elif pio_carrying_item:
                    if item_request_manager.check_trash_bin_click((mouse_x, mouse_y)):
                        should_cancel_cleaning = True
            
            if should_cancel_cleaning:
                cleaning_progress_bar.stop_cleaning()
                pio_cleaning = False
                pio_cleaning_start_time = 0

            # --- 1. CHECK HELP BUTTON CLICK FIRST ---
            if help_system.check_help_button_click((mouse_x, mouse_y)):
                # Help button clicked - tutorial will show and game will freeze
                continue

            # --- 2. CHECK IF TUTORIAL IS SHOWING (handle tutorial clicks) ---
            if help_system.is_tutorial_showing():
                if help_system.check_tutorial_click((mouse_x, mouse_y)):
                    # Tutorial was clicked - close it
                    help_system.hide_tutorial()
                continue  # Block all other interactions while tutorial is showing

            # --- 3. CHECK SETTINGS BUTTON CLICK ---
            if hasattr(pause_menu, "check_settings_click"):
                if pause_menu.check_settings_click((mouse_x, mouse_y)):
                    if not game_paused:  # Only pause if not already paused
                        game_paused = True
                        pause_start_time = real_time
                        
                        if hasattr(pause_menu, "set_paused"):
                            pause_menu.set_paused(True)
                        elif hasattr(pause_menu, "is_paused"):
                            pause_menu.active = True
                        # --- PAUSE TIMER ---
                        if hasattr(timer, "pause"):
                            timer.pause()
                        # --- PAUSE MUSIC AND SFX ---
                        from music import pause_music
                        pause_music()
                        pause_all_sfx()  # Pause all sound effects including cleaning SFX
                    continue

            # --- 4. IF PAUSED, HANDLE PAUSE MENU BUTTONS ---
            if game_paused:
                if hasattr(pause_menu, "check_pause_menu_click"):
                    result = pause_menu.check_pause_menu_click((mouse_x, mouse_y))
                    if result == "resume":
                        if game_paused:  # Only resume if currently paused
                            # Calculate total pause duration
                            total_pause_duration += real_time - pause_start_time
                            game_paused = False
                            
                            if hasattr(pause_menu, "set_paused"):
                                pause_menu.set_paused(False)
                            elif hasattr(pause_menu, "is_paused"):
                                pause_menu.active = False
                            # --- RESUME TIMER ---
                            if hasattr(timer, "resume"):
                                timer.resume()
                            # --- UNPAUSE MUSIC AND SFX ---
                            from music import unpause_music
                            unpause_music()
                            unpause_all_sfx()  # Unpause all sound effects
                        continue
                    elif result == "go_to_title_screen" or result == "quit":
                        # Clean up pause state
                        if game_paused:
                            total_pause_duration += real_time - pause_start_time
                            game_paused = False
                        if hasattr(pause_menu, "set_paused"):
                            pause_menu.set_paused(False)
                        elif hasattr(pause_menu, "is_paused"):
                            pause_menu.active = False
                        play_home_music()
                        # Show welcoming screen and wait for 'start'
                        while True:
                            result = show_welcoming_screen(screen)
                            if result == "start":
                                break
                        # Reset ALL game state variables here (score, groups, lives, etc.)
                        stats.score = 0
                        scoreboard.prep_score()  # Reset the scoreboard display
                        groups.clear()
                        score_manager = ScoreManager(scoreboard)
                        current_lives = max_lives
                        pio_x = VIRTUAL_WIDTH - pio_frame_width * pio_scale - 50
                        pio_y = Settings.GROUND_Y
                        pio_facing_right = False
                        pio_frame = 0
                        pio_last_update = pygame.time.get_ticks()
                        pio_target_x, pio_target_y = pio_x, pio_y
                        pio_path = []
                        pio_state = PIO_STATE_IDLE
                        pio_target_storage = None
                        pio_carrying_item = None
                        pio_carrying_for_group = None
                        item_request_manager = ItemRequestManager()
                        pio_cleaning = False
                        pio_cleaning_start_time = 0
                        pio_cleaning_door = None
                        doors_with_caution.clear()
                        group_waiting_for_check = None
                        groups_with_points.clear()
                        current_time = pygame.time.get_ticks()
                        game_start_time = current_time
                        first_group_time = current_time + 4000
                        next_group_time = first_group_time
                        game_paused = False
                        pause_start_time = 0
                        total_pause_duration = 0
                        timer = GameTimer(
                            duration_ms=TIMER_DURATION_MS,
                            font_path="assets/Space_Mono/SpaceMono-Bold.ttf",
                            font_size=32,
                            timer_bg_path="assets/images/timer-bg.png",
                            pos=(40, 30)
                        )
                        hourglass_timer = HourglassTimer()
                        cleaning_progress_bar = CleaningProgressBar()
                        door_manager = DoorManager()
                        caution_manager = CautionManager('assets/images/caution.png')
                        check_popup = CheckPopup()
                        game_paused = False
                        if hasattr(pause_menu, "set_paused"):
                            pause_menu.set_paused(False)
                        elif hasattr(pause_menu, "is_paused"):
                            pause_menu.active = False
                        stop_music()
                        play_game_music()
                        continue
                    elif result == "back":
                        continue
                    else:
                        break
            action_taken = False

            # 0. Check if a storage room was clicked (to pick up items)
            if not pio_carrying_item:
                clicked_storage = item_request_manager.check_storage_room_click((mouse_x, mouse_y))
                if clicked_storage:
                    # Get the storage room position (on ground floor)
                    storage_data = item_request_manager.storage_rooms[clicked_storage]
                    storage_pos = storage_data["position"]
                    
                    # Send Pio to the storage room position on ground floor
                    pio_path = []
                    pio_path.append((pio_x, pio_y))
                    
                    # If Pio is on second floor, go down to ground floor first
                    tolerance = pio_speed
                    is_on_second_floor_path = (pio_y <= SECOND_FLOOR_CURVE_Y + tolerance and pio_y >= SECOND_FLOOR_Y - tolerance)
                    current_side_is_left = pio_x < STAIRS_HORIZONTAL_MID_X
                    
                    if is_on_second_floor_path:
                        # Go down to ground floor
                        if current_side_is_left:
                            pio_path.append((STAIRS_LEFT_SECOND_FLOOR_X, SECOND_FLOOR_Y))
                            pio_path.append((STAIRS_LEFT_GROUND_X, GROUND_Y))
                        else:
                            pio_path.append((STAIRS_RIGHT_SECOND_FLOOR_X, SECOND_FLOOR_Y))
                            pio_path.append((STAIRS_RIGHT_GROUND_X, GROUND_Y))
                    
                    # Go directly to storage room position on ground floor
                    pio_path.append((storage_pos[0], GROUND_Y))
                    
                    pio_state = PIO_STATE_FOLLOWING_PATH
                    if pio_path:
                        pio_target_x, pio_target_y = pio_path.pop(0)
                    
                    # Mark which room Pio is going to
                    pio_target_storage = clicked_storage
                    action_taken = True

            # 0.1. Check if trash bin was clicked (to dispose of items)
            if pio_carrying_item and not action_taken:
                if item_request_manager.check_trash_bin_click((mouse_x, mouse_y)):
                    # Send Pio to the trash bin
                    trash_pos = item_request_manager.trash_bin_position
                    
                    pio_path = []
                    pio_path.append((pio_x, pio_y))
                    
                    # If Pio is on second floor, go down to ground floor first
                    tolerance = pio_speed
                    is_on_second_floor_path = (pio_y <= SECOND_FLOOR_CURVE_Y + tolerance and pio_y >= SECOND_FLOOR_Y - tolerance)
                    current_side_is_left = pio_x < STAIRS_HORIZONTAL_MID_X
                    
                    if is_on_second_floor_path:
                        # Go down to ground floor
                        if current_side_is_left:
                            pio_path.append((STAIRS_LEFT_SECOND_FLOOR_X, SECOND_FLOOR_Y))
                            pio_path.append((STAIRS_LEFT_GROUND_X, GROUND_Y))
                        else:
                            pio_path.append((STAIRS_RIGHT_SECOND_FLOOR_X, SECOND_FLOOR_Y))
                            pio_path.append((STAIRS_RIGHT_GROUND_X, GROUND_Y))
                    
                    # Go directly to trash bin position on ground floor
                    pio_path.append((trash_pos[0], GROUND_Y))
                    
                    pio_state = PIO_STATE_FOLLOWING_PATH
                    if pio_path:
                        pio_target_x, pio_target_y = pio_path.pop(0)
                    
                    # Mark that Pio is going to trash
                    pio_target_storage = "trash_bin"
                    action_taken = True

            # 0.5. Check if a student group was clicked for item delivery
            if pio_carrying_item and not action_taken:
                # First check if an item request bubble was clicked directly
                clicked_group_id = item_request_manager.check_request_click((mouse_x, mouse_y), pio_carrying_item)
                if clicked_group_id:
                    # Find the group with this ID
                    target_group = None
                    for group in groups:
                        if id(group) == clicked_group_id:
                            target_group = group
                            break
                    
                    if target_group and hasattr(target_group, 'target_door_name'):
                        # Send Pio to deliver the item
                        pio_path = []
                        pio_path.append((pio_x, pio_y))
                        
                        # Navigate to the door
                        door_pos = door_manager.door_target_positions[target_group.target_door_name]
                        final_door_target_x, final_door_target_y = door_pos
                        target_door_is_left = door_manager.is_left_door(target_group.target_door_name)
                        tolerance = pio_speed
                        is_on_ground_floor = (pio_y >= GROUND_Y - tolerance)
                        is_on_second_floor_path = (pio_y <= SECOND_FLOOR_CURVE_Y + tolerance and pio_y >= SECOND_FLOOR_Y - tolerance)
                        current_side_is_left = pio_x < STAIRS_HORIZONTAL_MID_X

                        if is_on_ground_floor:
                            if target_door_is_left:
                                pio_path.append((STAIRS_LEFT_GROUND_X, GROUND_Y))
                                pio_path.append((STAIRS_LEFT_SECOND_FLOOR_X, SECOND_FLOOR_Y))
                            else:
                                pio_path.append((STAIRS_RIGHT_GROUND_X, GROUND_Y))
                                pio_path.append((STAIRS_RIGHT_SECOND_FLOOR_X, SECOND_FLOOR_Y))
                            pio_path.append((final_door_target_x, SECOND_FLOOR_CURVE_Y))
                            pio_path.append((final_door_target_x, final_door_target_y))
                        elif is_on_second_floor_path:
                            if target_door_is_left == current_side_is_left:
                                pio_path.append((pio_x, SECOND_FLOOR_CURVE_Y))
                                pio_path.append((final_door_target_x, SECOND_FLOOR_CURVE_Y))
                                pio_path.append((final_door_target_x, final_door_target_y))
                            else:
                                if current_side_is_left:
                                    pio_path.append((STAIRS_LEFT_SECOND_FLOOR_X, SECOND_FLOOR_Y))
                                    pio_path.append((STAIRS_LEFT_GROUND_X, GROUND_Y))
                                else:
                                    pio_path.append((STAIRS_RIGHT_SECOND_FLOOR_X, SECOND_FLOOR_Y))
                                    pio_path.append((STAIRS_RIGHT_GROUND_X, GROUND_Y))
                                if target_door_is_left:
                                    pio_path.append((STAIRS_LEFT_GROUND_X, GROUND_Y))
                                else:
                                    pio_path.append((STAIRS_RIGHT_GROUND_X, GROUND_Y))
                                if target_door_is_left:
                                    pio_path.append((STAIRS_LEFT_SECOND_FLOOR_X, SECOND_FLOOR_Y))
                                else:
                                    pio_path.append((STAIRS_RIGHT_SECOND_FLOOR_X, SECOND_FLOOR_Y))
                                pio_path.append((final_door_target_x, SECOND_FLOOR_CURVE_Y))
                                pio_path.append((final_door_target_x, final_door_target_y))

                        pio_state = PIO_STATE_FOLLOWING_PATH
                        if pio_path:
                            pio_target_x, pio_target_y = pio_path.pop(0)
                        
                        # Mark which group Pio is delivering to
                        pio_carrying_for_group = target_group
                        action_taken = True
                
                # If no bubble was clicked, try clicking the door itself (fallback)
                if not action_taken:
                    for group in groups:
                        if (hasattr(group, 'item_request') and group.item_request == pio_carrying_item and
                            hasattr(group, 'state') and group.state == "in_room"):
                            # Check if the door itself was clicked (use door manager's click detection)
                            if hasattr(group, 'target_door_name'):
                                clicked_door = door_manager.check_click((mouse_x, mouse_y))
                                if clicked_door == group.target_door_name:
                                    # Send Pio to deliver the item
                                    pio_path = []
                                    pio_path.append((pio_x, pio_y))
                                    
                                    # Navigate to the door
                                    door_pos = door_manager.door_target_positions[group.target_door_name]
                                    final_door_target_x, final_door_target_y = door_pos
                                    target_door_is_left = door_manager.is_left_door(group.target_door_name)
                                    tolerance = pio_speed
                                    is_on_ground_floor = (pio_y >= GROUND_Y - tolerance)
                                    is_on_second_floor_path = (pio_y <= SECOND_FLOOR_CURVE_Y + tolerance and pio_y >= SECOND_FLOOR_Y - tolerance)
                                    current_side_is_left = pio_x < STAIRS_HORIZONTAL_MID_X

                                    if is_on_ground_floor:
                                        if target_door_is_left:
                                            pio_path.append((STAIRS_LEFT_GROUND_X, GROUND_Y))
                                            pio_path.append((STAIRS_LEFT_SECOND_FLOOR_X, SECOND_FLOOR_Y))
                                        else:
                                            pio_path.append((STAIRS_RIGHT_GROUND_X, GROUND_Y))
                                            pio_path.append((STAIRS_RIGHT_SECOND_FLOOR_X, SECOND_FLOOR_Y))
                                        pio_path.append((final_door_target_x, SECOND_FLOOR_CURVE_Y))
                                        pio_path.append((final_door_target_x, final_door_target_y))
                                    elif is_on_second_floor_path:
                                        if target_door_is_left == current_side_is_left:
                                            pio_path.append((pio_x, SECOND_FLOOR_CURVE_Y))
                                            pio_path.append((final_door_target_x, SECOND_FLOOR_CURVE_Y))
                                            pio_path.append((final_door_target_x, final_door_target_y))
                                        else:
                                            if current_side_is_left:
                                                pio_path.append((STAIRS_LEFT_SECOND_FLOOR_X, SECOND_FLOOR_Y))
                                                pio_path.append((STAIRS_LEFT_GROUND_X, GROUND_Y))
                                            else:
                                                pio_path.append((STAIRS_RIGHT_SECOND_FLOOR_X, SECOND_FLOOR_Y))
                                                pio_path.append((STAIRS_RIGHT_GROUND_X, GROUND_Y))
                                            if target_door_is_left:
                                                pio_path.append((STAIRS_LEFT_GROUND_X, GROUND_Y))
                                            else:
                                                pio_path.append((STAIRS_RIGHT_GROUND_X, GROUND_Y))
                                            if target_door_is_left:
                                                pio_path.append((STAIRS_LEFT_SECOND_FLOOR_X, SECOND_FLOOR_Y))
                                            else:
                                                pio_path.append((STAIRS_RIGHT_SECOND_FLOOR_X, SECOND_FLOOR_Y))
                                            pio_path.append((final_door_target_x, SECOND_FLOOR_CURVE_Y))
                                            pio_path.append((final_door_target_x, final_door_target_y))

                                    pio_state = PIO_STATE_FOLLOWING_PATH
                                    if pio_path:
                                        pio_target_x, pio_target_y = pio_path.pop(0)
                                    
                                    # Mark which group Pio is delivering to
                                    pio_carrying_for_group = group
                                    action_taken = True
                                    break

            # 1. Check if a caution sign was clicked (BLOCKED while cleaning that door)
            caution_door = caution_manager.check_click((mouse_x, mouse_y), door_manager.door_click_areas)
            if caution_door and not (pio_cleaning and pio_cleaning_door == caution_door):
                pio_path = []
                pio_path.append((pio_x, pio_y))
                final_door_target_x, final_door_target_y = door_manager.door_target_positions[caution_door]
                target_door_is_left = door_manager.is_left_door(caution_door)
                tolerance = pio_speed
                is_on_ground_floor = (pio_y >= GROUND_Y - tolerance)
                is_on_second_floor_path = (pio_y <= SECOND_FLOOR_CURVE_Y + tolerance and pio_y >= SECOND_FLOOR_Y - tolerance)
                current_side_is_left = pio_x < STAIRS_HORIZONTAL_MID_X

                if is_on_ground_floor:
                    if target_door_is_left:
                        pio_path.append((STAIRS_LEFT_GROUND_X, GROUND_Y))
                        pio_path.append((STAIRS_LEFT_SECOND_FLOOR_X, SECOND_FLOOR_Y))
                    else:
                        pio_path.append((STAIRS_RIGHT_GROUND_X, GROUND_Y))
                        pio_path.append((STAIRS_RIGHT_SECOND_FLOOR_X, SECOND_FLOOR_Y))
                    pio_path.append((final_door_target_x, SECOND_FLOOR_CURVE_Y))
                    pio_path.append((final_door_target_x, final_door_target_y))
                elif is_on_second_floor_path:
                    if target_door_is_left == current_side_is_left:
                        pio_path.append((pio_x, SECOND_FLOOR_CURVE_Y))
                        pio_path.append((final_door_target_x, SECOND_FLOOR_CURVE_Y))
                        pio_path.append((final_door_target_x, final_door_target_y))
                    else:
                        if current_side_is_left:
                            pio_path.append((STAIRS_LEFT_SECOND_FLOOR_X, SECOND_FLOOR_Y))
                            pio_path.append((STAIRS_LEFT_GROUND_X, GROUND_Y))
                        else:
                            pio_path.append((STAIRS_RIGHT_SECOND_FLOOR_X, SECOND_FLOOR_Y))
                            pio_path.append((STAIRS_RIGHT_GROUND_X, GROUND_Y))
                        if target_door_is_left:
                            pio_path.append((STAIRS_LEFT_GROUND_X, GROUND_Y))
                        else:
                            pio_path.append((STAIRS_RIGHT_GROUND_X, GROUND_Y))
                        if target_door_is_left:
                            pio_path.append((STAIRS_LEFT_SECOND_FLOOR_X, SECOND_FLOOR_Y))
                        else:
                            pio_path.append((STAIRS_RIGHT_SECOND_FLOOR_X, SECOND_FLOOR_Y))
                        pio_path.append((final_door_target_x, SECOND_FLOOR_CURVE_Y))
                        pio_path.append((final_door_target_x, final_door_target_y))
                pio_state = PIO_STATE_FOLLOWING_PATH
                if pio_path and abs(pio_x - pio_path[0][0]) < tolerance and abs(pio_y - pio_path[0][1]) < tolerance:
                    pio_path.pop(0)
                if pio_path:
                    pio_target_x, pio_target_y = pio_path.pop(0)
                else:
                    pio_state = PIO_STATE_IDLE
                pio_cleaning = True
                pio_cleaning_start_time = 0
                pio_cleaning_door = caution_door
                # Progress bar will start when Pio reaches the door
                action_taken = True

            # 1. Check if a check icon was clicked (ALWAYS ALLOWED)
            check_door = check_popup.check_click((mouse_x, mouse_y))
            if check_door and group_waiting_for_check:
                final_door_target_x, final_door_target_y = door_manager.door_target_positions[check_door]
                group_waiting_for_check.start_following((final_door_target_x, final_door_target_y), check_door)
                door_manager.lock_door(check_door)
                group_waiting_for_check = None
                action_taken = True

            # 1.5. Check if a door was clicked directly for room assignment (when student is waiting for check)
            if not action_taken and group_waiting_for_check:
                clicked_door = door_manager.check_click((mouse_x, mouse_y))
                if clicked_door and not door_manager.is_door_locked(clicked_door) and not door_manager.is_door_pending(clicked_door):
                    # Direct door click for room assignment
                    final_door_target_x, final_door_target_y = door_manager.door_target_positions[clicked_door]
                    group_waiting_for_check.start_following((final_door_target_x, final_door_target_y), clicked_door)
                    door_manager.lock_door(clicked_door)
                    group_waiting_for_check = None
                    check_popup.hide_checks()  # Hide the check popup
                    action_taken = True

            # 2. If not, check for key icon clicks or student clicks (ALWAYS ALLOWED)
            if not action_taken:
                frozen_key_clicked = False
                for group in groups:
                    if hasattr(group, "state") and group.state == "stopped":
                        available_doors = [d for d in door_manager.door_click_areas if not door_manager.is_door_locked(d) and not door_manager.is_door_pending(d)]
                        group.key.clickable = bool(available_doors)
                        
                        # Check if key was clicked OR if student group was clicked
                        key_clicked = group.key.check_click((mouse_x, mouse_y))
                        student_clicked = group.check_student_click((mouse_x, mouse_y))
                        
                        if key_clicked or student_clicked:
                            if available_doors:
                                play_keys_sfx()  # Play SFX only when key is actually clickable
                                check_popup.show_checks(available_doors)
                                group.state = "waiting_for_check"
                                group_waiting_for_check = group
                                action_taken = True
                            else:
                                frozen_key_clicked = True
                            break

            # 3. If not, check for door clicks (Only block Pio movement during cleaning, not student assignments)
            if not action_taken and not check_popup.active:
                if not is_any_key_frozen():
                        
                        # Always allow student assignments, regardless of cleaning state
                        for group in groups:
                            if hasattr(group, "state") and group.state == "ready_to_follow":
                                group.start_following((final_door_target_x, final_door_target_y), group.target_door_name)
                        action_taken = True

            # 4. If not, check for ground movement (BLOCKED while cleaning)
            if not action_taken and not check_popup.active and not pio_cleaning:
                for group in groups:
                    if hasattr(group, "state") and group.state == "stopped":
                        available_doors = [d for d in door_manager.door_click_areas if not door_manager.is_door_locked(d) and not door_manager.is_door_pending(d)]
                        group.key.clickable = bool(available_doors)
                if mouse_y > SECOND_FLOOR_CURVE_Y - pio_frame_height * pio_scale / 2:
                    ground_min_y = GROUND_Y - int(pio_frame_height * pio_scale / 2)
                    ground_max_y = GROUND_Y + int(pio_frame_height * pio_scale / 2)
                    target_y = GROUND_Y
                    min_x = 0
                    max_x = VIRTUAL_WIDTH - pio_frame_width * pio_scale
                    target_x = max(min_x, min(mouse_x, max_x))
                    pio_path = []
                    pio_path.append((pio_x, pio_y))
                    if pio_y <= SECOND_FLOOR_CURVE_Y + pio_speed:
                        if pio_x < STAIRS_HORIZONTAL_MID_X:
                            pio_path.append((STAIRS_LEFT_SECOND_FLOOR_X, SECOND_FLOOR_Y))
                            pio_path.append((STAIRS_LEFT_GROUND_X, GROUND_Y))
                        else:
                            pio_path.append((STAIRS_RIGHT_SECOND_FLOOR_X, SECOND_FLOOR_Y))
                            pio_path.append((STAIRS_RIGHT_GROUND_X, GROUND_Y))
                    pio_path.append((target_x, target_y))
                    pio_state = PIO_STATE_FOLLOWING_PATH
                    if pio_path and abs(pio_x - pio_path[0][0]) < pio_speed and abs(pio_y - pio_path[0][1]) < pio_speed:
                        pio_path.pop(0)
                    if pio_path:
                        pio_target_x, pio_target_y = pio_path.pop(0)
                    else:
                        pio_state = PIO_STATE_IDLE
                    action_taken = True
                if not action_taken:
                    pio_state = PIO_STATE_IDLE

    # --- GAME UPDATE LOGIC: Freeze everything when paused or tutorial is showing ---
    if not game_paused and not help_system.is_tutorial_showing():
        pio_moving = False
        tolerance = pio_speed / 2.0
        if pio_state == PIO_STATE_FOLLOWING_PATH:
            if abs(pio_target_x - pio_x) < tolerance and abs(pio_target_y - pio_y) < tolerance:
                pio_x = pio_target_x
                pio_y = pio_target_y
                if pio_path:
                    pio_target_x, pio_target_y = pio_path.pop(0)
                else:
                    pio_state = PIO_STATE_IDLE
                    pio_moving = False                    # Check if Pio reached a storage room for item pickup
                    if pio_target_storage and not pio_carrying_item:
                        # Check if Pio is close enough to the storage room position
                        storage_data = item_request_manager.storage_rooms[pio_target_storage]
                        storage_pos = storage_data["position"]
                        if abs(pio_x - storage_pos[0]) < tolerance * 2 and abs(pio_y - GROUND_Y) < tolerance:
                            # Pick up the item
                            item_type = item_request_manager.pickup_item(pio_target_storage)
                            if item_type:
                                pio_carrying_item = item_type
                                print(f"Pio picked up {item_type}!")
                            pio_target_storage = None
                    
                    # Check if Pio reached the trash bin for item disposal
                    if pio_target_storage == "trash_bin" and pio_carrying_item:
                        trash_pos = item_request_manager.trash_bin_position
                        if abs(pio_x - trash_pos[0]) < tolerance * 2 and abs(pio_y - GROUND_Y) < tolerance:
                            # Dispose of the item
                            discarded_item = pio_carrying_item
                            pio_carrying_item = None
                            pio_target_storage = None
                            pio_carrying_for_group = None  # Clear delivery target
                            play_trash_sfx()  
                            print(f"Pio discarded {discarded_item} in the trash!")
                    
                    # Check if Pio reached a student for item delivery
                    if pio_carrying_for_group and pio_carrying_item:
                        # Check if the group still has the matching request
                        if (hasattr(pio_carrying_for_group, 'item_request') and 
                            pio_carrying_for_group.item_request == pio_carrying_item and
                            hasattr(pio_carrying_for_group, 'target_door_name')):
                            door_pos = door_manager.door_target_positions[pio_carrying_for_group.target_door_name]
                            if abs(pio_x - door_pos[0]) < tolerance and abs(pio_y - door_pos[1]) < tolerance:                                # Deliver the item
                                item_request_manager.remove_request(pio_carrying_for_group)
                                delivered_item = pio_carrying_item
                                pio_carrying_item = None
                                pio_carrying_for_group = None  # Clear delivery target
                                pio_target_storage = None  # Clear any storage target
                                try:
                                    play_item_dropped_sfx()  # Play SFX when item is dropped at the door
                                except Exception as e:
                                    print(f"SFX error: {e}")
                                print("Item delivered successfully!")
                                # Give points for successful delivery
                                score_manager.reward_item_delivery()
                                
                                # No need to restock - items stay in storage rooms
                        else:
                            pio_carrying_for_group = None
                               
            else:
                pio_moving = True
                dist_x = pio_target_x - pio_x
                dist_y = pio_target_y - pio_y
                distance = pygame.math.Vector2(dist_x, dist_y).length()
                if distance > 0:
                    move_x = pio_speed * (dist_x / distance)
                    move_y = pio_speed * (dist_y / distance)
                    if move_x > 0:
                        pio_facing_right = True
                    elif move_x < 0:
                        pio_facing_right = False
                    if abs(move_x) > abs(dist_x): move_x = dist_x
                    if abs(move_y) > abs(dist_y): move_y = dist_y
                    pio_x += move_x
                    pio_y += move_y
        elif pio_state == PIO_STATE_MOVING_TO_POINT:
            if abs(pio_target_x - pio_x) < tolerance and abs(pio_target_y - pio_y) < tolerance:
                pio_x = pio_target_x
                pio_y = pio_target_y
                pio_state = PIO_STATE_IDLE
                pio_moving = False
            else:
                pio_moving = True
                dist_x = pio_target_x - pio_x
                dist_y = pio_target_y - pio_y
                distance = pygame.math.Vector2(dist_x, dist_y).length()
                if distance > 0:
                    move_x = pio_speed * (dist_x / distance)
                    move_y = pio_speed * (dist_y / distance)
                    if move_x > 0:
                        pio_facing_right = True
                    elif move_x < 0:
                        pio_facing_right = False
                    if abs(move_x) > abs(dist_x): move_x = dist_x
                    if abs(move_y) > abs(dist_y): move_y = dist_y
                    pio_x += move_x
                    pio_y += move_y

        pio_x = max(0, min(pio_x, VIRTUAL_WIDTH - pio_frame_width * pio_scale))
        pio_y = max(0, min(pio_y, VIRTUAL_HEIGHT - pio_frame_height * pio_scale))

        if pio_moving and current_time - pio_last_update > pio_animation_cooldown:
            pio_frame = (pio_frame + 1) % pio_animation_steps
            pio_last_update = current_time
        elif not pio_moving:
            pio_frame = 0

        for i, group in enumerate(groups):
            front_group = groups[i - 1] if i > 0 else None
            # Check if group just entered a room to start hourglass timer
            old_state = getattr(group, '_previous_state', None)
            if group.state == "in_room" and old_state != "in_room" and hasattr(group, 'target_door_name'):
                print(f"Group entered room {group.target_door_name}")
                # Student just entered room - start hourglass timer
                door_pos = door_manager.door_target_positions[group.target_door_name]
                room_duration = getattr(group, 'room_stay_duration', 12000)  # Default 12 seconds
                hourglass_timer.start_room_usage(group.target_door_name, door_pos, current_time, room_duration)
                # 70% chance for a request, and with a 2-second delay
                request_chance = random.random()
                print(f"Request chance: {request_chance}")
                if request_chance < 0.7:  # 70% chance for a request
                    print("Setting up request cooldown...")
                    # Set a 2-second delay before the request appears
                    group.request_cooldown_start = current_time
                    group.request_pending = True
                else:
                    print("No request (random chance)")
                # Mark that this group has entered a room (for penalty logic)
                group.entered_room = True
            
            # Check if group just left a room to stop hourglass timer
            if group.state == "exiting_room" and old_state == "in_room" and hasattr(group, 'target_door_name'):
                # Student just left room - stop hourglass timer
                hourglass_timer.stop_room_usage(group.target_door_name)
                # Remove any unfulfilled item requests
                item_request_manager.remove_request(group)
              # Check for pending item requests (after cooldown)
            if (hasattr(group, 'request_pending') and group.request_pending and 
                hasattr(group, 'request_cooldown_start') and group.state == "in_room"):
                elapsed_cooldown = current_time - group.request_cooldown_start
                if elapsed_cooldown >= 2000:  # 2 seconds cooldown
                    print("Creating item request!")
                    item_request_manager.create_request(group)
                    group.request_pending = False
            
            # Store current state for next iteration
            group._previous_state = group.state
            
            group.update(current_time, front_group, door_manager)
        # Check for groups leaving without entering a room (apply penalty)
        for group in groups:
            # Check if group just transitioned from "stopped" to "exiting" (never entered a room)
            old_state = getattr(group, '_previous_state', None)
            if (group.state == "exiting" and old_state == "stopped" and 
                not getattr(group, 'entered_room', False) and not getattr(group, 'penalty_applied', False)):
                # Group left without being served - apply ONE penalty regardless of reason
                score_manager.apply_student_leaving_penalty("student group left without being served")
                current_lives -= 1
                play_life_lose_sfx()  # Play sound when life is lost
                group.penalty_applied = True
                print(f"Lives remaining: {current_lives}")
                # Note: Could be due to no key click, no available doors, or player didn't assign room

        groups = [g for g in groups if not g.is_done()]
        
        # Check for game over condition (no lives left)
        if current_lives <= 0:
            stop_music()
            scaled_surface = pygame.transform.scale(virtual_surface, (screen_width, screen_height))
            screen.blit(scaled_surface, (0, 0))
            pygame.display.flip()
            
            # Update high score if current score is higher
            if stats.score > high_score:
                high_score = stats.score
                play_game_complete_sfx()
            else:
                play_game_over_sfx()

            result = show_gameover_screen(screen, stats.score, high_score)
            
            if result == "play_again":
                # Loop back to title and welcoming screen
                while True:
                    play_home_music()
                    show_title_screen(screen)
                    result = show_welcoming_screen(screen)
                    if result == "back":
                        continue  # balik ulit sa title screen
                    else:
                        break    # proceed sa bagong game 
                stop_music()
                play_game_music()
                # Reset ALL game state variables
                stats.score = 0
                scoreboard.prep_score()  # Reset the scoreboard display
                groups.clear()
                # Reset score manager (will reset scoreboard internally)
                score_manager = ScoreManager(scoreboard)
                current_lives = max_lives
                pio_x = VIRTUAL_WIDTH - pio_frame_width * pio_scale - 50
                pio_y = Settings.GROUND_Y
                pio_facing_right = False
                pio_frame = 0
                pio_last_update = pygame.time.get_ticks()
                pio_target_x, pio_target_y = pio_x, pio_y
                pio_path = []
                pio_state = PIO_STATE_IDLE
                pio_target_storage = None
                pio_carrying_item = None
                pio_carrying_for_group = None
                item_request_manager = ItemRequestManager()
                pio_cleaning = False
                pio_cleaning_start_time = 0
                pio_cleaning_door = None
                doors_with_caution.clear()
                group_waiting_for_check = None
                groups_with_points.clear()
                current_time = pygame.time.get_ticks()
                game_start_time = current_time
                first_group_time = current_time + 4000
                next_group_time = first_group_time
                game_paused = False
                pause_start_time = 0
                total_pause_duration = 0
                timer = GameTimer(
                    duration_ms=TIMER_DURATION_MS,
                    font_path="assets/Space_Mono/SpaceMono-Bold.ttf",
                    font_size=32,
                    timer_bg_path="assets/images/timer-bg.png",
                    pos=(40, 30)
                )
                hourglass_timer = HourglassTimer()
                cleaning_progress_bar = CleaningProgressBar()
                door_manager = DoorManager()
                caution_manager = CautionManager('assets/images/caution.png')
                check_popup = CheckPopup()
                game_paused = False
                if hasattr(pause_menu, "set_paused"):
                    pause_menu.set_paused(False)
                elif hasattr(pause_menu, "is_paused"):
                    pause_menu.active = False
                stop_music()
                play_game_music()
                continue
            else:
                break  # quit game if not play again
        
        # --- Pio Pi cleaning logic ---
        if pio_cleaning and pio_cleaning_door:
            cleaning_x, cleaning_y = door_manager.door_target_positions[pio_cleaning_door]
            if abs(pio_x - cleaning_x) < pio_speed and abs(pio_y - cleaning_y) < pio_speed:
                if pio_cleaning_start_time == 0:
                    pio_cleaning_start_time = current_time
                    # Start progress bar when Pio reaches the door
                    door_pos = door_manager.door_target_positions[pio_cleaning_door]
                    cleaning_progress_bar.start_cleaning(door_pos, current_time)
                    play_caution_cleaning_sfx()  # Play SFX only once when cleaning starts
                if current_time - pio_cleaning_start_time >= 3000:
                    caution_manager.remove_caution(pio_cleaning_door)
                    doors_with_caution.discard(pio_cleaning_door)
                    door_manager.unlock_door(pio_cleaning_door)
                    cleaning_progress_bar.stop_cleaning()  # Stop progress bar
                    pio_cleaning = False
                    pio_cleaning_start_time = 0
                    pio_cleaning_door = None
                    for group in groups:
                        if hasattr(group, "state") and group.state == "stopped":
                            available_doors = [d for d in door_manager.door_click_areas if not door_manager.is_door_locked(d) and not door_manager.is_door_pending(d)]
                            group.key.clickable = bool(available_doors)

        # --- Update hourglass timer (for students in rooms) ---
        hourglass_timer.update(current_time)

        # --- No need to update cleaning progress bar here - it draws dynamically ---

        # --- Only update queue positions for groups that are in the queue ---
        queue_pos = 0
        for group in groups:
            if group.state in ["entering", "stopped", "waiting_for_check"]:
                new_stop = max(322 - queue_pos * GROUP_SPACING, 322)
                if group.state in ["entering", "stopped"] and group.stop_position != new_stop:
                    group.stop_position = new_stop
                    if group.state == "stopped":
                        group.state = "entering"
                        group.stop_time = None
                queue_pos += 1

        # --- Group spawning ---
        queue_count = len([g for g in groups if g.state in ["entering", "stopped", "waiting_for_check"]])
        if current_time >= next_group_time:
            chosen_type = random.choice(group_types)
            stop_x = max(322 - queue_count * GROUP_SPACING, 322)
            new_group = StudentGroup(
                current_time, chosen_type, stop_x, group_sprites, load_group_frames,
                VIRTUAL_WIDTH, group_frame_height, key_image, key_mask, key_width, key_height
            )
            groups.append(new_group)
            
            # Calculate dynamic spawn interval based on game progression
            time_elapsed = current_time - game_start_time
            spawn_interval = calculate_spawn_interval(time_elapsed)
            next_group_time = current_time + spawn_interval
            current_time = pygame.time.get_ticks()

        groups = [group for group in groups if not group.is_done()]

        # --- Guard update (only if not paused) ---
        sheet.update(current_time)

        # --- When a group leaves a room, add caution sign IMMEDIATELY (per door) ---
        for group in groups:
            if hasattr(group, "state") and group.state == "leaving" and getattr(group, "target_door_name", None):
                door = group.target_door_name
                if door not in doors_with_caution:
                    caution_manager.add_caution(door)
                    doors_with_caution.add(door)
                if not getattr(group, "score_added", False):
                    points = score_manager.reward_room_exit(getattr(group, 'name', 'StudentGroup'))
                    group.score_added = True    # --- Drawing and update code (keep your existing drawing logic) ---
    virtual_surface.blit(background_image, (0, 0))
    virtual_surface.blit(building_image, building_position)
    virtual_surface.blit(room_image, room_position)
    sheet.draw(virtual_surface)
    virtual_surface.blit(border_image, border_position)
    
    # Draw trash bin EARLY so it appears behind characters
    item_request_manager.draw_trash_bin(virtual_surface)
    
    check_popup.draw(virtual_surface)
    door_manager.draw_door_states(virtual_surface)
    # --- Draw caution signs, pass paused state for overlay effect ---
    caution_manager.draw(
        virtual_surface,
        door_manager.door_click_areas,
        paused=game_paused
    )

    # --- TEST DRAW: Draw a red circle to confirm game loop is running in browser ---
    pygame.draw.circle(virtual_surface, (255, 0, 0), (100, 100), 50)
    
    # Draw cleaning progress bar if cleaning
    # --- Freeze progress bar visually when paused or tutorial showing, do not reset ---
    if not game_paused and not help_system.is_tutorial_showing():
        cleaning_progress_bar.draw(virtual_surface, current_time)
        # Track the last progress time for freezing
        last_cleaning_progress_time = current_time
    else:
        # Use the last progress time before pause to freeze the bar
        if 'last_cleaning_progress_time' not in locals():
            last_cleaning_progress_time = pio_cleaning_start_time if pio_cleaning_start_time else current_time
        cleaning_progress_bar.draw(virtual_surface, last_cleaning_progress_time)
    # Draw hourglass timers for students in rooms
    hourglass_timer.draw(virtual_surface)
    
    for group in groups:
        group.draw(virtual_surface)
    
    # Update and draw item request system (only when not paused and tutorial not showing)
    if not game_paused and not help_system.is_tutorial_showing():
        item_request_manager.update_requests(current_time)  # Handle timeouts
        item_request_manager.update_request_positions()  # Handle animations
        
        # Check for item request penalties
        item_penalties = item_request_manager.get_and_clear_penalties()
        if item_penalties > 0:
            # Apply penalty for each unfulfilled request
            for _ in range(item_penalties // 10):  # Since each penalty is 10 points
                score_manager.apply_item_request_penalty()
    
    item_request_manager.draw_requests(virtual_surface, current_time)  # Pass frozen current_time
    item_request_manager.draw_storage_rooms(virtual_surface)
    
    # Draw Pio
    if pio_facing_right:
        virtual_surface.blit(pio_right_frames[pio_frame], (pio_x, pio_y))
    else:
        virtual_surface.blit(pio_left_frames[pio_frame], (pio_x, pio_y))
    
    # Draw carried item on Pio
    if pio_carrying_item:
        if pio_carrying_item == "hdmi":
            carried_icon = item_request_manager.hdmi_pick
        else:  # remote
            carried_icon = item_request_manager.remote_pick
        
        # Position the carried item above Pio
        carry_x = pio_x + (pio_frame_width * pio_scale // 2) - 12
        carry_y = pio_y - 20
        virtual_surface.blit(carried_icon, (carry_x, carry_y))
    
    # Draw the score
    if not game_paused and not help_system.is_tutorial_showing():
        scoreboard.update_floating_points(current_time)  # Update floating point animations only when not paused or tutorial showing
    scoreboard.show_score()

    # Draw the timer (timer.draw always called, but timer logic is frozen when paused)
    timer.draw(virtual_surface)
    
    # Draw lives/stars below the timer (using single star animation sprite sheet)
    # Always show 5 stars, they turn from full golden → half-gray but never disappear
    for i in range(5):
        star_x = lives_start_x + (i * (star_width + 2))  # 2px spacing between stars
        
        # Calculate which state this star should be in based on current_lives
        # Each star represents up to 2 lives
        star_lives = max(0, current_lives - (i * 2))  # How many lives this star represents
        
        if star_lives >= 2:
            # Draw full golden star (frame 0) - this star has 2 lives
            source_rect = pygame.Rect(0, 0, star_width, star_height)
            virtual_surface.blit(lives_image, (star_x, lives_y), source_rect)
        elif star_lives == 1:
            # Draw half-gray star (frame 1) - this star has 1 life (odd life loss)
            if star_frames > 1:
                source_rect = pygame.Rect(star_width, 0, star_width, star_height)
                virtual_surface.blit(lives_image, (star_x, lives_y), source_rect)
            else:
                # Fallback if only one frame available
                source_rect = pygame.Rect(0, 0, star_width, star_height)
                virtual_surface.blit(lives_image, (star_x, lives_y), source_rect)
        else:
            # star_lives == 0 - Draw full gray star (frame 2) when even lives lost
            if star_frames > 2:
                source_rect = pygame.Rect(star_width * 2, 0, star_width, star_height)
                virtual_surface.blit(lives_image, (star_x, lives_y), source_rect)
            elif star_frames > 1:
                # Fallback to half-gray if no full gray frame
                source_rect = pygame.Rect(star_width, 0, star_width, star_height)
                virtual_surface.blit(lives_image, (star_x, lives_y), source_rect)
            else:
                # Fallback to full star if only one frame available
                source_rect = pygame.Rect(0, 0, star_width, star_height)
                virtual_surface.blit(lives_image, (star_x, lives_y), source_rect)

    # Draw the pause menu overlay ON TOP if paused
    if game_paused:
        pause_menu.draw(virtual_surface)
    else:
        if hasattr(pause_menu, "draw_settings_button"):
            pause_menu.draw_settings_button(virtual_surface)
    
    # Draw help system (button and tutorial overlay if active)
    help_system.draw_help_button(virtual_surface)
    if help_system.is_tutorial_showing():
        help_system.draw_tutorial(virtual_surface, game_frame=virtual_surface.copy())

    scaled_surface = pygame.transform.scale(virtual_surface, (screen_width, screen_height))
    screen.blit(scaled_surface, (0, 0))    # Game over logic
    if timer.is_time_up():
        stop_music()
        scaled_surface = pygame.transform.scale(virtual_surface, (screen_width, screen_height))
        screen.blit(scaled_surface, (0, 0))
        pygame.display.flip()
        
        # Update high score if current score is higher
        if stats.score > high_score:
            high_score = stats.score
            play_game_complete_sfx()
        elif stats.score < high_score:
            play_game_over_sfx()

        result = show_gameover_screen(screen, stats.score, high_score)
        
        if result == "play_again":
            # Loop back to title and welcoming screen
            while True:
                play_home_music()
                show_title_screen(screen)
                result = show_welcoming_screen(screen)
                if result == "back":
                    continue  # balik ulit sa title screen
                else:
                    break    # proceed sa bagong game 
            stop_music()
            play_game_music()            # Reset ALL game state variables
            stats.score = 0
            scoreboard.prep_score()  # Reset the scoreboard display
            groups.clear()
            
            # Reset score manager (will reset scoreboard internally)
            score_manager = ScoreManager(scoreboard)
            
            # Reset lives
            current_lives = max_lives
            
            # Reset Pio state
            pio_x = VIRTUAL_WIDTH - pio_frame_width * pio_scale - 50
            pio_y = Settings.GROUND_Y
            pio_facing_right = False
            pio_frame = 0
            pio_last_update = pygame.time.get_ticks()
            pio_target_x, pio_target_y = pio_x, pio_y
            pio_path = []
            pio_state = PIO_STATE_IDLE
            pio_target_storage = None
            
            # Reset item system
            pio_carrying_item = None
            pio_carrying_for_group = None
            item_request_manager = ItemRequestManager()  # Reset item request manager
            
            # Reset cleaning state
            pio_cleaning = False
            pio_cleaning_start_time = 0
            pio_cleaning_door = None
            doors_with_caution.clear()
            
            # Reset group management
            group_waiting_for_check = None
            groups_with_points.clear()
            
            # Reset spawn timers with current time
            current_time = pygame.time.get_ticks()
            game_start_time = current_time  # Reset game start time for spawn calculations
            first_group_time = current_time + 4000
            next_group_time = first_group_time
            
            # Reset pause system
            game_paused = False
            pause_start_time = 0
            total_pause_duration = 0
            
            # Reset timers
            timer = GameTimer(
                duration_ms=TIMER_DURATION_MS,
                font_path="assets/Space_Mono/SpaceMono-Bold.ttf", 
                font_size=32,
                timer_bg_path="assets/images/timer-bg.png",
                pos=(40, 30)
            )
            
            # Reset hourglass and cleaning progress timers
            hourglass_timer = HourglassTimer()  # Create new instance
            cleaning_progress_bar = CleaningProgressBar()  # Create new instance
            
            # Reset door manager and caution manager states
            door_manager = DoorManager()
            caution_manager = CautionManager('assets/images/caution.png')
            
            # Reset popup states
            check_popup = CheckPopup()
            
            # Reset pause menu
            game_paused = False
            if hasattr(pause_menu, "set_paused"):
                pause_menu.set_paused(False)
            elif hasattr(pause_menu, "is_paused"):
                pause_menu.active = False
            
            continue  # restart main game loop

        else:
            break  # quit game if not play again

    pygame.display.flip()