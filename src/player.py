"""Player class for first-person movement"""

import math
from src.constants import *

class Player:
    """Player with position and rotation"""
    
    def __init__(self, x, y, angle=0):
        """Initialize player at position with angle"""
        self.x = x
        self.y = y
        self.angle = angle
        
    def move(self, dungeon_map, forward=0, strafe=0):
        """Move player forward/back and strafe left/right"""
        # Calculate movement direction
        dx = math.cos(self.angle) * forward + math.cos(self.angle + math.pi/2) * strafe
        dy = math.sin(self.angle) * forward + math.sin(self.angle + math.pi/2) * strafe
        
        # New position
        new_x = self.x + dx * PLAYER_SPEED
        new_y = self.y + dy * PLAYER_SPEED
        
        # Check collision with walls
        if not dungeon_map.is_wall(new_x, self.y):
            self.x = new_x
        if not dungeon_map.is_wall(self.x, new_y):
            self.y = new_y
    
    def rotate(self, angle_delta):
        """Rotate player view"""
        self.angle += angle_delta
        # Keep angle in range [0, 2π]
        self.angle %= (2 * math.pi)
