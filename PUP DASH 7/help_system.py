import pygame

class HelpSystem:
    """Help system that shows tutorial overlay and manages help button"""
    
    def __init__(self, virtual_width, virtual_height):
        self.virtual_width = virtual_width
        self.virtual_height = virtual_height
        
        # Load help assets
        try:
            self.help_button = pygame.image.load("assets/Help/HelpB.png").convert_alpha()
            self.tutorial_overlay = pygame.image.load("assets/Help/Overall-Tut.png").convert_alpha()
        except pygame.error as e:
            print(f"Error loading help assets: {e}")
            # Create fallback rectangles if images fail to load
            self.help_button = pygame.Surface((50, 50))
            self.help_button.fill((100, 150, 255))  # Blue color
            self.tutorial_overlay = pygame.Surface((virtual_width, virtual_height))
            self.tutorial_overlay.fill((0, 0, 0, 180))  # Semi-transparent black
        
        # Scale tutorial overlay to fit screen
        self.tutorial_overlay = pygame.transform.scale(self.tutorial_overlay, (virtual_width, virtual_height))
        
        # Help button position (beside pause menu)
        button_margin = 20
        self.help_button_pos = (
            virtual_width - self.help_button.get_width() - button_margin - 60,  # 60px left of pause button
            button_margin
        )
        
        # Help button clickable area (slightly larger for easier clicking)
        button_padding = 10
        self.help_button_rect = pygame.Rect(
            self.help_button_pos[0] - button_padding,
            self.help_button_pos[1] - button_padding,
            self.help_button.get_width() + (button_padding * 2),
            self.help_button.get_height() + (button_padding * 2)
        )
        
        # State
        self.showing_tutorial = False
    
    def check_help_button_click(self, click_pos):
        """Check if the help button was clicked"""
        if self.help_button_rect.collidepoint(click_pos):
            self.showing_tutorial = True
            try:
                from music import pause_music
                pause_music()
                from music import pause_all_sfx
                pause_all_sfx()
            except Exception:
                pass
            return True
        return False

    def check_tutorial_click(self, click_pos):
        """Check if tutorial overlay was clicked (to close it)"""
        if self.showing_tutorial:
            self.showing_tutorial = False
            try:
                from music import unpause_music
                unpause_music()
                from music import unpause_all_sfx
                unpause_all_sfx()
            except Exception:
                pass
            return True
        return False
    
    def is_tutorial_showing(self):
        """Check if tutorial is currently being shown"""
        return self.showing_tutorial
    
    def hide_tutorial(self):
        """Hide the tutorial overlay"""
        self.showing_tutorial = False
    
    def draw_help_button(self, surface):
        """Draw the help button (when tutorial is not showing)"""
        if not self.showing_tutorial:
            surface.blit(self.help_button, self.help_button_pos)
    
    def draw_tutorial(self, surface, game_frame=None):
        """Draw the tutorial overlay with a blurred game background (when showing)"""
        if self.showing_tutorial:
            if game_frame is not None:
                # Blur the game frame only (not the tutorial)
                blur_scale = 0.25
                small = pygame.transform.smoothscale(game_frame, (int(self.virtual_width * blur_scale), int(self.virtual_height * blur_scale)))
                blurred = pygame.transform.smoothscale(small, (self.virtual_width, self.virtual_height))
                surface.blit(blurred, (0, 0))
            else:
                surface.fill((0, 0, 0))
            # Draw the tutorial overlay on top (not blurred)
            surface.blit(self.tutorial_overlay, (0, 0))
            # Draw close instruction text
            font = pygame.font.Font(None, 36)
            close_text = font.render("Click anywhere to close", True, (255, 255, 255))
            text_rect = close_text.get_rect(center=(self.virtual_width // 2, self.virtual_height - 50))
            surface.blit(close_text, text_rect)
