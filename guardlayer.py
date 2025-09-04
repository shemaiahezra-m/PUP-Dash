import pygame

class GuardLayer:
    def __init__(self, x, y, sheet, frame_width, frame_height, scale, animation_steps, animation_cooldown):
        self.frames = [
            sheet.get_image(i, frame_width, frame_height, scale, None)
            for i in range(animation_steps)
        ]
        self.x = x
        self.y = y
        self.frame = 0
        self.last_update = pygame.time.get_ticks()
        self.animation_cooldown = animation_cooldown
        self.animation_steps = animation_steps

    def update(self, current_time):
        if current_time - self.last_update > self.animation_cooldown:
            self.frame = (self.frame + 1) % self.animation_steps
            self.last_update = current_time

    def draw(self, surface):
        surface.blit(self.frames[self.frame], (self.x, self.y))