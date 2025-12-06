"""Classic grid-based dungeon renderer (Eye of the Beholder style)"""

import pygame
import math
from src.constants import *

class ClassicRenderer:
    """Renders dungeon in classic first-person grid style"""
    
    def __init__(self, dungeon_map):
        self.dungeon_map = dungeon_map
        self.load_textures()
        
        # Define view dimensions (centered viewport for 3D view)
        self.view_width = SCREEN_WIDTH
        self.view_height = SCREEN_HEIGHT
        self.center_x = self.view_width // 2
        self.center_y = self.view_height // 2
        
    def load_textures(self):
        """Load or generate wall textures"""
        import os
        
        # Try to load wall texture
        texture_paths = ['textures/wall.png', 'textures/wall.jpg']
        self.wall_texture = None
        
        for path in texture_paths:
            if os.path.exists(path):
                try:
                    self.wall_texture = pygame.image.load(path)
                    print(f"Loaded wall texture from {path}")
                    break
                except Exception as e:
                    print(f"Failed to load {path}: {e}")
        
        # Generate procedural texture if none loaded
        if self.wall_texture is None:
            self.wall_texture = pygame.Surface((64, 64))
            self.wall_texture.fill((120, 100, 80))
            # Add some stone pattern
            for i in range(20):
                x = (i * 13) % 64
                y = (i * 17) % 64
                pygame.draw.rect(self.wall_texture, (100, 85, 70), (x, y, 8, 8))
    
    def check_wall(self, gx, gy):
        """Check if there's a wall at grid position"""
        if gx < 0 or gy < 0 or gx >= self.dungeon_map.width or gy >= self.dungeon_map.height:
            return True
        return self.dungeon_map.is_wall_grid(gx, gy)
    
    def render(self, screen, player):
        """Render the dungeon view"""
        # Draw ceiling (dark gray/blue)
        pygame.draw.rect(screen, (30, 30, 40), (0, 0, self.view_width, self.center_y))
        
        # Draw floor (brown/gray)
        pygame.draw.rect(screen, (60, 50, 40), (0, self.center_y, self.view_width, self.center_y))
        
        # Get player grid position and facing
        px, py = player.grid_x, player.grid_y
        facing = player.facing  # 0=North, 1=East, 2=South, 3=West
        
        # Direction vectors based on facing
        forward_dirs = [(0, -1), (1, 0), (0, 1), (-1, 0)]  # N, E, S, W
        right_dirs = [(1, 0), (0, 1), (-1, 0), (0, -1)]    # Right is 90° clockwise
        
        fx, fy = forward_dirs[facing]
        rx, ry = right_dirs[facing]
        
        # Debug output once
        if not hasattr(self, '_debug'):
            self._debug = True
            print(f"\n=== Classic Renderer Debug ===")
            print(f"Player: ({px},{py}), Facing: {facing}")
            print(f"Forward: ({fx},{fy}), Right: ({rx},{ry})")
        
        # Check walls at each distance and build the view
        # In classic dungeon crawlers, a solid wall at distance N blocks everything at N+1, N+2, etc.
        
        # Check distance 1 first - this is the most important
        walls_at_1 = []
        for offset in [-1, 0, 1]:
            gx = px + fx * 1 + rx * offset
            gy = py + fy * 1 + ry * offset
            if self.check_wall(gx, gy):
                walls_at_1.append(offset)
        
        # If there's a center wall at distance 1, we ONLY draw that (blocks everything behind)
        if 0 in walls_at_1:
            self.draw_wall_at_distance(screen, 1, 0)
            # Also draw side walls at distance 1 if they exist
            if -1 in walls_at_1:
                self.draw_wall_at_distance(screen, 1, -1)
            if 1 in walls_at_1:
                self.draw_wall_at_distance(screen, 1, 1)
        else:
            # No center wall at distance 1, so we can see distance 2 and 3
            
            # Check distance 2
            walls_at_2 = []
            for offset in [-1, 0, 1]:
                gx = px + fx * 2 + rx * offset
                gy = py + fy * 2 + ry * offset
                if self.check_wall(gx, gy):
                    walls_at_2.append(offset)
            
            # If there's a center wall at distance 2, draw it and check distance 3 is blocked
            if 0 in walls_at_2:
                self.draw_wall_at_distance(screen, 2, 0)
                if -1 in walls_at_2:
                    self.draw_wall_at_distance(screen, 2, -1)
                if 1 in walls_at_2:
                    self.draw_wall_at_distance(screen, 2, 1)
            else:
                # No center wall at distance 2, check distance 3
                for offset in [-1, 0, 1]:
                    gx = px + fx * 3 + rx * offset
                    gy = py + fy * 3 + ry * offset
                    if self.check_wall(gx, gy):
                        self.draw_wall_at_distance(screen, 3, offset)
                
                # Also draw distance 2 side walls if they exist
                if -1 in walls_at_2:
                    self.draw_wall_at_distance(screen, 2, -1)
                if 1 in walls_at_2:
                    self.draw_wall_at_distance(screen, 2, 1)
            
            # Draw distance 1 side walls
            if -1 in walls_at_1:
                self.draw_wall_at_distance(screen, 1, -1)
            if 1 in walls_at_1:
                self.draw_wall_at_distance(screen, 1, 1)
        
        # Always check immediate side walls (distance 0)
        gx, gy = px + rx, py + ry
        if self.check_wall(gx, gy):
            self.draw_side_wall(screen, 'left')
        
        gx, gy = px - rx, py - ry
        if self.check_wall(gx, gy):
            self.draw_side_wall(screen, 'right')
    
    def draw_wall_at_distance(self, screen, distance, offset):
        """Draw a wall at specified distance and offset (-1=left, 0=center, 1=right)"""
        # Define wall sizes based on distance (classic perspective)
        # These are tuned to look like Eye of the Beholder
        
        if distance == 3:
            # Far walls (small, centered)
            if offset == 0:  # Center
                x, y, w, h = self.center_x - 80, self.center_y - 60, 160, 120
            elif offset == -1:  # Left
                x, y, w, h = self.center_x - 160, self.center_y - 60, 80, 120
            else:  # Right
                x, y, w, h = self.center_x + 80, self.center_y - 60, 80, 120
            shade = 0.3
            
        elif distance == 2:
            # Medium distance
            if offset == 0:  # Center
                x, y, w, h = self.center_x - 150, self.center_y - 100, 300, 200
            elif offset == -1:  # Left
                x, y, w, h = self.center_x - 300, self.center_y - 100, 150, 200
            else:  # Right
                x, y, w, h = self.center_x + 150, self.center_y - 100, 150, 200
            shade = 0.5
            
        elif distance == 1:
            # Close distance
            if offset == 0:  # Center
                x, y, w, h = self.center_x - 250, self.center_y - 175, 500, 350
            elif offset == -1:  # Left
                x, y, w, h = self.center_x - 500, self.center_y - 175, 250, 350
            else:  # Right
                x, y, w, h = self.center_x + 250, self.center_y - 175, 250, 350
            shade = 0.7
        else:
            return
        
        self.draw_textured_wall(screen, x, y, w, h, shade)
    
    def draw_side_wall(self, screen, side):
        """Draw immediate side walls (distance 0)"""
        # These are the walls immediately beside the player
        if side == 'left':
            x, y, w, h = 0, self.center_y - 250, 150, 500
        else:  # right
            x, y, w, h = self.view_width - 150, self.center_y - 250, 150, 500
        
        self.draw_textured_wall(screen, x, y, w, h, shade=0.8)
    
    def draw_textured_wall(self, screen, x, y, w, h, shade=1.0):
        """Draw a textured wall rectangle with shading"""
        if w <= 0 or h <= 0:
            return
        
        # Scale texture to wall size
        scaled_tex = pygame.transform.scale(self.wall_texture, (int(w), int(h)))
        
        # Apply distance shading
        if shade < 1.0:
            dark = pygame.Surface((int(w), int(h)))
            dark.fill((0, 0, 0))
            dark.set_alpha(int(255 * (1.0 - shade)))
            scaled_tex.blit(dark, (0, 0))
        
        screen.blit(scaled_tex, (int(x), int(y)))
        
        # Draw border for definition
        pygame.draw.rect(screen, (20, 20, 20), (int(x), int(y), int(w), int(h)), 2)
