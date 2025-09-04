import pygame

class GameTimer:
    def __init__(self, duration_ms, font_path, font_size, timer_bg_path, pos=(40, 30)):
        self.duration = duration_ms
        self.start_time = pygame.time.get_ticks()
        self.font = pygame.font.Font(font_path, font_size)
        self.bg = pygame.image.load(timer_bg_path).convert_alpha()
        self.bg_rect = self.bg.get_rect()
        self.bg_rect.topleft = pos
        self.paused = False
        self.pause_time = 0
        self.total_paused = 0

    def pause(self):
        if not self.paused:
            self.paused = True
            self.pause_time = pygame.time.get_ticks()

    def resume(self):
        if self.paused:
            paused_duration = pygame.time.get_ticks() - self.pause_time
            self.total_paused += paused_duration
            self.paused = False

    def get_time_left(self):
        if self.paused:
            elapsed = self.pause_time - self.start_time - self.total_paused
        else:
            elapsed = pygame.time.get_ticks() - self.start_time - self.total_paused
        time_left = max(0, self.duration - elapsed)
        minutes = time_left // 60000
        seconds = (time_left % 60000) // 1000
        return minutes, seconds, time_left

    def draw(self, surface):
        minutes, seconds, _ = self.get_time_left()
        surface.blit(self.bg, self.bg_rect)
        timer_text = self.font.render(f"{minutes}:{seconds:02d}", True, (255, 231, 165))
        timer_text_rect = timer_text.get_rect(
            left=self.bg_rect.left + 45,
            centery=self.bg_rect.centery - 4
        )
        surface.blit(timer_text, timer_text_rect)

    def is_time_up(self):
        _, _, time_left = self.get_time_left()
        return time_left <= 0