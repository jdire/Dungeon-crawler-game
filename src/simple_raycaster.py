"""Dead simple raycaster - just render what's in front of the player"""

import pygame
import math
from src.constants import *

class SimpleRaycaster:
    """Ultra-simple raycaster"""
    
    def __init__(self, dungeon_map):
        self.dungeon_map = dungeon_map
        self.load_texture()
        
    def load_texture(self):
        """Load wall texture"""
        import os
        if os.path.exists('textures/wall.png'):
            self.wall_tex = pygame.image.load('textures/wall.png')
            print("Loaded wall texture")
        else:
            # Solid gray texture
            self.wall_tex = pygame.Surface((64, 64))
            self.wall_tex.fill((100, 100, 100))
    
    def render(self, screen, player):
        """Render first-person view"""
        # Draw solid ceiling - opaque
        pygame.draw.rect(screen, (40, 40, 50), (0, 0, SCREEN_WIDTH, SCREEN_HEIGHT // 2))
        
        # Draw solid floor - opaque
        pygame.draw.rect(screen, (70, 60, 50), (0, SCREEN_HEIGHT // 2, SCREEN_WIDTH, SCREEN_HEIGHT // 2))
        
        # Cast rays
        num_rays = SCREEN_WIDTH
        fov = math.pi / 3  # 60 degrees
        
        for x in range(num_rays):
            # Calculate ray angle
            camera_x = 2 * x / num_rays - 1
            ray_angle = player.angle + math.atan(camera_x * math.tan(fov / 2))
            
            ray_dx = math.cos(ray_angle)
            ray_dy = math.sin(ray_angle)
            
            # Cast ray until hit wall (step in world units)
            step_size = 1.0  # world pixels per step
            distance = 0
            hit_wall = False
            max_distance = 1000  # world pixels
            
            while not hit_wall and distance < max_distance:
                distance += step_size
                
                check_x = player.x + ray_dx * distance
                check_y = player.y + ray_dy * distance
                
                grid_x = int(check_x / TILE_SIZE)
                grid_y = int(check_y / TILE_SIZE)
                
                # Check if hit wall
                if self.is_wall(grid_x, grid_y):
                    hit_wall = True
            
            if hit_wall:
                # Calculate wall height based on perpendicular distance
                perp_distance = distance * math.cos(ray_angle - player.angle)
                wall_height = int(SCREEN_HEIGHT * TILE_SIZE / (perp_distance + 1))
                wall_height = min(wall_height, SCREEN_HEIGHT * 2)
                
                # Draw wall stripe - completely opaque
                wall_top = SCREEN_HEIGHT // 2 - wall_height // 2
                wall_bottom = SCREEN_HEIGHT // 2 + wall_height // 2
                
                # Get wall color with distance shading
                base_color = 120
                shade = max(0.2, 1 - distance / max_distance)
                color_value = int(base_color * shade)
                color = (color_value, color_value, color_value)
                
                # Draw solid opaque wall stripe
                pygame.draw.line(screen, color, (x, wall_top), (x, wall_bottom))
    
    def is_wall(self, gx, gy):
        """Check if grid position is a wall"""
        if gx < 0 or gy < 0 or gx >= self.dungeon_map.width or gy >= self.dungeon_map.height:
            return True
        return self.dungeon_map.grid[gy][gx] == 1
