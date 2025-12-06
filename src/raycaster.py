"""Raycasting engine for 3D rendering"""

import math
import pygame
import random
from src.constants import *

class Raycaster:
    """Cast rays and render 3D view"""
    
    def __init__(self, dungeon_map):
        """Initialize raycaster with dungeon map"""
        self.dungeon_map = dungeon_map
        self.wall_heights = []  # Store wall heights for rendering
        
        # Try to load wall texture, fallback to generated texture
        self.wall_texture = self.load_wall_texture()
        
    def load_wall_texture(self):
        """Load wall texture from file or generate one"""
        import os
        
        # Try to load from textures folder
        texture_paths = [
            'textures/wall.png',
            'textures/wall.jpg',
            'textures/wall.jpeg',
            'textures/wall.bmp'
        ]
        
        for path in texture_paths:
            if os.path.exists(path):
                try:
                    texture = pygame.image.load(path)
                    # Scale to desired size if needed
                    if texture.get_width() != 64 or texture.get_height() != 256:
                        texture = pygame.transform.scale(texture, (64, 256))
                    print(f"Loaded wall texture from {path}")
                    return texture
                except Exception as e:
                    print(f"Failed to load texture from {path}: {e}")
        
        # Fallback to generated texture
        print("No wall texture found, using procedurally generated texture")
        return self.create_wall_texture()
        
    def create_wall_texture(self):
        """Create a single vertical strip of wall texture to be stretched"""
        texture_width = 64
        texture_height = 256
        texture = pygame.Surface((texture_width, texture_height))
        
        # Base stone color
        random.seed(12345)
        for x in range(texture_width):
            for y in range(texture_height):
                # Random stone variation
                base = 120
                variation = random.randint(-20, 20)
                shade = base + variation
                
                # Add mortar lines
                if y % 32 == 0 or y % 32 == 1:  # Horizontal mortar
                    shade = int(shade * 0.6)
                if x % 8 == 0:  # Vertical mortar
                    shade = int(shade * 0.6)
                    
                shade = max(60, min(180, shade))
                texture.set_at((x, y), (shade, shade, shade))
        
        return texture
        
    def cast_rays(self, player):
        """Cast rays - simple algorithm"""
        self.wall_heights = []
        self.player = player
        
        ray_angle = player.angle - HALF_FOV
        
        for ray in range(NUM_RAYS):
            # Ray direction
            cos_a = math.cos(ray_angle)
            sin_a = math.sin(ray_angle)
            
            # Step along ray until we hit a wall
            for depth in range(0, int(MAX_DEPTH * TILE_SIZE), 1):
                x = player.x + cos_a * depth
                y = player.y + sin_a * depth
                
                # Get grid position
                map_x = int(x / TILE_SIZE)
                map_y = int(y / TILE_SIZE)
                
                # Check if we hit a wall
                if self.dungeon_map.is_wall_grid(map_x, map_y):
                    # Calculate texture X based on hit position
                    if abs(cos_a) > abs(sin_a):
                        # Hit vertical wall
                        texture_x = (y % TILE_SIZE) / TILE_SIZE
                    else:
                        # Hit horizontal wall
                        texture_x = (x % TILE_SIZE) / TILE_SIZE
                    
                    # Store: depth, texture_x, ray_angle
                    self.wall_heights.append((depth / TILE_SIZE, texture_x, ray_angle))
                    break
            else:
                # No wall hit
                self.wall_heights.append((MAX_DEPTH, 0, ray_angle))
            
            ray_angle += DELTA_ANGLE
    
    def render(self, screen):
        """Render the 3D view - simple approach"""
        horizon = int(SCREEN_HEIGHT * 0.55)
        ray_width = SCREEN_WIDTH / NUM_RAYS
        
        # Draw ceiling
        screen.fill((50, 50, 50), (0, 0, SCREEN_WIDTH, horizon))
        # Draw floor
        screen.fill((80, 80, 80), (0, horizon, SCREEN_WIDTH, SCREEN_HEIGHT - horizon))
        
        # Draw each ray
        for i, ray_data in enumerate(self.wall_heights):
            depth, texture_x, ray_angle = ray_data
            
            if depth >= MAX_DEPTH:
                continue
            
            # Remove fisheye effect
            corrected_depth = depth * math.cos(ray_angle - self.player.angle)
            
            # Calculate wall height
            if corrected_depth > 0:
                wall_height = (TILE_SIZE * SCREEN_HEIGHT) / (corrected_depth * TILE_SIZE)
                wall_height = min(wall_height, SCREEN_HEIGHT * 2)
            else:
                wall_height = SCREEN_HEIGHT
            
            # Calculate wall position
            wall_top = int(horizon - wall_height / 2)
            wall_bottom = int(horizon + wall_height / 2)
            
            if wall_bottom <= wall_top:
                continue
            
            # Get texture column
            tex_x = int(texture_x * 63) % 64
            strip_height = wall_bottom - wall_top
            
            # Create and sample texture
            strip = pygame.Surface((1, strip_height))
            for y in range(strip_height):
                tex_y = int((y / strip_height) * 255) % 256
                color = self.wall_texture.get_at((tex_x, tex_y))
                strip.set_at((0, y), color)
            
            # Scale and draw
            scaled = pygame.transform.scale(strip, (int(ray_width) + 1, strip_height))
            screen.blit(scaled, (i * ray_width, wall_top))
