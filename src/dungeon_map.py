"""Dungeon map class"""

from src.constants import *

class DungeonMap:
    """Grid-based dungeon map"""
    
    def __init__(self):
        """Initialize dungeon with a simple test level"""
        # 1 = wall, 0 = empty
        # Simple corridor layout for testing
        self.grid = [
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 0, 0, 0, 1, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 1, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 1, 0, 0, 0, 0, 1],
            [1, 1, 1, 0, 1, 0, 1, 1, 1, 1],
            [1, 0, 0, 0, 1, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 1, 0, 0, 0, 0, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        ]
        
        self.width = len(self.grid[0])
        self.height = len(self.grid)
    
    def is_wall(self, x, y):
        """Check if position is a wall"""
        # Convert world coordinates to grid coordinates
        grid_x = int(x / TILE_SIZE)
        grid_y = int(y / TILE_SIZE)
        
        # Check bounds
        if grid_x < 0 or grid_x >= self.width or grid_y < 0 or grid_y >= self.height:
            return True
        
        return self.grid[grid_y][grid_x] == WALL
    
    def get_tile(self, x, y):
        """Get tile value at grid position"""
        if x < 0 or x >= self.width or y < 0 or y >= self.height:
            return WALL
        return self.grid[y][x]
    
    def is_wall_grid(self, grid_x, grid_y):
        """Check if grid position is a wall"""
        if grid_x < 0 or grid_x >= self.width or grid_y < 0 or grid_y >= self.height:
            return True
        return self.grid[grid_y][grid_x] == WALL
