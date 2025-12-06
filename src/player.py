"""Player class for tile-based movement"""

import math
from src.constants import *

class Player:
    """Player with grid position and facing direction"""
    
    def __init__(self, grid_x, grid_y, facing=0):
        """Initialize player at grid position with facing direction
        facing: 0=North, 1=East, 2=South, 3=West"""
        self.grid_x = grid_x
        self.grid_y = grid_y
        self.facing = facing
        
        # Smooth animation
        self.x = grid_x * TILE_SIZE + TILE_SIZE // 2
        self.y = grid_y * TILE_SIZE + TILE_SIZE // 2
        # Fix angle: North=up=-90°, East=0°, South=90°, West=180°
        angle_map = [-math.pi/2, 0, math.pi/2, math.pi]
        self.angle = angle_map[self.facing]
        
    def try_move_forward(self, dungeon_map):
        """Try to move one tile forward"""
        new_x, new_y = self.grid_x, self.grid_y
        
        if self.facing == 0:  # North
            new_y -= 1
        elif self.facing == 1:  # East
            new_x += 1
        elif self.facing == 2:  # South
            new_y += 1
        elif self.facing == 3:  # West
            new_x -= 1
            
        if not dungeon_map.is_wall_grid(new_x, new_y):
            self.grid_x = new_x
            self.grid_y = new_y
            self.x = self.grid_x * TILE_SIZE + TILE_SIZE // 2
            self.y = self.grid_y * TILE_SIZE + TILE_SIZE // 2
            return True
        return False
    
    def try_move_backward(self, dungeon_map):
        """Try to move one tile backward"""
        new_x, new_y = self.grid_x, self.grid_y
        
        if self.facing == 0:  # North - move South
            new_y += 1
        elif self.facing == 1:  # East - move West
            new_x -= 1
        elif self.facing == 2:  # South - move North
            new_y -= 1
        elif self.facing == 3:  # West - move East
            new_x += 1
            
        if not dungeon_map.is_wall_grid(new_x, new_y):
            self.grid_x = new_x
            self.grid_y = new_y
            self.x = self.grid_x * TILE_SIZE + TILE_SIZE // 2
            self.y = self.grid_y * TILE_SIZE + TILE_SIZE // 2
            return True
        return False
    
    def try_strafe_left(self, dungeon_map):
        """Try to strafe one tile left"""
        new_x, new_y = self.grid_x, self.grid_y
        
        if self.facing == 0:  # North - move West
            new_x -= 1
        elif self.facing == 1:  # East - move North
            new_y -= 1
        elif self.facing == 2:  # South - move East
            new_x += 1
        elif self.facing == 3:  # West - move South
            new_y += 1
            
        if not dungeon_map.is_wall_grid(new_x, new_y):
            self.grid_x = new_x
            self.grid_y = new_y
            self.x = self.grid_x * TILE_SIZE + TILE_SIZE // 2
            self.y = self.grid_y * TILE_SIZE + TILE_SIZE // 2
            return True
        return False
    
    def try_strafe_right(self, dungeon_map):
        """Try to strafe one tile right"""
        new_x, new_y = self.grid_x, self.grid_y
        
        if self.facing == 0:  # North - move East
            new_x += 1
        elif self.facing == 1:  # East - move South
            new_y += 1
        elif self.facing == 2:  # South - move West
            new_x -= 1
        elif self.facing == 3:  # West - move North
            new_y -= 1
            
        if not dungeon_map.is_wall_grid(new_x, new_y):
            self.grid_x = new_x
            self.grid_y = new_y
            self.x = self.grid_x * TILE_SIZE + TILE_SIZE // 2
            self.y = self.grid_y * TILE_SIZE + TILE_SIZE // 2
            return True
        return False
    
    def turn_left(self):
        """Turn 90 degrees left"""
        self.facing = (self.facing - 1) % 4
        angle_map = [-math.pi/2, 0, math.pi/2, math.pi]
        self.angle = angle_map[self.facing]
    
    def turn_right(self):
        """Turn 90 degrees right"""
        self.facing = (self.facing + 1) % 4
        angle_map = [-math.pi/2, 0, math.pi/2, math.pi]
        self.angle = angle_map[self.facing]
