"""Dead simple raycaster - just render what's in front of the player"""

import pygame
import math
from src.constants import *

class SimpleRaycaster:
    """Ultra-simple raycaster"""
    
    def __init__(self, dungeon_map, enemy_encounters=None):
        self.dungeon_map = dungeon_map
        self.enemy_encounters = enemy_encounters
        self.load_texture()
        
    def load_texture(self):
        """Load wall and enemy textures"""
        import os
        if os.path.exists('textures/wall.png'):
            self.wall_tex = pygame.image.load('textures/wall.png')
            print("Loaded wall texture")
        else:
            # Solid gray texture
            self.wall_tex = pygame.Surface((64, 64))
            self.wall_tex.fill((100, 100, 100))
        
        # Load enemy sprite
        if os.path.exists('textures/dummy.png'):
            self.enemy_sprite = pygame.image.load('textures/dummy.png')
            print("Loaded dummy sprite")
        else:
            # Create a simple red square sprite
            self.enemy_sprite = pygame.Surface((64, 64), pygame.SRCALPHA)
            pygame.draw.circle(self.enemy_sprite, (200, 50, 50), (32, 32), 28)
            pygame.draw.circle(self.enemy_sprite, (150, 30, 30), (32, 32), 20)
            print("Using default dummy sprite")
    
    def render(self, screen, player):
        """Render first-person view"""
        # Draw solid ceiling - opaque
        pygame.draw.rect(screen, (40, 40, 50), (0, 0, SCREEN_WIDTH, SCREEN_HEIGHT // 2))
        
        # Draw solid floor - opaque
        pygame.draw.rect(screen, (70, 60, 50), (0, SCREEN_HEIGHT // 2, SCREEN_WIDTH, SCREEN_HEIGHT // 2))
        
        # Store wall depths for sprite rendering
        z_buffer = [float('inf')] * SCREEN_WIDTH
        
        # Cast rays for walls
        num_rays = SCREEN_WIDTH
        fov = math.pi / 3  # 60 degrees
        
        for x in range(num_rays):
            # Calculate ray angle
            camera_x = 2 * x / num_rays - 1
            ray_angle = player.angle + math.atan(camera_x * math.tan(fov / 2))
            
            ray_dx = math.cos(ray_angle)
            ray_dy = math.sin(ray_angle)
            
            # Cast ray until hit wall
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
                z_buffer[x] = perp_distance  # Store for sprite rendering
                
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
        
        # Render sprites (enemies) after walls
        self.render_sprites(screen, player, z_buffer, fov)
    
    def render_sprites(self, screen, player, z_buffer, fov):
        """Render enemy sprites using billboarding"""
        if not self.enemy_encounters:
            return
        
        # Get all enemies and calculate their screen positions
        sprites_to_draw = []
        
        for (grid_x, grid_y), enemy in self.enemy_encounters.encounters.items():
            if not enemy.is_alive:
                continue
            
            # Enemy is at center of grid tile
            sprite_x = grid_x * TILE_SIZE + TILE_SIZE // 2
            sprite_y = grid_y * TILE_SIZE + TILE_SIZE // 2
            
            # Calculate relative position to player
            dx = sprite_x - player.x
            dy = sprite_y - player.y
            
            # Calculate distance
            distance = math.sqrt(dx * dx + dy * dy)
            
            # Calculate angle relative to player
            sprite_angle = math.atan2(dy, dx)
            angle_diff = sprite_angle - player.angle
            
            # Normalize angle to [-pi, pi]
            while angle_diff > math.pi:
                angle_diff -= 2 * math.pi
            while angle_diff < -math.pi:
                angle_diff += 2 * math.pi
            
            # Check if sprite is in front of player (within FOV)
            if abs(angle_diff) > fov / 2 + 0.5:  # Add small margin
                continue
            
            # Calculate screen X position
            # Convert angle difference to screen space
            screen_x = int(SCREEN_WIDTH / 2 * (1 + angle_diff / (fov / 2)))
            
            sprites_to_draw.append({
                'distance': distance,
                'screen_x': screen_x,
                'enemy': enemy
            })
        
        # Sort sprites by distance (far to near)
        sprites_to_draw.sort(key=lambda s: s['distance'], reverse=True)
        
        # Draw sprites
        for sprite in sprites_to_draw:
            distance = sprite['distance']
            screen_x = sprite['screen_x']
            
            # Calculate sprite size based on distance
            sprite_height = int(SCREEN_HEIGHT * TILE_SIZE / (distance + 1))
            sprite_height = min(sprite_height, SCREEN_HEIGHT * 2)
            sprite_width = sprite_height  # Keep square
            
            # Calculate screen position
            sprite_top = SCREEN_HEIGHT // 2 - sprite_height // 2
            sprite_left = screen_x - sprite_width // 2
            
            # Check if sprite is off screen
            if sprite_left + sprite_width < 0 or sprite_left >= SCREEN_WIDTH:
                continue
            
            # Scale sprite
            scaled_sprite = pygame.transform.scale(self.enemy_sprite, (sprite_width, sprite_height))
            
            # Apply distance shading
            shade = max(0.3, 1 - distance / 1000)
            if shade < 1.0:
                dark = pygame.Surface((sprite_width, sprite_height), pygame.SRCALPHA)
                dark.fill((0, 0, 0, int(255 * (1.0 - shade))))
                scaled_sprite.blit(dark, (0, 0))
            
            # Draw sprite column by column, checking z-buffer
            for sx in range(sprite_width):
                screen_col = sprite_left + sx
                if 0 <= screen_col < SCREEN_WIDTH:
                    # Check if sprite is closer than wall at this column
                    if distance < z_buffer[screen_col]:
                        # Blit one column of the sprite
                        col_rect = pygame.Rect(sx, 0, 1, sprite_height)
                        screen.blit(scaled_sprite, (screen_col, sprite_top), col_rect)
    
    def is_wall(self, gx, gy):
        """Check if grid position is a wall"""
        if gx < 0 or gy < 0 or gx >= self.dungeon_map.width or gy >= self.dungeon_map.height:
            return True
        return self.dungeon_map.grid[gy][gx] == 1
