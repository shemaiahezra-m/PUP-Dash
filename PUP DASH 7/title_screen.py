import sys
import pygame
import random
import spritesheet
from music import play_button_sfx

def darken_image(image, darkness=40):
    """Return a darkened copy of an image."""
    dark_img = pygame.Surface(image.get_size(), flags=pygame.SRCALPHA)
    dark_img.fill((0, 0, 0, darkness))  # RGBA overlay
    copy = image.copy()
    copy.blit(dark_img, (0, 0), special_flags=pygame.BLEND_RGBA_SUB)
    return copy

def scale_down(image, scale=0.95):
    """Return a scaled-down version of an image."""
    w, h = image.get_size()
    new_size = (int(w * scale), int(h * scale))
    return pygame.transform.smoothscale(image, new_size)

def show_title_screen(screen):
    sw, sh = screen.get_width(), screen.get_height()

    # Load and scale background
    background = pygame.image.load("assets/Title UI/background-2.png")
    background = pygame.transform.scale(background, (sw, sh))

    # Load and scale clouds overlay
    clouds = pygame.image.load("assets/Title UI/cloud.png").convert_alpha()
    clouds = pygame.transform.scale(clouds, (sw, sh))

    # Title
    title_img = pygame.image.load("assets/Title UI/Title.png")
    title_img = pygame.transform.scale(title_img, (int(sw * 1), int(sh * 0.9)))
    title_rect = title_img.get_rect(center=(sw // 2, int(sh * 0.50)))

    # Start button
    start_img = pygame.image.load("assets/Title UI/StartB.png").convert_alpha()
    start_img = pygame.transform.scale(start_img, (int(sw * 0.25), int(sh * 0.15)))
    start_hover_scaled_dark = darken_image(scale_down(start_img))
    start_rect = start_img.get_rect(center=(sw // 2, int(sh * 0.55)))

    # Quit button
    quit_img = pygame.image.load("assets/Title UI/QuitB.png").convert_alpha()
    quit_img = pygame.transform.scale(quit_img, (int(sw * 0.18), int(sh * 0.13)))
    quit_hover_scaled_dark = darken_image(scale_down(quit_img))
    quit_rect = quit_img.get_rect(center=(sw // 2, int(sh * 0.70)))

    # Load Pio animation sprites using sprite sheet (same as game)
    try:
        from settings import Settings
        
        pio_sprite_image = pygame.image.load("assets/images/pio-pi.png").convert_alpha()
        pio_sprite_sheet = spritesheet.SpriteSheet(pio_sprite_image)
        pio_frame_width = Settings.PIO_FRAME_WIDTH
        pio_frame_height = Settings.PIO_FRAME_HEIGHT
        pio_scale = Settings.PIO_SCALE
        pio_animation_steps = Settings.PIO_ANIMATION_STEPS
        pio_animation_cooldown = Settings.PIO_ANIMATION_COOLDOWN
        pio_speed = Settings.PIO_SPEED
        
        # Create animation frames
        pio_right_frames = []
        pio_left_frames = []
        for i in range(pio_animation_steps):
            image = pio_sprite_sheet.get_image(i, pio_frame_width, pio_frame_height, pio_scale, None)
            pio_right_frames.append(image)
            pio_left_frames.append(pygame.transform.flip(image, True, False))
        
        # Load items that Pio will carry (using game assets)
        hdmi_img = pygame.image.load("assets/Items/hdmi pick.png").convert_alpha()
        remote_img = pygame.image.load("assets/Items/remote pick.png").convert_alpha()
        
        animation_enabled = True
    except Exception as e:
        print(f"Could not load Pio animation sprites: {e}")
        animation_enabled = False

    # Animation variables (using game coordinates scaled to screen)
    if animation_enabled:
        # Scale coordinates from game's virtual resolution to screen resolution
        virtual_width = Settings.VIRTUAL_WIDTH
        virtual_height = Settings.VIRTUAL_HEIGHT
        scale_x = sw / virtual_width
        scale_y = sh / virtual_height
        
        # Pio position and movement (fixed Y position at 760 scaled to screen)
        pio_x = (virtual_width - pio_frame_width * pio_scale - 50) * scale_x  # Start from right like in game
        pio_y = 760 * scale_y  # Fixed Y position at 760
        pio_facing_right = False  # Start facing left like in game
        pio_frame = 0
        pio_last_update = pygame.time.get_ticks()
        
        # Movement boundaries (scaled)
        pio_min_x = -100 * scale_x  # Extended left boundary for wrap-around
        pio_max_x = (virtual_width + 50) * scale_x  # Extended right boundary for wrap-around  
        pio_direction = -1  # Start moving left
        
    # Items Pio is carrying
        items = [hdmi_img, remote_img]

    # Add clock for consistent frame rate
    clock = pygame.time.Clock()
    mouse_held = False

    while True:
        clock.tick(60)  # Limit to 60 FPS for smooth animation
        current_time = pygame.time.get_ticks()
        
        screen.blit(background, (0, 0))
        
        # Draw Pio animation using proper sprite sheet (same as game)
        if animation_enabled:
            # Update Pio animation frame (smoother timing)
            pio_moving = False
            if current_time - pio_last_update > pio_animation_cooldown // 2:  # Animation update timing
                # Update position (slightly slower speed for smoother movement)
                pio_x += pio_speed * pio_direction * scale_x * 1.2  # Slower than before for smooth movement
                pio_moving = True
                
                # Wrap-around logic: if Pio exits one side, reappear on the other side
                sprite_width = pio_frame_width * pio_scale * scale_x
                if pio_direction == 1 and pio_x > pio_max_x + sprite_width:  # Moving right, exit right side
                    pio_x = pio_min_x - sprite_width  # Reappear from left side
                elif pio_direction == -1 and pio_x < pio_min_x - sprite_width:  # Moving left, exit left side
                    pio_x = pio_max_x + sprite_width  # Reappear from right side
                
                # Update animation frame
                if pio_moving:
                    pio_frame = (pio_frame + 1) % pio_animation_steps
                else:
                    pio_frame = 0
                
                pio_last_update = current_time
        
        # Draw Pio using sprite sheet frames (same as game)
        if animation_enabled:
            # Draw Pio with proper sprite sheet animation
            if pio_facing_right:
                pio_sprite = pio_right_frames[pio_frame]
            else:
                pio_sprite = pio_left_frames[pio_frame]
            
            pio_copy = pio_sprite.copy()
            pio_copy.set_alpha(220)  # Slightly transparent
            screen.blit(pio_copy, (int(pio_x), int(pio_y)))
            
            # Draw items Pio is carrying (larger size)
            item_scale = 0.4 * scale_x  # Much larger items (increased from 0.15 to 0.4)
            item_offset_x = (15 if pio_facing_right else -15) * scale_x
            for i, item in enumerate(items):
                # Scale items to match screen resolution (larger)
                item_width = int(item.get_width() * item_scale)
                item_height = int(item.get_height() * item_scale)
                scaled_item = pygame.transform.scale(item, (item_width, item_height))
                
                item_x = pio_x + item_offset_x + (i * 30 * scale_x)  # More spacing between items
                item_y = pio_y - (40 + i * 25) * scale_y  # Higher above Pio with more spacing
                item_copy = scaled_item.copy()
                item_copy.set_alpha(240)  # Items more visible
                screen.blit(item_copy, (int(item_x), int(item_y)))

        screen.blit(title_img, title_rect)
        screen.blit(clouds, (0, 0))  # Add clouds overlay in front of title

        mouse_pos = pygame.mouse.get_pos()

        # START button render (scale down and darken on hover)
        if start_rect.collidepoint(mouse_pos):
            scaled_rect = start_hover_scaled_dark.get_rect(center=start_rect.center)
            screen.blit(start_hover_scaled_dark, scaled_rect)
        else:
            screen.blit(start_img, start_rect)

        # QUIT button render (scale down and darken on hover)
        if quit_rect.collidepoint(mouse_pos):
            scaled_rect = quit_hover_scaled_dark.get_rect(center=quit_rect.center)
            screen.blit(quit_hover_scaled_dark, scaled_rect)
        else:
            screen.blit(quit_img, quit_rect)

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                play_button_sfx()
                pygame.quit()
                sys.exit()

            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_held = True

            elif event.type == pygame.MOUSEBUTTONUP:
                mouse_held = False
                if start_rect.collidepoint(event.pos):
                    play_button_sfx()
                    print("Start button clicked!")
                    return
                elif quit_rect.collidepoint(event.pos):
                    play_button_sfx()
                    pygame.quit()
                    sys.exit()