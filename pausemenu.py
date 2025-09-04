import pygame
from music import play_menu_sfx, play_button_sfx

def darken_image(image, darkness=20):
    """Return a slightly darkened copy of an image."""
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

class PauseMenu:
    def __init__(self, virtual_width, virtual_height):
        self.virtual_width = virtual_width
        self.virtual_height = virtual_height
        self.active = False
        
        # Load pause menu assets
        try:
            # Settings button (gear icon)
            self.settings_button = pygame.image.load("assets//Pause Menu/Settings-btn.png").convert_alpha()
            
            # Resume and quit buttons (your wooden style buttons)
            self.resume_button_normal = pygame.image.load("assets//Pause Menu/Resume-btn.png").convert_alpha()
            self.quit_button_normal = pygame.image.load("assets//Pause Menu/Quit-btn.png").convert_alpha()
            
            # Create hover versions (only scaled down, no darkening)
            self.resume_button_hover = scale_down(self.resume_button_normal)
            self.quit_button_hover = scale_down(self.quit_button_normal)
            
        except pygame.error as e:
            print(f"Error loading pause menu images: {e}")
            # Create fallback buttons if images don't exist
            self.settings_button = pygame.Surface((60, 60))
            self.settings_button.fill((100, 100, 100))
            
            self.resume_button_normal = pygame.Surface((200, 80))
            self.resume_button_normal.fill((139, 69, 19))
            self.resume_button_hover = scale_down(self.resume_button_normal)
            
            self.quit_button_normal = pygame.Surface((200, 80))
            self.quit_button_normal.fill((139, 69, 19))
            self.quit_button_hover = scale_down(self.quit_button_normal)
        
        # Button positions
        self.settings_pos = (virtual_width - 80, 20)  # Upper right corner
        
        # Center the resume and quit buttons
        resume_x = (virtual_width - self.resume_button_normal.get_width()) // 2
        quit_x = (virtual_width - self.quit_button_normal.get_width()) // 2
        
        # Position buttons vertically centered with some spacing
        button_spacing = 20
        total_height = self.resume_button_normal.get_height() + self.quit_button_normal.get_height() + button_spacing
        start_y = (virtual_height - total_height) // 2
        
        self.resume_pos = (resume_x, start_y)
        self.quit_pos = (quit_x, start_y + self.resume_button_normal.get_height() + button_spacing)
        
        # Button rectangles for click detection
        self.settings_rect = pygame.Rect(self.settings_pos[0], self.settings_pos[1], 
                                       self.settings_button.get_width(), self.settings_button.get_height())
        self.resume_rect = pygame.Rect(self.resume_pos[0], self.resume_pos[1],
                                     self.resume_button_normal.get_width(), self.resume_button_normal.get_height())
        self.quit_rect = pygame.Rect(self.quit_pos[0], self.quit_pos[1],
                                   self.quit_button_normal.get_width(), self.quit_button_normal.get_height())
        
        # Hover state tracking
        self.resume_hovered = False
        self.quit_hovered = False
    
    def update_hover(self, mouse_pos):
        """Update hover states based on mouse position"""
        if self.active:
            self.resume_hovered = self.resume_rect.collidepoint(mouse_pos)
            self.quit_hovered = self.quit_rect.collidepoint(mouse_pos)
        else:
            self.resume_hovered = False
            self.quit_hovered = False

        # Semi-transparent overlay for pause effect
        self.overlay = pygame.Surface((self.virtual_width, self.virtual_height), pygame.SRCALPHA)
        self.overlay.fill((0, 0, 0, 120))  # RGBA, alpha controls darkness

    def draw(self, surface):
        # Always draw settings button
        self.draw_settings_button(surface)
        
        # Draw pause buttons only when active
        if self.active:
            # Draw dim overlay
            surface.blit(self.overlay, (0, 0))
            self.draw_pause_buttons(surface)
    
    def check_settings_click(self, mouse_pos):
        """Check if settings button was clicked"""
        if self.settings_rect.collidepoint(mouse_pos):
            play_menu_sfx()
            self.active = True
            return True
        return False
    
    def check_pause_menu_click(self, mouse_pos):
        """Check pause menu button clicks. Returns 'resume', 'quit', or None"""
        if not self.active:
            return None
            
        if self.resume_rect.collidepoint(mouse_pos):
            play_button_sfx()
            self.active = False
            return "resume"
        elif self.quit_rect.collidepoint(mouse_pos):
            play_button_sfx()
            return "quit"  # Use 'quit' for clarity
        # Example button logic (adjust as needed for your button layout)
        if hasattr(self, "resume_button_rect") and self.resume_button_rect.collidepoint(mouse_pos):
            return "resume"
        if hasattr(self, "quit_button_rect") and self.quit_button_rect.collidepoint(mouse_pos):
            return "quit"
        if hasattr(self, "go_to_title_screen_button_rect") and self.go_to_title_screen_button_rect.collidepoint(mouse_pos):
            return "go_to_title_screen"
        return None
    
    def draw_settings_button(self, surface):
        """Draw only the settings button (call this always)"""
        surface.blit(self.settings_button, self.settings_pos)
    
    def draw_pause_buttons(self, surface):
        """Draw the pause menu buttons (call this only when paused)"""
        if self.active:
            # Get current mouse position for hover detection
            mouse_pos = pygame.mouse.get_pos()
            # Convert to virtual coordinates
            screen_width, screen_height = pygame.display.get_surface().get_size()
            scale_x = self.virtual_width / screen_width
            scale_y = self.virtual_height / screen_height
            virtual_mouse_x = int(mouse_pos[0] * scale_x)
            virtual_mouse_y = int(mouse_pos[1] * scale_y)
            virtual_mouse_pos = (virtual_mouse_x, virtual_mouse_y)
            
            # Draw the resume button (scale down on hover)
            if self.resume_rect.collidepoint(virtual_mouse_pos):
                scaled_rect = self.resume_button_hover.get_rect(center=self.resume_rect.center)
                surface.blit(self.resume_button_hover, scaled_rect)
            else:
                surface.blit(self.resume_button_normal, self.resume_pos)
                
            # Draw the quit button (scale down on hover)
            if self.quit_rect.collidepoint(virtual_mouse_pos):
                scaled_rect = self.quit_button_hover.get_rect(center=self.quit_rect.center)
                surface.blit(self.quit_button_hover, scaled_rect)
            else:
                surface.blit(self.quit_button_normal, self.quit_pos)
    
    def draw(self, surface):
        """Draw the complete pause menu system"""
        # Always draw settings button
        self.draw_settings_button(surface)
        
        # Draw pause buttons only when active
        if self.active:
            self.draw_pause_buttons(surface)
    
    def is_paused(self):
        """Returns True if the game is currently paused"""
        return self.active
    
    def toggle_pause(self):
        """Toggle pause state"""
        self.active = not self.active
    
    def resume_game(self):
        """Resume the game"""
        self.active = False
    
    def pause_game(self):
        """Pause the game"""
        self.active = True
    
    def handle_keypress(self, key):
        """Handle keyboard input for pause menu"""
        if key == pygame.K_ESCAPE:
            if self.active:
                self.resume_game()
            else:
                self.pause_game()
            return True
        return False