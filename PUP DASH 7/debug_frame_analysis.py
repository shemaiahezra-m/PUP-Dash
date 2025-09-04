#!/usr/bin/env python3

import pygame
import sys
import os

# Add current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Initialize Pygame
pygame.init()

# Create a small window for testing
screen = pygame.display.set_mode((1600, 300))
pygame.display.set_caption("Debug Frame Analysis")

print("=== Frame Analysis Debug ===")

# Load the timeout sprite sheet
try:
    hdmi_timeout_image = pygame.image.load("assets/Items/hdmi-2.png").convert_alpha()
    print(f"Successfully loaded hdmi-2.png")
    print(f"Image size: {hdmi_timeout_image.get_size()}")
except pygame.error as e:
    print(f"Error loading hdmi-2.png: {e}")
    sys.exit(1)

# Sprite sheet parameters
timeout_frame_width = 320  # 1600/5 = 320px per frame
timeout_frame_height = 900  # Full height
timeout_frames = 5

print(f"Expected frame dimensions: {timeout_frame_width}x{timeout_frame_height}")
print(f"Expected frames: {timeout_frames}")

# Create display to show raw frames from the sprite sheet
running = True
current_raw_frame = 0
last_frame_time = pygame.time.get_ticks()
frame_display_time = 2000  # Show each frame for 2 seconds

clock = pygame.time.Clock()

while running and current_raw_frame < 5:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                current_raw_frame += 1
                if current_raw_frame >= 5:
                    running = False
    
    current_time = pygame.time.get_ticks()
    
    # Clear screen
    screen.fill((50, 50, 50))
    
    if current_raw_frame < 5:
        # Extract raw frame from sprite sheet (left to right, no reverse order)
        frame_rect = pygame.Rect(current_raw_frame * timeout_frame_width, 0, timeout_frame_width, timeout_frame_height)
        raw_frame_surface = pygame.Surface((timeout_frame_width, timeout_frame_height), pygame.SRCALPHA).convert_alpha()
        raw_frame_surface.blit(hdmi_timeout_image, (0, 0), frame_rect)
        
        # Scale down for display
        display_scale = 0.3
        display_width = int(timeout_frame_width * display_scale)
        display_height = int(timeout_frame_height * display_scale)
        scaled_frame = pygame.transform.scale(raw_frame_surface, (display_width, display_height))
        
        # Draw the frame
        frame_x = 50 + current_raw_frame * (display_width + 20)
        screen.blit(scaled_frame, (frame_x, 50))
        
        # Draw frame info
        font = pygame.font.Font(None, 36)
        text = font.render(f"Raw Frame {current_raw_frame}", True, (255, 255, 255))
        screen.blit(text, (10, 10))
        
        instruction_text = font.render("Press SPACE for next frame", True, (255, 255, 255))
        screen.blit(instruction_text, (10, 250))
        
        print(f"Displaying Raw Frame {current_raw_frame} from position x={current_raw_frame * timeout_frame_width}")
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
print("Raw frame analysis completed.")
print("Expected: Frame 0 should be WHITE (full time), Frame 4 should be RED (almost expired)")
print("If this is backwards, the sprite sheet frames are ordered opposite to what we expect.")
