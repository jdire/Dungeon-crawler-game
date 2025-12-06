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
            hit_x, hit_y = 0, 0
            
            while not hit_wall and distance < max_distance:
                distance += step_size
                
                check_x = player.x + ray_dx * distance
                check_y = player.y + ray_dy * distance
                
                grid_x = int(check_x / TILE_SIZE)
                grid_y = int(check_y / TILE_SIZE)
                
                # Check if hit wall
                if self.is_wall(grid_x, grid_y):
                    hit_wall = True
                    hit_x = check_x
                    hit_y = check_y
            
            if hit_wall:
                # Calculate wall height based on perpendicular distance
                perp_distance = distance * math.cos(ray_angle - player.angle)
                wall_height = int(SCREEN_HEIGHT * TILE_SIZE / (perp_distance + 1))
                wall_height = min(wall_height, SCREEN_HEIGHT * 2)
                
                # Draw wall stripe - completely opaque
                wall_top = SCREEN_HEIGHT // 2 - wall_height // 2
                wall_bottom = SCREEN_HEIGHT // 2 + wall_height // 2
                
                # Calculate texture coordinate
                # Determine if we hit a vertical or horizontal wall
                wall_x = hit_x % TILE_SIZE
                wall_y = hit_y % TILE_SIZE
                
                # Use the coordinate that's closer to an edge (more likely the hit surface)
                if min(wall_x, TILE_SIZE - wall_x) < min(wall_y, TILE_SIZE - wall_y):
                    # Hit vertical wall, use Y coordinate
                    tex_x = int((wall_y / TILE_SIZE) * 64) % 64
                else:
                    # Hit horizontal wall, use X coordinate
                    tex_x = int((wall_x / TILE_SIZE) * 64) % 64
                
                # Get the column from texture
                if tex_x >= 64:
                    tex_x = 63
                
                # Scale texture column to wall height
                tex_column = pygame.Surface((1, 64))
                tex_column.blit(self.wall_tex, (0, 0), (tex_x, 0, 1, 64))
                tex_column = pygame.transform.scale(tex_column, (1, wall_height))
                
                # Apply distance shading
                shade = max(0.3, 1 - distance / max_distance)
                if shade < 1.0:
                    dark = pygame.Surface((1, wall_height))
                    dark.fill((0, 0, 0))
                    dark.set_alpha(int(255 * (1.0 - shade)))
                    tex_column.blit(dark, (0, 0))
                
                # Draw the textured stripe
                screen.blit(tex_column, (x, wall_top))
    
    def is_wall(self, gx, gy):
        """Check if grid position is a wall"""
        if gx < 0 or gy < 0 or gx >= self.dungeon_map.width or gy >= self.dungeon_map.height:
            return True
        return self.dungeon_map.grid[gy][gx] == 1
