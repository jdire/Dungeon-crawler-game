"""Raycasting engine for 3D rendering"""

import math
import pygame
from src.constants import *

class Raycaster:
    """Cast rays and render 3D view"""
    
    def __init__(self, dungeon_map):
        """Initialize raycaster with dungeon map"""
        self.dungeon_map = dungeon_map
        self.wall_heights = []  # Store wall heights for rendering
        
    def cast_rays(self, player):
        """Cast rays from player position"""
        self.wall_heights = []
        
        # Start angle for leftmost ray
        ray_angle = player.angle - HALF_FOV
        
        for ray in range(NUM_RAYS):
            # Cast single ray
            depth = 0
            hit_wall = False
            
            # Ray direction
            ray_x = math.cos(ray_angle)
            ray_y = math.sin(ray_angle)
            
            # Step along ray until hit wall or max depth
            while not hit_wall and depth < MAX_DEPTH:
                depth += 0.1
                
                # Calculate test point
                test_x = player.x + ray_x * depth * TILE_SIZE
                test_y = player.y + ray_y * depth * TILE_SIZE
                
                # Check if hit wall
                if self.dungeon_map.is_wall(test_x, test_y):
                    hit_wall = True
                    
                    # Fix fish-eye effect by using perpendicular distance
                    depth *= math.cos(player.angle - ray_angle)
                    
                    # Calculate wall height based on distance
                    if depth > 0:
                        wall_height = (TILE_SIZE * SCREEN_HEIGHT) / (depth * TILE_SIZE)
                    else:
                        wall_height = SCREEN_HEIGHT
                    
                    self.wall_heights.append((depth, wall_height))
            
            if not hit_wall:
                self.wall_heights.append((MAX_DEPTH, 0))
            
            ray_angle += DELTA_ANGLE
    
    def render(self, screen):
        """Render 3D view to screen"""
        # Draw ceiling (dark gray)
        screen.fill(DARK_GRAY, (0, 0, SCREEN_WIDTH, SCREEN_HEIGHT // 2))
        
        # Draw floor (darker gray)
        screen.fill(BLACK, (0, SCREEN_HEIGHT // 2, SCREEN_WIDTH, SCREEN_HEIGHT // 2))
        
        # Draw walls
        wall_width = SCREEN_WIDTH / NUM_RAYS
        
        for i, (depth, wall_height) in enumerate(self.wall_heights):
            if wall_height > 0:
                # Calculate shading based on distance
                shade = max(50, 255 - int(depth * 12))
                wall_color = (shade, shade, shade)
                
                # Calculate wall position
                wall_top = (SCREEN_HEIGHT - wall_height) / 2
                wall_rect = pygame.Rect(
                    i * wall_width,
                    wall_top,
                    wall_width + 1,  # +1 to avoid gaps
                    wall_height
                )
                
                pygame.draw.rect(screen, wall_color, wall_rect)
