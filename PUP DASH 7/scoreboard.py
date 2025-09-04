import random
import pygame.font
from music import play_score_sfx

class Scoreboard:
    """A class to report scoring information and handle random point earning."""

    def __init__(self, ai_game):
        """Initialize scorekeeping attributes."""
        self.ai_game = ai_game
        self.screen = ai_game.screen
        self.screen_rect = self.screen.get_rect()
        self.settings = ai_game.settings
        self.stats = ai_game.stats

        # Font settings for scoring information
        self.text_color = (255, 231, 165)
        self.font = pygame.font.Font("assets/Space_Mono/SpaceMono-Bold.ttf", 50)
        
        # Font for floating point animations
        self.point_font = pygame.font.Font("assets/Space_Mono/SpaceMono-Bold.ttf", 32)
        
        # List to store active point animations
        self.floating_points = []
        
        # Load scoreboard background image
        self.bg_image = pygame.image.load("assets/images/scoreboard-bg.png").convert_alpha()
        self.bg_rect = self.bg_image.get_rect()
        # Center the scoreboard in the screen
        self.bg_rect.centerx = self.screen_rect.centerx - 30
        self.bg_rect.top = 20

        self.prep_score()

    def prep_score(self):
        """Render the current score as an image."""
        score_str = f"{self.stats.score:,}"
        self.score_image = self.font.render(score_str, True, self.text_color)
        self.score_rect = self.score_image.get_rect(center=self.bg_rect.center)
        self.score_rect.top = 25
        # Position the score numbers with more right spacing within the centered area
        self.score_rect.centerx = self.bg_rect.centerx + 40  # More right spacing for better readability

    def add_random_points_on_exit(self, studentgroup):
        """Add random points (30-40) when a student group exits a room."""
        points = random.randint(15, 25)
        studentgroup.score = getattr(studentgroup, 'score', 0) + points
        self.stats.score += points
        self.prep_score()  
        play_score_sfx()
        
        # Add floating point animation for positive points
        self._add_floating_point(points, is_positive=True)
        
        return points

    def minus_points(self, points):
        """Subtract points from the score, but not below zero."""
        self.stats.score = max(0, self.stats.score - points)
        self.prep_score()
        
        # Add floating point animation for negative points
        self._add_floating_point(points, is_positive=False)

    def add_points(self, points):
        """Add points to the score (for item delivery, etc.)."""
        self.stats.score += points
        self.prep_score()
        
        # Add floating point animation for positive points
        self._add_floating_point(points, is_positive=True)

    def _add_floating_point(self, points, is_positive=True):
        """Add a floating point animation."""
        current_time = pygame.time.get_ticks()
        
        # Position the floating text to the right of the scoreboard
        start_x = self.bg_rect.right + 20
        start_y = self.bg_rect.centery
        
        # Check for existing active floating points and offset vertically to avoid overlap
        active_floating_points = [fp for fp in self.floating_points 
                                 if current_time - fp['start_time'] < fp['duration']]
        
        # Offset by 30 pixels for each existing floating point to ensure no overlap
        vertical_offset = len(active_floating_points) * 30
        start_y = start_y + vertical_offset
        
        # Create the floating point data
        floating_point = {
            'points': points,
            'is_positive': is_positive,
            'x': start_x,
            'y': start_y,
            'start_time': current_time,
            'duration': 2000,  # 2 seconds
            'start_y': start_y
        }
        
        self.floating_points.append(floating_point)

    def update_floating_points(self, current_time):
        """Update and remove expired floating point animations."""
        # Remove expired animations
        self.floating_points = [fp for fp in self.floating_points 
                               if current_time - fp['start_time'] < fp['duration']]
        
        # Update positions for remaining animations
        for fp in self.floating_points:
            elapsed = current_time - fp['start_time']
            progress = elapsed / fp['duration']
            
            # Move upward and fade out
            fp['y'] = fp['start_y'] - (progress * 60)  # Move up 60 pixels over duration
            fp['alpha'] = max(0, 255 * (1 - progress))  # Fade out

    def draw_floating_points(self):
        """Draw all active floating point animations."""
        for fp in self.floating_points:
            # Choose color based on positive/negative
            if fp['is_positive']:
                color = (0, 255, 0)  # Green for positive
                text = f"+{fp['points']}"
            else:
                color = (255, 0, 0)  # Red for negative
                text = f"-{fp['points']}"
            
            # Render the text
            point_surface = self.point_font.render(text, True, color)
            
            # Apply alpha for fade effect
            if fp['alpha'] < 255:
                point_surface.set_alpha(int(fp['alpha']))
            
            # Draw the floating point
            point_rect = point_surface.get_rect()
            point_rect.x = fp['x']
            point_rect.y = fp['y']
            self.screen.blit(point_surface, point_rect)

    def show_score(self):
        """Draw the score to the screen."""
        self.screen.blit(self.bg_image, self.bg_rect)
        self.screen.blit(self.score_image, self.score_rect)
        
        # Draw floating point animations
        self.draw_floating_points()