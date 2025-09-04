import pygame
import sys
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

def show_gameover_screen(screen, score, high_score):
    screen_rect = screen.get_rect()
    
    try:
        background = pygame.image.load("assets/images/background.png")
        background = pygame.transform.scale(background, screen.get_size())
    except Exception as e:
        background = pygame.Surface(screen.get_size())
        background.fill((50, 100, 150))
    
    bg = pygame.image.load("assets/Gameover/Gameover-bg.png").convert_alpha()
    play_btn = pygame.image.load("assets/Gameover/Playagain-btn.png").convert_alpha()
    play_btn = pygame.transform.smoothscale(play_btn, (250, 80))
    play_btn_hover = scale_down(darken_image(play_btn))

    bg_rect = bg.get_rect(center=screen_rect.center)
    play_btn_rect = play_btn.get_rect()
    play_btn_rect.center = (bg_rect.centerx, bg_rect.bottom - 180)
    play_btn_hover_rect = play_btn_hover.get_rect(center=play_btn_rect.center)

    font_path = "assets/Space_Mono/SpaceMono-Bold.ttf"
    score_font = pygame.font.Font(font_path, 72)

    while True:
        mouse_pos = pygame.mouse.get_pos()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                play_button_sfx()
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if play_btn_rect.collidepoint(event.pos):
                    play_button_sfx()
                    return "play_again"

        screen.blit(background, (0, 0))
        screen.blit(bg, bg_rect)
        
        if play_btn_rect.collidepoint(mouse_pos):
            screen.blit(play_btn_hover, play_btn_hover_rect)
        else:
            screen.blit(play_btn, play_btn_rect)

        # Render texts
        score_text = score_font.render(f"{score}", True, (253, 221, 132))
        high_score_text = score_font.render(f"{high_score}", True, (253, 221, 132))

        # Fixed left indent positions
        score_x = bg_rect.centerx + 90
        score_y = bg_rect.centery - 110
        high_score_x = bg_rect.centerx + 90
        high_score_y = bg_rect.centery + 20

        # Blit score and high score texts (LEFT-aligned to given coords)
        screen.blit(score_text, (score_x, score_y))
        screen.blit(high_score_text, (high_score_x, high_score_y))

        pygame.display.flip()
