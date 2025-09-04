import sys
import pygame
from music import play_button_sfx

def darken_image(image, darkness=40):
    dark_img = pygame.Surface(image.get_size(), flags=pygame.SRCALPHA)
    dark_img.fill((0, 0, 0, darkness))
    copy = image.copy()
    copy.blit(dark_img, (0, 0), special_flags=pygame.BLEND_RGBA_SUB)
    return copy

def scale_down(image, scale=0.95):
    w, h = image.get_size()
    new_size = (int(w * scale), int(h * scale))
    return pygame.transform.smoothscale(image, new_size)

def show_welcoming_screen(screen):
    sw, sh = screen.get_width(), screen.get_height()

    # Background
    background = pygame.image.load("assets/images/background.png")
    background = pygame.transform.scale(background, (sw, sh))

    # Welcoming Board
    welcoming_img = pygame.image.load("assets/Welcoming/Welcoming.png")
    welcoming_img = pygame.transform.scale(welcoming_img, (sw, sh))
    welcoming_rect = welcoming_img.get_rect(center=(sw // 2, sh // 2))

    # Go Back button
    go_back_img = pygame.image.load("assets/Welcoming/BGoBack.png")
    go_back_img = pygame.transform.scale(go_back_img, (int(sw * 0.10), int(sh * 0.06)))
    go_back_rect = go_back_img.get_rect(center=(sw // 2 - int(sw * 0.13), int(sh * 0.88)))
    go_back_hover = scale_down(darken_image(go_back_img))
    go_back_hover_rect = go_back_hover.get_rect(center=go_back_rect.center)

    # Let's Start button
    lets_start_img = pygame.image.load("assets/Welcoming/BLetsStart.png")
    lets_start_img = pygame.transform.scale(lets_start_img, (int(sw * 0.15), int(sh * 0.08)))
    lets_start_rect = lets_start_img.get_rect(center=(sw // 2 + int(sw * 0.1), int(sh * 0.68)))
    lets_start_hover = scale_down(darken_image(lets_start_img))
    lets_start_hover_rect = lets_start_hover.get_rect(center=lets_start_rect.center)

    while True:
        mouse_pos = pygame.mouse.get_pos()

        screen.blit(background, (0, 0))
        screen.blit(welcoming_img, welcoming_rect)

        # Hover logic for both buttons
        if go_back_rect.collidepoint(mouse_pos):
            screen.blit(go_back_hover, go_back_hover_rect)
        else:
            screen.blit(go_back_img, go_back_rect)

        if lets_start_rect.collidepoint(mouse_pos):
            screen.blit(lets_start_hover, lets_start_hover_rect)
        else:
            screen.blit(lets_start_img, lets_start_rect)

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                play_button_sfx()
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if go_back_rect.collidepoint(event.pos):
                    play_button_sfx()
                    return "back"
                elif lets_start_rect.collidepoint(event.pos):
                    play_button_sfx()
                    return "start"
