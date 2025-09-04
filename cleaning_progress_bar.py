import pygame

class CleaningProgressBar:
    def __init__(self, width=80, height=8):
        """
        Initialize the cleaning progress bar.
        
        Args:
            width: Width of the progress bar
            height: Height of the progress bar
        """
        self.width = width
        self.height = height
        self.active = False
        self.start_time = 0
        self.duration = 3000  # 3 seconds cleaning time
        self.position = (0, 0)
        
        # Colors
        self.bg_color = (60, 60, 60)  # Dark gray background
        self.border_color = (255, 255, 255)  # White border
        self.progress_colors = [
            (255, 100, 100),  # Red (start)
            (255, 150, 50),   # Orange
            (255, 200, 0),    # Yellow
            (150, 255, 50),   # Light green
            (50, 255, 50),    # Green (complete)
        ]
    
    def start_cleaning(self, door_position, current_time):
        """Start the progress bar above the specified door."""
        self.active = True
        self.start_time = current_time
        # Position progress bar above the door
        self.position = (door_position[0] - self.width // 2, 
                        door_position[1] - self.height - 15)
    
    def stop_cleaning(self):
        """Stop the progress bar."""
        self.active = False
        self.start_time = 0
    
    def get_progress(self, current_time):
        """Get the current cleaning progress as a percentage (0.0 to 1.0)."""
        if not self.active:
            return 0.0
        
        elapsed = current_time - self.start_time
        return min(elapsed / self.duration, 1.0)
    
    def is_complete(self, current_time):
        """Check if the cleaning is complete."""
        if not self.active:
            return False
        
        elapsed = current_time - self.start_time
        return elapsed >= self.duration
    
    def draw(self, surface, current_time):
        """Draw the progress bar on the surface."""
        if not self.active:
            return
        
        progress = self.get_progress(current_time)
        
        # Draw background
        bg_rect = pygame.Rect(self.position[0], self.position[1], self.width, self.height)
        pygame.draw.rect(surface, self.bg_color, bg_rect)
        pygame.draw.rect(surface, self.border_color, bg_rect, 1)
        
        # Draw progress
        if progress > 0:
            progress_width = int((self.width - 2) * progress)
            if progress_width > 0:
                # Choose color based on progress
                color_index = min(int(progress * len(self.progress_colors)), len(self.progress_colors) - 1)
                color = self.progress_colors[color_index]
                
                progress_rect = pygame.Rect(self.position[0] + 1, self.position[1] + 1, 
                                          progress_width, self.height - 2)
                pygame.draw.rect(surface, color, progress_rect)
        
        # Draw text showing time remaining
        if hasattr(self, '_font') or True:  # Create font if needed
            try:
                if not hasattr(self, '_font'):
                    self._font = pygame.font.Font(None, 16)
                
                remaining_time = max(0, self.duration - (current_time - self.start_time))
                seconds = (remaining_time // 1000) + 1  # Round up
                
                if seconds > 0:
                    text = self._font.render(f"{seconds}s", True, (255, 255, 255))
                    text_rect = text.get_rect(centerx=self.position[0] + self.width // 2,
                                            y=self.position[1] - 18)
                    surface.blit(text, text_rect)
            except:
                pass  # Skip text if font loading fails
