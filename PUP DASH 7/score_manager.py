import pygame
import random
from music import play_points_plus_sfx, play_points_minus_sfx

class ScoreManager:
    def __init__(self, scoreboard):
        self.scoreboard = scoreboard
        
        # Penalty amounts (centralized here)
        self.ITEM_REQUEST_PENALTY = 5  # Points lost for unfulfilled item requests
        self.STUDENT_LEAVING_PENALTY = 10  # Points lost when students leave without entering rooms
        
        # Point rewards
        self.ITEM_DELIVERY_REWARD = 30  # Points gained for successful item delivery
        self.ROOM_EXIT_POINTS_MIN = 15  # Minimum points for room exit
        self.ROOM_EXIT_POINTS_MAX = 25  # Maximum points for room exit
    
    def add_points(self, points, reason=""):
        """Add points to the score"""
        self.scoreboard.add_points(points)
        play_points_plus_sfx()  # Play sound effect for gaining points
        if reason:
            print(f"Added {points} points: {reason}")
    
    def minus_points(self, points, reason=""):
        """Subtract points from the score"""
        self.scoreboard.minus_points(points)
        play_points_minus_sfx()  # Play sound effect for losing points
        if reason:
            print(f"Lost {points} points: {reason}")
    
    def apply_item_request_penalty(self, group=None):
        """Apply penalty for unfulfilled item requests, with floating text if group provided"""
        self.minus_points(
            self.ITEM_REQUEST_PENALTY, 
            "unfulfilled item request"
        )
        # Show floating -5 text at the group's door if group is provided
        if group is not None and hasattr(group, 'target_door_name'):
            try:
                # Add a floating point animation for penalty
                self.scoreboard._add_floating_point(self.ITEM_REQUEST_PENALTY, is_positive=False)
            except Exception as e:
                print(f"Could not show penalty floating text: {e}")
        return self.ITEM_REQUEST_PENALTY
    
    def apply_student_leaving_penalty(self, reason="student group left without entering room"):
        """Apply penalty when students leave without entering rooms"""
        self.minus_points(
            self.STUDENT_LEAVING_PENALTY, 
            reason
        )
        return self.STUDENT_LEAVING_PENALTY
    
    def reward_item_delivery(self):
        """Give points for successful item delivery"""
        self.add_points(
            self.ITEM_DELIVERY_REWARD, 
            "successful item delivery"
        )
        return self.ITEM_DELIVERY_REWARD
    
    def reward_room_exit(self, group_name="StudentGroup"):
        """Give random points when a group exits a room"""
        points = random.randint(self.ROOM_EXIT_POINTS_MIN, self.ROOM_EXIT_POINTS_MAX)
        self.add_points(
            points, 
            f"{group_name} completed room visit"
        )
        return points
    
    def get_current_score(self):
        """Get the current score"""
        return self.scoreboard.score if hasattr(self.scoreboard, 'score') else 0
