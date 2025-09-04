import pygame
import random
import spritesheet
from music import play_item_picked_sfx, play_item_dropped_sfx

class ItemRequestManager:
    """Manages HDMI and Remote requests from student groups"""
    
    def __init__(self):
        # Load item icons
        self.hdmi_icon = pygame.image.load("assets/Items/hdmi.png").convert_alpha()
        self.remote_icon = pygame.image.load("assets/Items/remote.png").convert_alpha()
        self.hdmi_pick = pygame.image.load("assets/Items/hdmi pick.png").convert_alpha()
        self.remote_pick = pygame.image.load("assets/Items/remote pick.png").convert_alpha()
        
        # Load trash bin icon
        self.trash_bin = pygame.image.load("assets/images/trash-bin.png").convert_alpha()
        self.trash_bin = pygame.transform.scale(self.trash_bin, (50, 50))  # Scale to appropriate size
        
        # Scale icons to same size as check icons (75x62 actual size)
        icon_size = (75, 62)
        self.hdmi_icon = pygame.transform.scale(self.hdmi_icon, icon_size)
        self.remote_icon = pygame.transform.scale(self.remote_icon, icon_size)
        
        # Pick up items (what Pio carries)
        pick_size = (45, 45)
        self.hdmi_pick = pygame.transform.scale(self.hdmi_pick, pick_size)
        self.remote_pick = pygame.transform.scale(self.remote_pick, pick_size)
        
        # Load timeout sprite sheets for animation
        try:
            hdmi_timeout_image = pygame.image.load("assets/Items/hdmi-2.png").convert_alpha()
            remote_timeout_image = pygame.image.load("assets/Items/remote-2.png").convert_alpha()
            print("Successfully loaded timeout sprite sheets")
        except pygame.error as e:
            print(f"Error loading timeout sprite sheets: {e}")
            # Fallback to regular icons
            hdmi_timeout_image = self.hdmi_icon
            remote_timeout_image = self.remote_icon
        
        # Create sprite sheet objects for timeout animations
        self.hdmi_timeout_sheet = spritesheet.SpriteSheet(hdmi_timeout_image)
        self.remote_timeout_sheet = spritesheet.SpriteSheet(remote_timeout_image)
        
        # Sprite sheet parameters (1600x900 sprite sheets, horizontal layout with proper cropping)
        self.timeout_frame_width = 320  # 1600/5 = 320px per frame
        self.timeout_frame_height = 900  # Full height
        self.timeout_frames = 5  # Number of frames in the sprite sheet
        self.timeout_scale = 0.2  # Slightly smaller scale for better fit (320*0.2 = 64px)
        
        # Pre-load all frames for both HDMI and remote timeout animations
        self.hdmi_timeout_frames = []
        self.remote_timeout_frames = []
        
        try:
            # Load frames in natural left-to-right order from sprite sheet
            # Frame 0 = white/empty (full time remaining)
            # Frame 1 = 1/4 red
            # Frame 2 = 1/2 red  
            # Frame 3 = 3/4 red
            # Frame 4 = full red (almost expired)
            for i in range(self.timeout_frames):
                # Extract HDMI frame manually with pixel-perfect cropping
                hdmi_rect = pygame.Rect(i * self.timeout_frame_width, 0, self.timeout_frame_width, self.timeout_frame_height)
                hdmi_frame_surface = pygame.Surface((self.timeout_frame_width, self.timeout_frame_height), pygame.SRCALPHA).convert_alpha()
                hdmi_frame_surface.blit(hdmi_timeout_image, (0, 0), hdmi_rect)
                
                # Scale after extraction to ensure pixel-perfect cropping
                if self.timeout_scale != 1:
                    scaled_width = int(self.timeout_frame_width * self.timeout_scale)
                    scaled_height = int(self.timeout_frame_height * self.timeout_scale)
                    hdmi_frame_surface = pygame.transform.scale(hdmi_frame_surface, (scaled_width, scaled_height))
                
                self.hdmi_timeout_frames.append(hdmi_frame_surface)
                
                # Extract Remote frame manually with pixel-perfect cropping
                remote_rect = pygame.Rect(i * self.timeout_frame_width, 0, self.timeout_frame_width, self.timeout_frame_height)
                remote_frame_surface = pygame.Surface((self.timeout_frame_width, self.timeout_frame_height), pygame.SRCALPHA).convert_alpha()
                remote_frame_surface.blit(remote_timeout_image, (0, 0), remote_rect)
                
                # Scale after extraction to ensure pixel-perfect cropping
                if self.timeout_scale != 1:
                    scaled_width = int(self.timeout_frame_width * self.timeout_scale)
                    scaled_height = int(self.timeout_frame_height * self.timeout_scale)
                    remote_frame_surface = pygame.transform.scale(remote_frame_surface, (scaled_width, scaled_height))
                    
                self.remote_timeout_frames.append(remote_frame_surface)
            
            print(f"Successfully loaded {self.timeout_frames} frames for each timeout animation (natural left-to-right order)")
        except Exception as e:
            print(f"Error loading sprite frames: {e}")
            # Fallback to single frames
            self.hdmi_timeout_frames = [self.hdmi_icon] * self.timeout_frames
            self.remote_timeout_frames = [self.remote_icon] * self.timeout_frames
        
        # Request tracking
        self.active_requests = {}  # {group_id: {"type": "hdmi"/"remote", "position": (x, y)}}
        
        # Door positions for request icons (same as checkpopup positions)
        self.door_positions = {
            "door1": (207, 470),
            "door2": (370, 470),
            "door3": (1082, 470),
            "door4": (1243, 470)
        }
        
        # Storage room locations - inside the ground floor rooms
        # Remote room = right-center ground floor room (near door3)
        # HDMI room = rightmost ground floor room (near door4)
        self.storage_rooms = {
            "remote_room": {"position": (1110, 725), "door": "door3", "has_item": True},  # Right-center room
            "hdmi_room": {"position": (1275, 725), "door": "door4", "has_item": True}     # Rightmost room
        }
        
        # Trash bin location - between HDMI and Remote rooms
        self.trash_bin_position = (1192, 780)  # Between the two storage rooms
        
        # Penalty tracking for unfulfilled requests
        self.pending_penalties = []
    
    def create_request(self, group):
        """Create a random item request for a student group"""
        request_type = random.choice(["hdmi", "remote"])
        group_id = id(group)
        current_time = pygame.time.get_ticks()
        
        print(f"Creating {request_type} request for group {group_id}")
        
        # Get the door position for the group's target door
        door_name = getattr(group, 'target_door_name', None)
        print(f"Group door: {door_name}")
        
        if door_name and door_name in self.door_positions:
            # Position the request icon at the door position (same as checkpopup)
            door_pos = self.door_positions[door_name]
            request_position = (door_pos[0], door_pos[1])
            print(f"Using door position: {request_position}")
        else:
            # Fallback: position above the group if no door assigned
            request_position = (group.x - 37, group.y - 70)
            print(f"Using fallback position: {request_position}")
        
        self.active_requests[group_id] = {
            "type": request_type,
            "position": request_position,
            "group": group,
            "fulfilled": False,
            "start_time": current_time,
            "duration": 20000,  # 20 seconds timeout (longer to see the animation)
            "door_name": door_name  # Store which door this request is for
        }
        
        # Set the request on the group
        group.item_request = request_type
        group.request_fulfilled = False
        
        print(f"Request created! Active requests: {len(self.active_requests)}")
        
        return request_type
    
    def remove_request(self, group):
        """Remove a request when fulfilled or group leaves"""
        group_id = id(group)
        if group_id in self.active_requests:
            del self.active_requests[group_id]
        
        if hasattr(group, 'item_request'):
            group.item_request = None
            group.request_fulfilled = True
    
    def get_storage_room_for_item(self, item_type):
        """Get the storage room location for an item type"""
        if item_type == "remote":
            return "remote_room", self.storage_rooms["remote_room"]["position"]
        elif item_type == "hdmi":
            return "hdmi_room", self.storage_rooms["hdmi_room"]["position"]
        return None, None
    
    def check_storage_room_click(self, click_pos):
        """Check if a storage room was clicked"""
        for room_name, room_data in self.storage_rooms.items():
            room_pos = room_data["position"]
            # Increased clickable area - 150px radius around the storage room
            click_radius = 150
            room_center_x = room_pos[0] + 22  # Center of 45x45 icon
            room_center_y = room_pos[1] + 22
            
            distance_x = click_pos[0] - room_center_x
            distance_y = click_pos[1] - room_center_y
            if abs(distance_x) <= click_radius and abs(distance_y) <= click_radius and room_data["has_item"]:
                return room_name
        return None
    
    def check_trash_bin_click(self, click_pos):
        """Check if the trash bin was clicked"""
        # Increased clickable area - 120px radius around the trash bin
        click_radius = 120
        trash_center_x = self.trash_bin_position[0] + 25  # Center of 50x50 icon
        trash_center_y = self.trash_bin_position[1] + 25
        
        distance_x = click_pos[0] - trash_center_x
        distance_y = click_pos[1] - trash_center_y
        return abs(distance_x) <= click_radius and abs(distance_y) <= click_radius
    
    def pickup_item(self, room_name):
        """Pick up an item from storage room"""
        if room_name in self.storage_rooms:
            if room_name == "remote_room":
                item_type = "remote"
                try:
                    play_item_picked_sfx()
                except Exception as e:
                    print(f"SFX error: {e}")
            elif room_name == "hdmi_room":
                item_type = "hdmi"
                try:
                    play_item_picked_sfx()
                except Exception as e:
                    print(f"SFX error: {e}")
            else:
                return None
                
            # Don't remove the item from storage - it stays available
            # self.storage_rooms[room_name]["has_item"] = False  # Commented out
            return item_type
        return None
    
    def restock_room(self, room_name):
        """Restock a storage room"""
        if room_name in self.storage_rooms:
            self.storage_rooms[room_name]["has_item"] = True
    
    def update_requests(self, current_time):
        """Update requests and remove expired ones"""
        expired_requests = []
        
        for group_id, request_data in self.active_requests.items():
            elapsed_time = current_time - request_data["start_time"]
            
            if elapsed_time >= request_data["duration"]:
                # Request has expired
                expired_requests.append(group_id)
                # Clear the request from the group
                group = request_data["group"]
                if hasattr(group, 'item_request'):
                    group.item_request = None
                    group.request_fulfilled = True
                    
                # PENALTY: Deduct 20 points for unfulfilled request
                print(f"Request expired! Deducting 20 points for unfulfilled {request_data['type']} request")
                # We'll return the penalty info so the main game can deduct points
                self.pending_penalties.append(10)  # 10 point penalty
        
        # Remove expired requests
        for group_id in expired_requests:
            del self.active_requests[group_id]
    
    def get_and_clear_penalties(self):
        """Get any pending penalties and clear them"""
        total_penalty = sum(self.pending_penalties)
        self.pending_penalties.clear()
        return total_penalty
    
    def draw_requests(self, surface, current_time=None):
        """Draw all active item requests with animated timeout sprites"""
        if current_time is None:
            current_time = pygame.time.get_ticks()
        
        for group_id, request_data in self.active_requests.items():
            if not request_data["fulfilled"]:
                # Calculate progress (remaining time as percentage)
                elapsed_time = current_time - request_data["start_time"]
                progress = max(0, 1 - (elapsed_time / request_data["duration"]))
                
                # Choose the appropriate sprite frames based on request type
                if request_data["type"] == "hdmi":
                    timeout_frames = self.hdmi_timeout_frames
                else:
                    timeout_frames = self.remote_timeout_frames
                
                # Calculate which frame to show based on time remaining (progress)
                # progress = 1.0 = full time remaining (frame 0 = white)
                # progress = 0.0 = no time remaining (frame 4 = red)
                # We want smooth progression: white -> quarter-red -> half-red -> three-quarter-red -> full-red
                frame_index = min(self.timeout_frames - 1, int((1 - progress) * self.timeout_frames))
                
                # Ensure we don't exceed bounds
                frame_index = max(0, min(frame_index, len(timeout_frames) - 1))
                
                # Draw the animated timeout sprite
                icon_pos = request_data["position"]
                timeout_frame = timeout_frames[frame_index]
                surface.blit(timeout_frame, icon_pos)
                
                # Only print debug info occasionally
                if elapsed_time % 2000 < 50:  # Print every 2 seconds
                    print(f"Drew {request_data['type']} request at {icon_pos}, frame {frame_index}, progress {progress:.2f}")
    
    def draw_storage_rooms(self, surface):
        """Draw HDMI and Remote pick icons in their respective rooms"""
        for room_name, room_data in self.storage_rooms.items():
            if room_data["has_item"]:  # Only draw if item is available
                pos = room_data["position"]
                
                if room_name == "hdmi_room":
                    icon = self.hdmi_pick  # Use hdmi pick icon
                elif room_name == "remote_room":
                    icon = self.remote_pick  # Use remote pick icon
                else:
                    continue
                
                # Draw the pick icon at the storage room position
                surface.blit(icon, pos)
    
    def draw_trash_bin(self, surface):
        """Draw the trash bin (call this early in draw order so it appears behind characters)"""
        surface.blit(self.trash_bin, self.trash_bin_position)
    
    def update_request_positions(self):
        """Update request icon positions (now fixed at door positions)"""
        for group_id, request_data in list(self.active_requests.items()):
            group = request_data["group"]
            door_name = request_data.get("door_name")
            
            # Check if group still exists and is in the same room
            if hasattr(group, 'state') and group.state == "in_room" and door_name:
                # Keep the door position - no update needed since doors are fixed
                pass
            else:
                # Group no longer exists or left the room, remove request
                del self.active_requests[group_id]
    
    def check_request_click(self, click_pos, pio_carrying_item):
        """Check if an item request bubble was clicked and return the matching group"""
        for group_id, request_data in self.active_requests.items():
            if request_data["type"] == pio_carrying_item:
                request_pos = request_data["position"]
                # Increased clickable area around the request bubble (75x62 icon)
                click_radius = 80
                request_center_x = request_pos[0] + 37  # Center of 75x62 icon
                request_center_y = request_pos[1] + 31
                
                distance_x = click_pos[0] - request_center_x
                distance_y = click_pos[1] - request_center_y
                if abs(distance_x) <= click_radius and abs(distance_y) <= click_radius:
                    # Find the group with this ID
                    return group_id
        return None
