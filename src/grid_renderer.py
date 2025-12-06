"""Simple grid-based first-person dungeon renderer"""

import pygame
from src.constants import *

class GridRenderer:
    """Renders dungeon in simple grid-based first-person view"""
    
    def __init__(self, dungeon_map):
        self.dungeon_map = dungeon_map
        self.load_texture()
        
    def load_texture(self):
        """Load wall texture"""
        import os
        if os.path.exists('textures/wall.png'):
            self.wall_tex = pygame.image.load('textures/wall.png')
        else:
            # Generate simple texture
            self.wall_tex = pygame.Surface((64, 64))
            self.wall_tex.fill((100, 90, 80))
    
    def render(self, screen, player):
        """Render the first-person view"""
        # Background
        screen.fill((30, 30, 40))  # Ceiling
        pygame.draw.rect(screen, (50, 45, 40), (0, SCREEN_HEIGHT // 2, SCREEN_WIDTH, SCREEN_HEIGHT // 2))  # Floor
        
        px, py = player.grid_x, player.grid_y
        facing = player.facing
        
        # Get direction vectors
        # North=0:(0,-1), East=1:(1,0), South=2:(0,1), West=3:(-1,0)
        fwd = [(0,-1), (1,0), (0,1), (-1,0)][facing]
        right = [(1,0), (0,1), (-1,0), (0,-1)][facing]
        
        # Define what we check: (forward_steps, right_steps, screen_rect, distance_label)
        # We check tiles and draw walls on screen
        view_checks = [
            # Distance 1 (closest, largest walls)
            (1, -1, (50, 150, 250, 350), 1),      # Left
            (1,  0, (300, 150, 500, 350), 1),     # Center  
            (1,  1, (800, 150, 250, 350), 1),     # Right
            
            # Distance 2 (medium)
            (2, -1, (200, 225, 200, 250), 2),     # Left
            (2,  0, (400, 225, 300, 250), 2),     # Center
            (2,  1, (700, 225, 200, 250), 2),     # Right
            
            # Distance 3 (far, small)
            (3, -1, (300, 300, 100, 150), 3),     # Left
            (3,  0, (400, 300, 300, 150), 3),     # Center
            (3,  1, (700, 300, 100, 150), 3),     # Right
        ]
        
        # Track if we've drawn a blocking wall
        blocked_at_dist = {}
        
        # Check each position from far to near
        for fwd_steps, right_steps, rect, dist in reversed(view_checks):
            # Skip if blocked by closer wall
            if dist in blocked_at_dist:
                continue
            
            # Calculate grid position
            check_x = px + fwd[0] * fwd_steps + right[0] * right_steps
            check_y = py + fwd[1] * fwd_steps + right[1] * right_steps
            
            # Check if wall
            if self.is_wall(check_x, check_y):
                # Draw wall
                self.draw_wall(screen, rect, dist)
                
                # If this is a center wall, block all farther distances
                if right_steps == 0:
                    for d in range(dist + 1, 10):
                        blocked_at_dist[d] = True
    
    def is_wall(self, gx, gy):
        """Check if position has a wall"""
        if gx < 0 or gy < 0 or gx >= self.dungeon_map.width or gy >= self.dungeon_map.height:
            return True
        return self.dungeon_map.grid[gy][gx] == 1
    
    def draw_wall(self, screen, rect, distance):
        """Draw a wall rectangle"""
        x, y, w, h = rect
        
        # Scale and draw texture
        tex = pygame.transform.scale(self.wall_tex, (w, h))
        
        # Apply distance shading
        shade = [0.3, 0.5, 0.7, 0.9][min(distance, 3)]
        if shade < 1.0:
            dark = pygame.Surface((w, h))
            dark.fill((0, 0, 0))
            dark.set_alpha(int(255 * (1 - shade)))
            tex.blit(dark, (0, 0))
        
        screen.blit(tex, (x, y))
        pygame.draw.rect(screen, (20, 20, 20), (x, y, w, h), 2)
