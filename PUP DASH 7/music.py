import pygame

def play_home_music():
    pygame.mixer.init()
    pygame.mixer.music.load("assets/music/home_soundtrack.mp3")
    pygame.mixer.music.set_volume(0.5)
    pygame.mixer.music.play(-1)

def play_game_music():
    pygame.mixer.init()
    pygame.mixer.music.load("assets/music/pup_dash_soundtrack.mp3")
    pygame.mixer.music.set_volume(0.5)
    pygame.mixer.music.play(-1)

def stop_music():
    pygame.mixer.music.stop()

def play_button_sfx():
    sound = pygame.mixer.Sound("assets/music/click_button.wav")
    sound.set_volume(0.4)
    sound.play()

def play_menu_sfx():
    sound = pygame.mixer.Sound("assets/music/click_menu.wav")
    sound.set_volume(0.4)
    sound.play()

def play_game_complete_sfx():
    sound = pygame.mixer.Sound("assets/music/game_complete.wav")
    sound.set_volume(0.4)
    sound.play()

def play_game_over_sfx():
    sound = pygame.mixer.Sound("assets/music/game_over.wav")
    sound.set_volume(0.4)
    sound.play()

def play_score_sfx():
    sound = pygame.mixer.Sound("assets/music/score_added.wav")
    sound.set_volume(0.1)
    sound.play()

def play_caution_cleaning_sfx():
    sound = pygame.mixer.Sound("assets/music/cleaning.WAV")
    sound.set_volume(0.5)
    sound.play()

def play_keys_sfx():
    sound = pygame.mixer.Sound("assets/music/grab_keys.WAV")
    sound.set_volume(0.5)
    sound.play()

def play_door_closed_sfx():
    sound = pygame.mixer.Sound("assets/music/door_closed.WAV")
    sound.set_volume(0.6)
    sound.play()

def play_door_open_sfx():
    sound = pygame.mixer.Sound("assets/music/door_open.WAV")
    sound.set_volume(0.4)
    sound.play()

def play_trash_sfx():
    sound = pygame.mixer.Sound("assets/music/trash.WAV")
    sound.set_volume(0.4)
    sound.play()

def play_item_picked_sfx():
    sound = pygame.mixer.Sound("assets/music/item_pick.WAV")
    sound.set_volume(0.4)
    sound.play()

def play_item_dropped_sfx():
    sound = pygame.mixer.Sound("assets/music/item_drop.WAV")
    sound.set_volume(0.4)
    sound.play()

def pause_music():
    pygame.mixer.music.pause()

def unpause_music():
    pygame.mixer.music.unpause()

def pause_all_sfx():
    """Pause all currently playing sound effects"""
    pygame.mixer.pause()

def unpause_all_sfx():
    """Unpause all sound effects"""
    pygame.mixer.unpause()

def play_life_lose_sfx():
    sound = pygame.mixer.Sound("assets/music/life.wav")
    sound.set_volume(0.5)
    sound.play()

def play_points_plus_sfx():
    """Sound effect for gaining points"""
    sound = pygame.mixer.Sound("assets/music/score_added.wav")
    sound.set_volume(0.3)
    sound.play()

def play_points_minus_sfx():
    """Sound effect for losing points/penalties"""
    sound = pygame.mixer.Sound("assets/music/life.wav")
    sound.set_volume(0.3)
    sound.play()