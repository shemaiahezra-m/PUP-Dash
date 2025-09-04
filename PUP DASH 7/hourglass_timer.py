import pygame

class HourglassTimer:
    def __init__(self, spritesheet_path=None, frame_width=32, frame_height=32, total_frames=8):
        """
        Initialize the hourglass timer with spritesheet animation for students in rooms.
        
        Args:
            spritesheet_path: Path to the hourglass spritesheet (if None, uses placeholder)
            frame_width: Width of each frame in the spritesheet
            frame_height: Height of each frame in the spritesheet
            total_frames: Total number of frames in the animation
        """
        self.frame_width = frame_width
        self.frame_height = frame_height
        self.total_frames = total_frames
        self.current_frame = 0
        self.animation_speed = 200  # milliseconds per frame (slower for room usage)
        self.last_frame_time = 0
        
        # Load spritesheet or create placeholder
        if spritesheet_path:
            try:
                self.spritesheet = pygame.image.load(spritesheet_path).convert_alpha()
                self.frames = self._extract_frames()
            except:
                self.frames = self._create_placeholder_frames()
        else:
            self.frames = self._create_placeholder_frames()
        
        # Timer properties for room usage
        self.active_timers = {}  # Dictionary to track multiple doors: {door_name: {start_time, duration, position}}
        self.default_duration = 15000  # 15 seconds default room usage time
    
    def _extract_frames(self):
        """Extract individual frames from the spritesheet."""
        frames = []
        for i in range(self.total_frames):
            frame = pygame.Surface((self.frame_width, self.frame_height), pygame.SRCALPHA)
            frame.blit(self.spritesheet, (0, 0), 
                      (i * self.frame_width, 0, self.frame_width, self.frame_height))
            frames.append(frame)
        return frames
    
    def _create_placeholder_frames(self):
        """Create placeholder hourglass frames if no spritesheet is provided."""
        frames = []
        colors = [
            (255, 215, 0),    # Gold
            (255, 200, 0),    # Slightly darker gold
            (255, 185, 0),    # Even darker
            (255, 170, 0),    # More sand color
            (218, 165, 32),   # Goldenrod
            (184, 134, 11),   # Dark goldenrod
            (160, 115, 8),    # Darker
            (139, 100, 7),    # Darkest
        ]
        
        for i, color in enumerate(colors):
            frame = pygame.Surface((self.frame_width, self.frame_height), pygame.SRCALPHA)
            
            # Draw hourglass outline
            pygame.draw.polygon(frame, (101, 67, 33), [
                (8, 4), (24, 4), (24, 8), (20, 12), (20, 20), (24, 24), (24, 28),
                (8, 28), (8, 24), (12, 20), (12, 12), (8, 8)
            ])
            
            # Draw sand based on progress
            sand_level = (i + 1) / len(colors)
            bottom_sand_height = int(12 * sand_level)
            top_sand_height = int(12 * (1 - sand_level))
            
            # Bottom sand
            if bottom_sand_height > 0:
                pygame.draw.rect(frame, color, 
                               (12, 28 - bottom_sand_height, 8, bottom_sand_height))
            
            # Top sand
            if top_sand_height > 0:
                pygame.draw.rect(frame, color, 
                               (12, 4, 8, top_sand_height))
            
            # Falling sand stream (middle frames)
            if 2 <= i <= 5:
                pygame.draw.rect(frame, color, (15, 14, 2, 4))
            
            frames.append(frame)
        
        return frames
    
    def start_room_usage(self, door_name, door_position, current_time, duration=None):
        """Start the hourglass timer above the specified door for room usage."""
        if duration is None:
            duration = self.default_duration
        
        # Position hourglass above the door
        position = (door_position[0] - self.frame_width // 2, 
                   door_position[1] - self.frame_height - 10)
        
        self.active_timers[door_name] = {
            'start_time': current_time,
            'duration': duration,
            'position': position
        }
    
    def stop_room_usage(self, door_name):
        """Stop the hourglass timer for a specific door."""
        if door_name in self.active_timers:
            del self.active_timers[door_name]
    
    def stop_all_timers(self):
        """Stop all hourglass timers."""
        self.active_timers.clear()
    
    def update(self, current_time):
        """Update the hourglass animation for all active timers."""
        if not self.active_timers:
            return
        
        # Update animation frame
        if current_time - self.last_frame_time >= self.animation_speed:
            self.last_frame_time = current_time
            
            # Update frames for each active timer based on their individual progress
            for door_name, timer_data in list(self.active_timers.items()):
                elapsed = current_time - timer_data['start_time']
                progress = min(elapsed / timer_data['duration'], 1.0)
                target_frame = int(progress * (self.total_frames - 1))
                
                # Store individual frame for this timer
                timer_data['current_frame'] = target_frame
                
                # Remove completed timers
                if progress >= 1.0:
                    del self.active_timers[door_name]
    
    def draw(self, surface):
        """Draw all active hourglass timers on the surface."""
        for door_name, timer_data in self.active_timers.items():
            frame_index = timer_data.get('current_frame', 0)
            if frame_index < len(self.frames):
                surface.blit(self.frames[frame_index], timer_data['position'])
    
    def get_progress(self, door_name, current_time):
        """Get the current room usage progress for a specific door as a percentage (0.0 to 1.0)."""
        if door_name not in self.active_timers:
            return 0.0
        
        timer_data = self.active_timers[door_name]
        elapsed = current_time - timer_data['start_time']
        return min(elapsed / timer_data['duration'], 1.0)
    
    def is_complete(self, door_name, current_time):
        """Check if the room usage timer is complete for a specific door."""
        if door_name not in self.active_timers:
            return False
        
        timer_data = self.active_timers[door_name]
        elapsed = current_time - timer_data['start_time']
        return elapsed >= timer_data['duration']
    
    def is_active(self, door_name):
        """Check if there's an active timer for a specific door."""
        return door_name in self.active_timers
