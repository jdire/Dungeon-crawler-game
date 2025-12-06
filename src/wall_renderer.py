"""3D wall panel renderer - renders walls as flat 3D planes"""

import math
import pygame
from src.constants import *

class WallRenderer:
    """Render walls as 3D panels facing inward"""
    
    def __init__(self, dungeon_map):
        """Initialize wall renderer"""
        self.dungeon_map = dungeon_map
        self.load_wall_texture()
        
    def load_wall_texture(self):
        """Load wall texture from file or generate one"""
        import os
        
        texture_paths = ['textures/wall.png', 'textures/wall.jpg', 'textures/wall.jpeg', 'textures/wall.bmp']
        for path in texture_paths:
            if os.path.exists(path):
                try:
                    texture = pygame.image.load(path)
                    if texture.get_width() != 64 or texture.get_height() != 64:
                        texture = pygame.transform.scale(texture, (64, 64))
                    print(f"Loaded wall texture from {path}")
                    self.wall_texture = texture
                    return
                except Exception as e:
                    print(f"Failed to load texture from {path}: {e}")
        
        print("No wall texture found, using procedurally generated texture")
        self.wall_texture = self.create_wall_texture()
    
    def create_wall_texture(self):
        """Create a simple stone texture"""
        import random
        texture = pygame.Surface((64, 64))
        random.seed(12345)
        for x in range(64):
            for y in range(64):
                base = 120
                variation = random.randint(-20, 20)
                shade = base + variation
                if y % 16 == 0 or y % 16 == 1:
                    shade = int(shade * 0.6)
                if x % 8 == 0:
                    shade = int(shade * 0.6)
                shade = max(60, min(180, shade))
                texture.set_at((x, y), (shade, shade, shade))
        return texture
    
    def project_3d_to_2d(self, x, y, z, player):
        """Project 3D world coordinate to 2D screen coordinate"""
        dx = x - player.x
        dy = y - player.y
        
        forward_x = math.cos(player.angle)
        forward_y = math.sin(player.angle)
        right_x = -forward_y
        right_y = forward_x
        
        cam_x = dx * right_x + dy * right_y
        cam_y = dx * forward_x + dy * forward_y
        cam_z = z - TILE_SIZE / 2  # Center Z at player eye height (middle of wall)
        
        if cam_y < 5:
            return None
        
        focal_length = SCREEN_WIDTH * 0.5  # Wider FOV
        screen_x = int(SCREEN_WIDTH / 2 + (cam_x * focal_length) / cam_y)
        # Horizon at screen center, not 0.55
        screen_y = int(SCREEN_HEIGHT / 2 - (cam_z * focal_length) / cam_y)
        screen_scale = focal_length / cam_y
        
        return (screen_x, screen_y, screen_scale)
    def render(self, screen, player):
        """Render all wall panels"""
        # Draw ceiling (darker)
        screen.fill((40, 40, 40), (0, 0, SCREEN_WIDTH, SCREEN_HEIGHT // 2))
        # Draw floor (lighter) - fully opaque
        pygame.draw.rect(screen, (70, 70, 70), (0, SCREEN_HEIGHT // 2, SCREEN_WIDTH, SCREEN_HEIGHT // 2))
        
        wall_panels = []
        # Single standard wall height - one panel per wall face
        wall_height = TILE_SIZE
        
        # For each wall cell, create visible faces only
        for gy in range(self.dungeon_map.height):
            for gx in range(self.dungeon_map.width):
                if not self.dungeon_map.is_wall_grid(gx, gy):
                    continue
                
                # Create one panel per visible face (standard height)
                x1 = gx * TILE_SIZE
                x2 = (gx + 1) * TILE_SIZE
                y1 = gy * TILE_SIZE
                y2 = (gy + 1) * TILE_SIZE
                z1 = 0  # floor level
                z2 = wall_height  # ceiling level (single height)
                
                # Only create faces that border empty space (visible faces)
                # North face (facing south, at y1)
                if gy == 0 or not self.dungeon_map.is_wall_grid(gx, gy - 1):
                    wall_panels.append({
                        'corners': [(x1, y1, z1), (x2, y1, z1), (x2, y1, z2), (x1, y1, z2)],
                        'center': ((x1+x2)/2, y1, z2/2),
                        'face': 'N',
                        'grid': (gx, gy)
                    })
                
                # South face (facing north, at y2)
                if gy == self.dungeon_map.height - 1 or not self.dungeon_map.is_wall_grid(gx, gy + 1):
                    wall_panels.append({
                        'corners': [(x1, y2, z1), (x2, y2, z1), (x2, y2, z2), (x1, y2, z2)],
                        'center': ((x1+x2)/2, y2, z2/2),
                        'face': 'S',
                        'grid': (gx, gy)
                    })
                
                # West face (facing east, at x1)
                if gx == 0 or not self.dungeon_map.is_wall_grid(gx - 1, gy):
                    wall_panels.append({
                        'corners': [(x1, y1, z1), (x1, y2, z1), (x1, y2, z2), (x1, y1, z2)],
                        'center': (x1, (y1+y2)/2, z2/2),
                        'face': 'W',
                        'grid': (gx, gy)
                    })
                
                # East face (facing west, at x2)
                if gx == self.dungeon_map.width - 1 or not self.dungeon_map.is_wall_grid(gx + 1, gy):
                    wall_panels.append({
                        'corners': [(x2, y1, z1), (x2, y2, z1), (x2, y2, z2), (x2, y1, z2)],
                        'center': (x2, (y1+y2)/2, z2/2),
                        'face': 'E',
                        'grid': (gx, gy)
                    })
                
                # Top face (ceiling) - only visible if we look up, which we don't in this game
                # Bottom face (floor) - only visible if we look down, which we don't in this game
        
        # Calculate camera space coordinates for all panels
        for panel in wall_panels:
            cx, cy, cz = panel['center']
            dx = cx - player.x
            dy = cy - player.y
            
            forward_x = math.cos(player.angle)
            forward_y = math.sin(player.angle)
            right_x = -forward_y
            right_y = forward_x
            
            panel['cam_depth'] = dx * forward_x + dy * forward_y
            panel['cam_right'] = dx * right_x + dy * right_y
        
        # Filter visible panels
        visible_panels = []
        for panel in wall_panels:
            if panel['cam_depth'] < 5:
                continue
            # Tighter FOV - only show what's actually in front
            fov_ratio = abs(panel['cam_right']) / max(panel['cam_depth'], 1)
            if fov_ratio > 1.2:  # Much tighter - only ~60 degree FOV
                continue
            visible_panels.append(panel)
        
        visible_panels.sort(key=lambda p: p['cam_depth'], reverse=True)
        
        for panel in visible_panels:
            self.render_panel(screen, panel, player)
    
    def render_panel(self, screen, panel, player):
        """Render a single wall panel - these are solid quads from floor to ceiling"""
        projected = []
        for corner in panel['corners']:
            proj = self.project_3d_to_2d(corner[0], corner[1], corner[2], player)
            if proj is None:
                return
            projected.append(proj)
        
        if len(projected) != 4:
            return
        
        points = [(p[0], p[1]) for p in projected]
        
        try:
            # Draw the solid wall face
            pygame.draw.polygon(screen, (100, 100, 100), points, 0)
            
            # Calculate bounding box for texture
            min_x = max(0, int(min(p[0] for p in points)))
            max_x = min(SCREEN_WIDTH, int(max(p[0] for p in points)))
            min_y = max(0, int(min(p[1] for p in points)))
            max_y = min(SCREEN_HEIGHT, int(max(p[1] for p in points)))
            
            # Calculate average scale for texture sizing
            avg_scale = sum(p[2] for p in projected) / 4
            tex_size = max(16, int(64 * avg_scale))
            
            # Tile texture over the wall face
            if tex_size > 0 and max_x > min_x and max_y > min_y:
                scaled_texture = pygame.transform.scale(self.wall_texture, (tex_size, tex_size))
                for y in range(min_y, max_y, tex_size):
                    for x in range(min_x, max_x, tex_size):
                        # Only draw texture within the polygon bounds
                        if min_x <= x < max_x and min_y <= y < max_y:
                            screen.blit(scaled_texture, (x, y))
            
            # Draw edge outline for depth perception
            pygame.draw.polygon(screen, (40, 40, 40), points, 2)
            
        except Exception as e:
            pass  # Skip problematic panels
            pass
